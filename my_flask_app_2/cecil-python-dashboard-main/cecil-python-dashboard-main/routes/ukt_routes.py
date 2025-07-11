from flask import Blueprint, jsonify, request
import base64
import requests
import re
import time
from datetime import datetime

ukt_bp = Blueprint('ukt_bp', __name__)

# === Konfigurasi Auth & API ===
# === Global Auth & API Configuration ===
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

API_URL = 'https://api.upnvj.ac.id/data/list_mahasiswa'
ID_PRODI_DIIKUTKAN = {3, 4, 6, 58}
TAHUN_LIST = ["2020", "2021", "2022", "2023", "2024"]

# === Setup Header Auth ===
def get_basic_auth_header(USERNAME,PASSWORD):
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


HEADERS = {
    "X-UPNVJ-API-KEY": API_SECRET,
    "Accept": 'application/json',
    "Authorization": get_basic_auth_header(USERNAME,PASSWORD),
    "User-Agent": "Thunder Client (https://www.thunderclient.com)"
}

# === Global Cache untuk data mahasiswa ===
ALL_MAHASISWA_DATA = None
LAST_DATA_FETCH_TIME = 0
CACHE_DURATION_SECONDS = 600  # 10 menit

# === Global Cache untuk distribusi UKT per angkatan ===
UKT_DISTRIBUSI_CACHE = {}
UKT_DISTRIBUSI_LAST_FETCH = {}
UKT_CACHE_DURATION_SECONDS = 600  # 10 menit


# === Ambil dan Cache Data Mahasiswa ===
def ambil_semua_data_mahasiswa():
    global ALL_MAHASISWA_DATA, LAST_DATA_FETCH_TIME

    now = time.time()
    if ALL_MAHASISWA_DATA is not None and (now - LAST_DATA_FETCH_TIME) < CACHE_DURATION_SECONDS:
        print("[INFO] Menggunakan cache data mahasiswa.")
        return ALL_MAHASISWA_DATA

    print("[INFO] Fetching fresh data dari API...")
    data_per_tahun = {}
    for tahun in TAHUN_LIST:
        try:
            response = requests.post(API_URL, data={"angkatan": tahun}, headers=HEADERS)
            if response.status_code == 200:
                res = response.json()
                data_per_tahun[tahun] = res.get("data", [])
            else:
                data_per_tahun[tahun] = []
        except Exception as e:
            print(f"[ERROR] {tahun}: {e}")
            data_per_tahun[tahun] = []

    ALL_MAHASISWA_DATA = data_per_tahun
    LAST_DATA_FETCH_TIME = now
    return data_per_tahun


# === Endpoint: /api/beasiswa-data ===
@ukt_bp.route('/api/beasiswa-data')
def get_beasiswa_data():
    data = ambil_semua_data_mahasiswa()
    result = {"KIPK": {}, "KJMU": {}}

    for tahun, mahasiswa_list in data.items():
        count_kipk = 0
        count_kjmu = 0

        for mhs in mahasiswa_list:
            if int(mhs.get("id_program_studi", -1)) in ID_PRODI_DIIKUTKAN:
                if mhs.get("kelompok_ukt") == "KIP-K":
                    count_kipk += 1
                if str(mhs.get("penerima_beasiswa_kjmu")).upper() == "KJMU":
                    count_kjmu += 1

        period = f"{tahun}/{int(tahun)+1}"
        result["KIPK"][period] = count_kipk
        result["KJMU"][period] = count_kjmu

    return jsonify(result)


# === Endpoint: /api/mahasiswa-kipk ===
@ukt_bp.route('/api/mahasiswa-kipk')
def get_mahasiswa_kipk():
    data = ambil_semua_data_mahasiswa()
    mahasiswa_kipk = []

    tahun_sekarang = datetime.now().year
    bulan_sekarang = datetime.now().month

    for tahun, mahasiswa_list in data.items():
        for m in mahasiswa_list:
            if m.get("kelompok_ukt") == "KIP-K" and int(m.get("id_program_studi", -1)) in ID_PRODI_DIIKUTKAN:
                tahun_masuk = int(m.get("angkatan", tahun))
                jumlah_tahun = tahun_sekarang - tahun_masuk
                semester = jumlah_tahun * 2 + (1 if 2 <= bulan_sekarang <= 7 else 2)
                m["semester"] = str(semester)
                mahasiswa_kipk.append(m)

    return jsonify(mahasiswa_kipk)


# === Endpoint: /api/ukt-distribusi ===
@ukt_bp.route('/api/ukt-distribusi')
def get_ukt_distribusi():
    global UKT_DISTRIBUSI_CACHE, UKT_DISTRIBUSI_LAST_FETCH

    angkatan_param = request.args.get('angkatan', 'ALL')
    now = time.time()

    # Cek apakah ada cache yang valid
    if angkatan_param in UKT_DISTRIBUSI_CACHE:
        last_fetch = UKT_DISTRIBUSI_LAST_FETCH.get(angkatan_param, 0)
        if (now - last_fetch) < UKT_CACHE_DURATION_SECONDS:
            print(f"[INFO] Menggunakan cache distribusi UKT angkatan={angkatan_param}")
            return jsonify(UKT_DISTRIBUSI_CACHE[angkatan_param])

    data = ambil_semua_data_mahasiswa()
    distribusi = {str(i): 0 for i in range(1, 9)}
    total = 0

    for tahun, mahasiswa_list in data.items():
        if angkatan_param != 'ALL' and tahun != angkatan_param:
            continue

        for m in mahasiswa_list:
            try:
                id_prodi = int(m.get("id_program_studi", -1))
                if id_prodi in ID_PRODI_DIIKUTKAN:
                    kelompok_str = m.get("kelompok_ukt")
                    if kelompok_str:
                        match = re.search(r'(\d+)', kelompok_str)
                        if match:
                            kelompok = match.group(1)
                            if kelompok in distribusi:
                                distribusi[kelompok] += 1
                                total += 1
            except Exception:
                continue

    result = {
        "distribusi": distribusi,
        "total": total
    }

    # Simpan cache distribusi
    UKT_DISTRIBUSI_CACHE[angkatan_param] = result
    UKT_DISTRIBUSI_LAST_FETCH[angkatan_param] = now
    print(f"[INFO] Cache distribusi UKT angkatan={angkatan_param} diperbarui.")

    return jsonify(result)


# === Optional: Reset semua cache ===
@ukt_bp.route('/api/reset-cache', methods=["POST"])
def reset_cache():
    global ALL_MAHASISWA_DATA, LAST_DATA_FETCH_TIME
    global UKT_DISTRIBUSI_CACHE, UKT_DISTRIBUSI_LAST_FETCH
    ALL_MAHASISWA_DATA = None
    LAST_DATA_FETCH_TIME = 0
    UKT_DISTRIBUSI_CACHE.clear()
    UKT_DISTRIBUSI_LAST_FETCH.clear()
    return jsonify({"message": "Semua cache telah dihapus."})
