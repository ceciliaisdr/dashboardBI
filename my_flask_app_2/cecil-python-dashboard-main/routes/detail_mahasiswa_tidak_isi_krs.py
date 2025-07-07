# DETAIL MAHASISWA BELUM ISI KRS
from flask import Blueprint, jsonify, request
import requests
import base64
from datetime import datetime

detail_krs_bp = Blueprint('detail_krs_bp', __name__)

def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"

@detail_krs_bp.route('/api/mahasiswa-belum-isi-krs', methods=['GET'])
def get_mahasiswa_belum_isi_krs():
    url = 'https://api.upnvj.ac.id/data/list_mahasiswa'
    url_biodata = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'
    tahun_list = ["2020", "2021", "2022", "2023", "2024"]

    username = "uakademik"
    password = "VTUzcjRrNGRlbTFrMjAyNCYh"
    api_key = "X-UPNVJ-API-KEY"
    api_secret = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

    def basic_auth(username, password):
        token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
        return f'Basic {token}'

    headers = {
        "API_KEY_NAME": api_key,
        "API_KEY_SECRET": api_secret,
        "Accept": 'application/json',
        "Authorization": basic_auth(username, password),
    }

    id_prodi_diambil = [3, 4, 6, 58]
    result = []

    now = datetime.now()
    tahun_sekarang = now.year
    bulan_sekarang = now.month

    for tahun in tahun_list:
        try:
            response = requests.post(url, data={"angkatan": tahun}, headers=headers)
            if response.status_code == 200:
                data = response.json().get("data", [])
                for m in data:
                    if m.get("status_mahasiswa_terakhir", "").upper() == "MENUNGGU ISI KRS" and int(m.get("id_program_studi", -1)) in id_prodi_diambil:
                        nim = m.get("nim")

                        tahun_angkatan = int(m.get("angkatan", tahun))
                        selisih_tahun = tahun_sekarang - tahun_angkatan
                        semester = selisih_tahun * 2 if bulan_sekarang <= 7 else selisih_tahun * 2 + 1

                        biodata = {}
                        try:
                            bio_response = requests.post(url_biodata, data={"nim": nim}, headers=headers)
                            if bio_response.status_code == 200:
                                biodata = bio_response.json().get("data", {})
                        except Exception as e:
                            print(f"Error ambil biodata {nim}: {e}")

                        alamat = f"{biodata.get('kelurahan', '')}, {biodata.get('kecamatan', '')}, {biodata.get('kotakab', '')}, {biodata.get('propinsi', '')}"
                        result.append({
                            "nim": nim,
                            "nama_mahasiswa": m.get("nama_mahasiswa", "-"),
                            "nama_program_studi": m.get("nama_program_studi", "-"),
                            "ipk": m.get("ipk", biodata.get("ipk", "-")),
                            "semester": str(semester),
                            "alamat": alamat,
                            "email": biodata.get("email", "-"),
                            "nomor_telepon": biodata.get("hp", "-"),
                            "status": "Aktif Tidak Isi KRS"
                        })
        except Exception as e:
            print(f"[ERROR {tahun}]: {e}")
            continue

    return jsonify(result)