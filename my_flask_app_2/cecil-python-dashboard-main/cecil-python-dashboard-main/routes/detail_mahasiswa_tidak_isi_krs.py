from flask import Blueprint, jsonify, request
import requests
import base64
from datetime import datetime

detail_krs_bp = Blueprint('detail_krs_bp', __name__)

# === Konfigurasi Auth & API ===
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

API_URL_LIST_MAHASISWA = 'https://api.upnvj.ac.id/data/list_mahasiswa'
API_URL_BIODATA_MAHASISWA = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'

TAHUN_LIST_UMUM = ["2020", "2021", "2022", "2023", "2024"]

ID_PRODI_DIIKUTKAN = [3, 4, 6, 58] # ID Prodi yang ingin disertakan

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
    
    # Hitung jumlah tahun berlalu sejak angkatan masuk
    years_passed = current_year - angkatan_tahun_masuk

    # Sesuaikan berdasarkan bulan saat ini
    current_semester_offset = 0
    if current_month >= 8: # Agustus-Desember
        current_semester_offset = 1
    elif current_month >= 2 and current_month <= 7: # Februari-Juli
        current_semester_offset = 2

    calculated_semester = (current_year - angkatan_tahun_masuk) * 2 + current_semester_offset

    if calculated_semester == 0 and angkatan_tahun_masuk == current_year:
        return 1

    return calculated_semester


# DETAIL MAHASISWA BELUM ISI KRS
@detail_krs_bp.route('/api/mahasiswa-belum-isi-krs', methods=['GET'])
def get_mahasiswa_belum_isi_krs():
    result = []

    for tahun in TAHUN_LIST_UMUM:
        try:
            response = requests.post(API_URL_LIST_MAHASISWA, data={"angkatan": tahun}, headers=COMMON_HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json().get("data", [])
            
            for m in data:
                # Memeriksa status dan id_program_studi
                if m.get("status_mahasiswa_terakhir", "").upper() == "MENUNGGU ISI KRS" and \
                   int(m.get("id_program_studi", -1)) in ID_PRODI_DIIKUTKAN:
                    
                    nim = m.get("nim")
                    # Menggunakan fungsi calculate_semester yang sudah disatukan
                    semester = calculate_semester(m.get("angkatan", tahun))

                    alamat = email = nomor_telepon = "-"
                    ipk = m.get("ipk", "-")

                    if nim:
                        try:
                            # Gunakan COMMON_HEADERS untuk request biodata
                            bio_response = requests.post(API_URL_BIODATA_MAHASISWA, data={"nim": nim}, headers=COMMON_HEADERS, timeout=10)
                            bio_response.raise_for_status()
                            biodata = bio_response.json().get("data", {})
                            
                            # Membangun alamat dengan lebih rapi, menghindari koma ganda jika ada bagian yang kosong
                            alamat_parts = [
                                biodata.get('kelurahan', ''),
                                biodata.get('kecamatan', ''),
                                biodata.get('kotakab', ''),
                                biodata.get('propinsi', '')
                            ]
                            alamat = ", ".join(filter(None, alamat_parts)) if any(alamat_parts) else "-"
                            
                            email = biodata.get("email", "-")
                            nomor_telepon = biodata.get("hp", "-")
                        except requests.exceptions.RequestException as e:
                            print(f"Error fetching biodata for NIM {nim}: {e}")
                        except ValueError as e:
                            print(f"Error parsing biodata JSON for NIM {nim}: {e}")
                        except Exception as e:
                            print(f"Error processing biodata for NIM {nim}: {e}")

                    result.append({
                        "nim": nim,
                        "nama_mahasiswa": m.get("nama_mahasiswa", "-"),
                        "nama_program_studi": m.get("nama_program_studi", "-"),
                        "ipk": ipk,
                        "semester": str(semester), # Pastikan semester berupa string
                        "alamat": alamat,
                        "email": email,
                        "nomor_telepon": nomor_telepon,
                        "status": "Aktif Tidak Isi KRS"
                    })
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Gagal ambil data untuk angkatan {tahun}: {e}")
        except ValueError as e:
            print(f"[ERROR] Gagal parse JSON untuk angkatan {tahun}: {e}")
        except Exception as e:
            print(f"[ERROR] Terjadi error tak terduga untuk angkatan {tahun}: {e}")
            continue

    return jsonify(result)