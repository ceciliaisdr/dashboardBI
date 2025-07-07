from flask import Blueprint, jsonify, request
import base64
import requests
import re
from datetime import datetime

sainsdata_bp = Blueprint('sainsdata_bp', __name__)

def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

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

# DETAIL MAHASISWA S1 SAINS DATA (INI DI DEKAN_NILAI_SD.HTML)
from flask import Flask, render_template, jsonify
import requests
import base64
from datetime import datetime

# Fungsi Basic Auth
def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f"Basic {token}"

# Konfigurasi API
API_URL = "https://api.upnvj.ac.id/data/list_mahasiswa"
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_KEY = "X-UPNVJ-API-KEY"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

# ID Prodi S1 SAINS DATA (sesuai sistem)
NAMA_PRODI = "S1 SAINS DATA"

@sainsdata_bp.route('/dekannilaisd')
def dekan_nilai_sd():
    return render_template('dekan_nilai_sd.html')

@sainsdata_bp.route('/api/mahasiswa-sainsdata', methods=['GET'])
def api_mahasiswa_sd():
    import requests
    import base64
    from datetime import datetime

    tahun_sekarang = datetime.now().year
    angkatan_list = [str(tahun) for tahun in range(2018, tahun_sekarang + 1)]
    bulan_sekarang = datetime.now().month

    USERNAME = "uakademik"
    PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
    API_KEY = "X-UPNVJ-API-KEY"
    API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"
    ID_PRODI_SISFO = 58  # berdasarkan contoh respons JSON

    def basic_auth(username, password):
        token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
        return f'Basic {token}'

    headers = {
        "API_KEY_NAME": API_KEY,
        "API_KEY_SECRET": API_SECRET,
        "Accept": "application/json",
        "Authorization": basic_auth(USERNAME, PASSWORD),
    }

    result_data = []

    for angkatan in angkatan_list:
        try:
            response = requests.post(
                "https://api.upnvj.ac.id/data/list_mahasiswa",
                data={"angkatan": angkatan},
                headers=headers
            )
            response.raise_for_status()
            data = response.json().get("data", [])

            for mhs in data:
                if (
                    int(mhs.get("id_program_studi", -1)) == ID_PRODI_SISFO and
                    mhs.get("status_mahasiswa_terakhir", "").strip().upper() == "AKTIF"
                ):
                    tahun_masuk = int(mhs.get("tahun_angkatan", angkatan))
                    jumlah_tahun = tahun_sekarang - tahun_masuk
                    semester = jumlah_tahun * 2 if bulan_sekarang <= 7 else jumlah_tahun * 2 + 1

                    result_data.append({
                        "nim": mhs.get("nim"),
                        "nama": mhs.get("nama_mahasiswa"),
                        "angkatan": str(tahun_masuk),
                        "semester": semester,
                        "ipk": mhs.get("ipk", "-")  # Ambil IPK disini
                    })
        except Exception as e:
            print(f"Gagal ambil data angkatan {angkatan}: {e}")

    return jsonify(result_data)

# DETAIL MAHASISWA BESERTA DENGAN GRAFIKNYA

# 1. Nama dan ipk mahasiswanya
from flask import Flask, jsonify, render_template, request
from datetime import datetime
import base64
import requests

# AUTH CONFIG
def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

API_BIODATA = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'
API_HISTORI = 'https://api.upnvj.ac.id/data/list_histori_mahasiswa'
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_KEY = "X-UPNVJ-API-KEY"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

HEADERS = {
    "API_KEY_NAME": API_KEY,
    "API_KEY_SECRET": API_SECRET,
    "Accept": 'application/json',
    "Authorization": basic_auth(USERNAME, PASSWORD),
}

# Endpoint untuk menampilkan detail mahasiswa
@sainsdata_bp.route('/detailnilaisd/<nim>')
def detail_mahasiswa(nim):
    try:
        # Ambil biodata mahasiswa menggunakan API
        bio_resp = requests.post(API_BIODATA, data={"nim": nim}, headers=HEADERS)
        bio_data = bio_resp.json().get("data", {}) if bio_resp.status_code == 200 else {}

        # Hitung semester berdasarkan tahun masuk
        angkatan = int(bio_data.get("angkatan", 0))
        now = datetime.now()
        tahun_sekarang = now.year
        bulan = now.month
        semester_now = ((tahun_sekarang - angkatan) * 2) - (0 if bulan < 8 else -1)

        # Ambil histori akademik mahasiswa
        histori = []
        for semester in range(1, semester_now + 1):
            id_periode = f"{angkatan}{1 if semester % 2 != 0 else 2}"  # 1 untuk ganjil, 2 untuk genap
            resp = requests.post(API_HISTORI, data={"nim": nim, "id_periode": id_periode}, headers=HEADERS)
            if resp.status_code == 200 and resp.json().get("data"):
                entry = next((item for item in resp.json().get("data", []) if item.get("nim") == nim), {})
                histori.append({
                    "semester": f"Semester {semester}",
                    "ips": float(entry.get("ips", 0)),
                    "ipk": float(entry.get("ipk", 0)) if entry.get("ipk") else None
                })

        # Format alamat dari data
        alamat = ", ".join(filter(None, [
            bio_data.get("kelurahan", ""),
            bio_data.get("kecamatan", ""),
            bio_data.get("kotakab", ""),
            bio_data.get("propinsi", "")
        ]))

        # Render template dengan data mahasiswa dan histori IPK
        return render_template("detail_nilai_sd.html", mahasiswa={
            "nama": bio_data.get("nama", "-"),
            "nim": bio_data.get("nim", "-"),
            "semester": bio_data.get("semester_mahasiswa", "-"),
            "prodi": bio_data.get("nama_program_studi", "-"),
            "alamat": alamat,
            "status_mhs": bio_data.get("status", "-"),
            "ipk": bio_data.get("ipk", "-"),
            "ipk_histori": histori  # Data histori IPK yang akan digunakan untuk grafik
        })

    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}", 500