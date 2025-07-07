# DIAGRAM BATANG PERBANDINGAN MHS AKTIF, NON AKTIF, AKTIF TIDAK ISI KRS
from flask import Blueprint, jsonify, request
import requests
import base64

krs_bp = Blueprint('krs_bp', __name__)

def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"

def fetch_status_mahasiswa_by_angkatan_final():
    url = 'https://api.upnvj.ac.id/data/list_mahasiswa'
    tahun_list = ["2020", "2021", "2022", "2023", "2024"]
    id_prodi_mapping = {
        3: "S1 Sistem Informasi",
        4: "S1 Informatika",
        6: "D3 Sistem Informasi",
        58: "S1 Sains Data"
    }

    username = "uakademik"
    password = "VTUzcjRrNGRlbTFrMjAyNCYh"
    api_key = "X-UPNVJ-API-KEY"
    api_secret = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

    headers = {
        "API_KEY_NAME": api_key,
        "API_KEY_SECRET": api_secret,
        "Accept": 'application/json',
        "Authorization": basic_auth(username, password),
    }

    # Format result: {"ALL": {...}, "2020": {...}, ...}
    result = {
        "ALL": {prodi: {"aktif": 0, "nonaktif": 0, "belum_isi_krs": 0} for prodi in id_prodi_mapping.values()}
    }

    for tahun in tahun_list:
        result[tahun] = {prodi: {"aktif": 0, "nonaktif": 0, "belum_isi_krs": 0} for prodi in id_prodi_mapping.values()}

        try:
            response = requests.post(url, data={"angkatan": tahun}, headers=headers)
            if response.status_code == 200:
                mahasiswa_list = response.json().get("data", [])

                for mhs in mahasiswa_list:
                    id_prodi = int(mhs.get("id_program_studi", -1))
                    prodi_name = id_prodi_mapping.get(id_prodi)
                    if not prodi_name:
                        continue

                    status = mhs.get("status_mahasiswa_terakhir", "").upper()

                    if status == "AKTIF":
                        result[tahun][prodi_name]["aktif"] += 1
                        result["ALL"][prodi_name]["aktif"] += 1
                    elif status == "NON-AKTIF":
                        result[tahun][prodi_name]["nonaktif"] += 1
                        result["ALL"][prodi_name]["nonaktif"] += 1
                    elif status == "CUTI":
                        # Dikonversi jadi "MENUNGGU ISI KRS"
                        result[tahun][prodi_name]["belum_isi_krs"] += 1
                        result["ALL"][prodi_name]["belum_isi_krs"] += 1

        except Exception as e:
            print(f"[ERROR] Gagal ambil data untuk angkatan {tahun}: {e}")

    return result

@krs_bp.route('/api/status-mahasiswa4', methods=['GET'])
def get_status_mahasiswa4():
    angkatan = request.args.get('angkatan')  # Optional, jika mau support ?angkatan=2021
    data = fetch_status_mahasiswa_by_angkatan_final()

    if angkatan:
        return jsonify({angkatan: data.get(angkatan, {})})
    else:
        return jsonify(data)
