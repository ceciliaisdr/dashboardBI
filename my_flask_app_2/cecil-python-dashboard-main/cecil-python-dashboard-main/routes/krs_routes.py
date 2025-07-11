from flask import Blueprint, jsonify, request
import requests
import base64

krs_bp = Blueprint('krs_bp', __name__)

# === Konfigurasi Auth & API ===
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

API_URL_LIST_MAHASISWA = 'https://api.upnvj.ac.id/data/list_mahasiswa'

TAHUN_LIST_UMUM = ["2020", "2021", "2022", "2023", "2024"]

ID_PRODI_MAPPING = {
    3: "S1 Sistem Informasi",
    4: "S1 Informatika",
    6: "D3 Sistem Informasi",
    58: "S1 Sains Data"
}

def get_basic_auth_header(USERNAME,PASSWORD):
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"

COMMON_HEADERS = {
    "X-UPNVJ-API-KEY": API_SECRET,
    "Accept": 'application/json',
    "Authorization": get_basic_auth_header(USERNAME,PASSWORD),
    "User-Agent": "Thunder Client (https://www.thunderclient.com)"
}

# DIAGRAM BATANG PERBANDINGAN MHS AKTIF, NON AKTIF, AKTIF TIDAK ISI KRS
def fetch_status_mahasiswa_by_angkatan_final():
    # Format result: {"ALL": {...}, "2020": {...}, ...}
    result = {
        "ALL": {prodi: {"aktif": 0, "nonaktif": 0, "belum_isi_krs": 0} for prodi in ID_PRODI_MAPPING.values()}
    }

    for tahun in TAHUN_LIST_UMUM:
        result[tahun] = {prodi: {"aktif": 0, "nonaktif": 0, "belum_isi_krs": 0} for prodi in ID_PRODI_MAPPING.values()}

        try:
            response = requests.post(API_URL_LIST_MAHASISWA, data={"angkatan": tahun}, headers=COMMON_HEADERS)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            mahasiswa_list = response.json().get("data", [])

            for mhs in mahasiswa_list:
                id_prodi = int(mhs.get("id_program_studi", -1))
                prodi_name = ID_PRODI_MAPPING.get(id_prodi)
                if not prodi_name:
                    continue

                status = mhs.get("status_mahasiswa_terakhir", "").upper()

                if status == "AKTIF":
                    result[tahun][prodi_name]["aktif"] += 1
                    result["ALL"][prodi_name]["aktif"] += 1
                elif status == "NON-AKTIF":
                    result[tahun][prodi_name]["nonaktif"] += 1
                    result["ALL"][prodi_name]["nonaktif"] += 1
                elif status == "CUTI": # Asumsi "CUTI" di sini berarti "belum_isi_krs"
                    result[tahun][prodi_name]["belum_isi_krs"] += 1
                    result["ALL"][prodi_name]["belum_isi_krs"] += 1

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Gagal ambil data untuk angkatan {tahun}: {e}")
        except ValueError as e:
            print(f"[ERROR] Gagal parse JSON untuk angkatan {tahun}: {e}")
        except Exception as e:
            print(f"[ERROR] Terjadi error tak terduga untuk angkatan {tahun}: {e}")

    return result

@krs_bp.route('/api/status-mahasiswa4', methods=['GET'])
def get_status_mahasiswa4():
    angkatan = request.args.get('angkatan')
    data = fetch_status_mahasiswa_by_angkatan_final()

    if angkatan:
        return jsonify({angkatan: data.get(angkatan, {})})
    else:
        return jsonify(data)