from flask import Blueprint, jsonify, request
import requests
import base64
import re
import time
from datetime import datetime

ukt_bp = Blueprint('ukt_bp', __name__)

# === Konfigurasi Auth & API ===
username = "uakademik"
password = "VTUzcjRrNGRlbTFrMjAyNCYh"
api_secret = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

API_URL = 'https://api.upnvj.ac.id/data/list_mahasiswa'
ID_PRODI_DIIKUTKAN = {3, 4, 6, 58}
TAHUN_LIST = ["2020", "2021", "2022", "2023", "2024"]

# === Helper untuk Basic Auth ===
def basic_auth_header():
    token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

# === Header Lengkap ===
HEADERS = {
    "X-UPNVJ-API-KEY": api_secret,
    "Accept": "application/json",
    "Authorization": basic_auth_header(),
    "User-Agent": "Thunder Client (https://www.thunderclient.com)"
}

# === Global Cache ===
ALL_MAHASISWA_DATA = None
LAST_DATA_FETCH_TIME = 0
CACHE_DURATION_SECONDS = 600
UKT_DISTRIBUSI_CACHE = {}
UKT_DISTRIBUSI_LAST_FETCH = {}
UKT_CACHE_DURATION_SECONDS = 600


# === Ambil Data Mahasiswa dari API ===
def ambil_semua_data_mahasiswa():
    global ALL_MAHASISWA_DATA, LAST_DATA_FETCH_TIME

    now = time.time()
    if ALL_MAHASISWA_DATA and (now - LAST_DATA_FETCH_TIME) < CACHE_DURATION_SECONDS:
        print("[INFO] Menggunakan cache data mahasiswa.")
        return ALL_MAHASISWA_DATA

    print("[INFO] Fetch data fresh dari API...")
    data_per_tahun = {}
    for tahun in TAHUN_LIST:
        try:
            res = requests.post(API_URL, data={"angkatan": tahun}, headers=HEADERS, timeout=30)
            if res.status_code == 200:
                result = res.json()
                data = result.get("data", [])
                if data:
                    print(f"[INFO] Dapat {len(data)} mahasiswa untuk angkatan {tahun}")
                else:
                    print(f"[WARN] Data kosong untuk angkatan {tahun}")
                data_per_tahun[tahun] = data
            else:
                print(f"[ERROR] Status {res.status_code} untuk angkatan {tahun}")
                data_per_tahun[tahun] = []
        except Exception as e:
            print(f"[ERROR] Gagal ambil data {tahun}: {e}")
            data_per_tahun[tahun] = []

    ALL_MAHASISWA_DATA = data_per_tahun
    LAST_DATA_FETCH_TIME = now
    return data_per_tahun


# === Endpoint: Beasiswa Data ===
@ukt_bp.route('/api/beasiswa-data')
def get_beasiswa_data():
    data = ambil_semua_data_mahasiswa()
    result = {"KIPK": {}, "KJMU": {}}

    for tahun, mahasiswa_list in data.items():
        count_kipk, count_kjmu = 0, 0
        for mhs in mahasiswa_list:
            if int(mhs.get("id_program_studi", -1)) in ID_PRODI_DIIKUTKAN:
                if mhs.get("kelompok_ukt") == "KIP-K":
                    count_kipk += 1
                if str(mhs.get("penerima_beasiswa_kjmu", "")).upper() == "KJMU":
                    count_kjmu += 1
        period = f"{tahun}/{int(tahun) + 1}"
        result["KIPK"][period] = count_kipk
        result["KJMU"][period] = count_kjmu

    return jsonify(result)


# === Endpoint: Mahasiswa KIPK ===
@ukt_bp.route('/api/mahasiswa-kipk')
def get_mahasiswa_kipk():
    data = ambil_semua_data_mahasiswa()
    mahasiswa_kipk = []

    tahun_now, bulan_now = datetime.now().year, datetime.now().month

    for tahun, mahasiswa_list in data.items():
        for m in mahasiswa_list:
            if m.get("kelompok_ukt") == "KIP-K" and int(m.get("id_program_studi", -1)) in ID_PRODI_DIIKUTKAN:
                tahun_masuk = int(m.get("angkatan", tahun))
                jumlah_tahun = tahun_now - tahun_masuk
                semester = jumlah_tahun * 2 + (1 if 2 <= bulan_now <= 7 else 2)
                m["semester"] = str(semester)
                mahasiswa_kipk.append(m)

    return jsonify(mahasiswa_kipk)


# === Endpoint: UKT Distribusi ===
@ukt_bp.route('/api/ukt-distribusi')
def get_ukt_distribusi():
    global UKT_DISTRIBUSI_CACHE, UKT_DISTRIBUSI_LAST_FETCH

    angkatan = request.args.get('angkatan', 'ALL')
    now = time.time()

    if angkatan in UKT_DISTRIBUSI_CACHE:
        last_fetch = UKT_DISTRIBUSI_LAST_FETCH.get(angkatan, 0)
        if (now - last_fetch) < UKT_CACHE_DURATION_SECONDS:
            print(f"[INFO] Menggunakan cache distribusi UKT angkatan={angkatan}")
            return jsonify(UKT_DISTRIBUSI_CACHE[angkatan])

    data = ambil_semua_data_mahasiswa()
    distribusi = {str(i): 0 for i in range(1, 9)}
    total = 0

    for tahun, mahasiswa_list in data.items():
        if angkatan != 'ALL' and tahun != angkatan:
            continue
        for m in mahasiswa_list:
            try:
                if int(m.get("id_program_studi", -1)) in ID_PRODI_DIIKUTKAN:
                    kelompok_str = m.get("kelompok_ukt")
                    if kelompok_str:
                        match = re.search(r'(\d+)', kelompok_str)
                        if match:
                            kelompok = match.group(1)
                            if kelompok in distribusi:
                                distribusi[kelompok] += 1
                                total += 1
            except Exception as e:
                print(f"[WARN] Error parsing mahasiswa: {e}")
                continue

    result = {"distribusi": distribusi, "total": total}
    UKT_DISTRIBUSI_CACHE[angkatan] = result
    UKT_DISTRIBUSI_LAST_FETCH[angkatan] = now
    print(f"[INFO] Cache distribusi UKT angkatan={angkatan} diperbarui.")

    return jsonify(result)


# === Endpoint: Reset Cache ===
@ukt_bp.route('/api/reset-cache', methods=["POST"])
def reset_cache():
    global ALL_MAHASISWA_DATA, LAST_DATA_FETCH_TIME
    global UKT_DISTRIBUSI_CACHE, UKT_DISTRIBUSI_LAST_FETCH

    ALL_MAHASISWA_DATA = None
    LAST_DATA_FETCH_TIME = 0
    UKT_DISTRIBUSI_CACHE.clear()
    UKT_DISTRIBUSI_LAST_FETCH.clear()

    print("[INFO] Semua cache telah direset.")
    return jsonify({"message": "Semua cache telah dihapus."})
