from flask import Blueprint, jsonify, request, render_template
import requests
import base64
from datetime import datetime

d3_bp = Blueprint('d3_bp', __name__)

# === Global Auth & API Configuration ===
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

API_URL_LIST_MAHASISWA = "https://api.upnvj.ac.id/data/list_mahasiswa"
API_URL_BIODATA_MAHASISWA = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'
API_URL_HISTORI_MAHASISWA = 'https://api.upnvj.ac.id/data/list_histori_mahasiswa'

# D3 Sistem Informasi Prodi ID
ID_PRODI_D3_SISFO = 6 

def get_basic_auth_header(USERNAME,PASSWORD):
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

COMMON_HEADERS = {
    "X-UPNVJ-API-KEY": API_SECRET,
    "Accept": 'application/json',
    "Authorization": get_basic_auth_header(USERNAME,PASSWORD),
    "User-Agent": "Thunder Client (https://www.thunderclient.com)"
}

def calculate_semester(angkatan_tahun_masuk):
    current_year = datetime.now().year
    current_month = datetime.now().month

    angkatan_tahun_masuk = int(angkatan_tahun_masuk)
    
    years_passed = current_year - angkatan_tahun_masuk

    current_semester_offset = 0
    if current_month >= 8: # August-December (Ganjil)
        current_semester_offset = 1
    elif current_month >= 2 and current_month <= 7: # February-July (Genap)
        current_semester_offset = 2

    calculated_semester = (current_year - angkatan_tahun_masuk) * 2 + current_semester_offset

    if calculated_semester == 0 and angkatan_tahun_masuk == current_year:
        return 1

    return calculated_semester

@d3_bp.route('/dekannilaid3')
def dekan_nilai_d3():
    return render_template('dekan_nilai_d3.html')

# D3 SISTEM INFORMASI STUDENT DETAILS (FOR DEKAN_NILAI_D3.HTML)
@d3_bp.route('/api/mahasiswa-d3', methods=['GET'])
def api_mahasiswa_d3():
    current_year = datetime.now().year
    angkatan_list = [str(year) for year in range(2018, current_year + 1)] 

    result_data = []

    for angkatan in angkatan_list:
        try:
            response = requests.post(
                API_URL_LIST_MAHASISWA,
                data={"angkatan": angkatan},
                headers=COMMON_HEADERS,
                timeout=30
            )
            response.raise_for_status()
            data = response.json().get("data", [])

            for mhs in data:
                if (
                    int(mhs.get("id_program_studi", -1)) == ID_PRODI_D3_SISFO and
                    mhs.get("status_mahasiswa_terakhir", "").strip().upper() == "AKTIF"
                ):
                    tahun_masuk = int(mhs.get("angkatan", angkatan))
                    semester = calculate_semester(tahun_masuk)

                    result_data.append({
                        "nim": mhs.get("nim"),
                        "nama": mhs.get("nama_mahasiswa"),
                        "angkatan": str(tahun_masuk),
                        "semester": semester,
                        "ipk": mhs.get("ipk", "-")
                    })
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for angkatan {angkatan}: {e}")
        except ValueError as e:
            print(f"Error parsing JSON for angkatan {angkatan}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred for angkatan {angkatan}: {e}")

    return jsonify(result_data)

# STUDENT DETAILS WITH GRAPH
@d3_bp.route('/detailnilaid3/<nim>')
def detail_mahasiswa(nim):
    mahasiswa_detail = {
        "nama": "-", "nim": nim, "semester": "-", "prodi": "-",
        "alamat": "-", "status_mhs": "-", "ipk": "-", "ipk_histori": []
    }
    
    try:
        # Fetch student biodata using API
        bio_resp = requests.post(API_URL_BIODATA_MAHASISWA, data={"nim": nim}, headers=COMMON_HEADERS, timeout=10)
        bio_resp.raise_for_status()
        bio_data = bio_resp.json().get("data", {})

        if bio_data:
            mahasiswa_detail["nama"] = bio_data.get("nama", "-")
            mahasiswa_detail["prodi"] = bio_data.get("nama_program_studi", "-")
            mahasiswa_detail["status_mhs"] = bio_data.get("status_mahasiswa_terakhir", "-")
            mahasiswa_detail["ipk"] = bio_data.get("ipk", "-")
            mahasiswa_detail["semester"] = bio_data.get("semester_mahasiswa", "-")
            
            angkatan = int(bio_data.get("angkatan", datetime.now().year))
            semester_now = calculate_semester(angkatan)
            
            # Format address from data
            alamat_parts = [
                bio_data.get("kelurahan", ""),
                bio_data.get("kecamatan", ""),
                bio_data.get("kotakab", ""),
                bio_data.get("propinsi", "")
            ]
            mahasiswa_detail["alamat"] = ", ".join(filter(None, alamat_parts)) if any(alamat_parts) else "-"

            # Fetch student academic history
            histori = []
            for semester_num in range(1, semester_now + 1):
                tahun_akademik_mulai = angkatan + ((semester_num - 1) // 2)
                periode_id_suffix = 1 if semester_num % 2 != 0 else 2
                id_periode = f"{tahun_akademik_mulai}{periode_id_suffix}"
                
                try:
                    hist_resp = requests.post(API_URL_HISTORI_MAHASISWA, data={"nim": nim, "id_periode": id_periode}, headers=COMMON_HEADERS, timeout=10)
                    hist_resp.raise_for_status()
                    hist_data_list = hist_resp.json().get("data", [])
                    
                    entry = next((item for item in hist_data_list if item.get("nim") == nim), {})
                    
                    if entry and entry.get("ipk") is not None:
                         histori.append({
                            "semester": f"Semester {semester_num}",
                            "ips": float(entry.get("ips", 0)),
                            "ipk": float(entry.get("ipk", 0))
                        })
                    else:
                        histori.append({
                            "semester": f"Semester {semester_num}",
                            "ips": 0.0,
                            "ipk": 0.0
                        })
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching histori for NIM {nim}, Periode {id_periode}: {e}")
                    histori.append({
                        "semester": f"Semester {semester_num}",
                        "ips": 0.0,
                        "ipk": 0.0
                    })
                except ValueError as e:
                    print(f"Error parsing histori JSON for NIM {nim}, Periode {id_periode}: {e}")
                    histori.append({
                        "semester": f"Semester {semester_num}",
                        "ips": 0.0,
                        "ipk": 0.0
                    })

            mahasiswa_detail["ipk_histori"] = histori

    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {str(e)}", 500
    except ValueError as e:
        return f"Error parsing JSON data: {str(e)}", 500
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

    return render_template("detail_nilai_d3.html", mahasiswa=mahasiswa_detail)