from flask import Blueprint, jsonify, request
import base64
import requests
import re
from datetime import datetime

statmhs_bp = Blueprint('statmhs_bp', __name__)

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

# PERBANDINGAN MAHASISWA AKTIF, NON AKTIF, DAN TOTALNYA
def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

def fetch_status_mahasiswa():
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

    result = {
        "ALL": {prodi: {"aktif": 0, "nonaktif": 0, "total": 0} for prodi in id_prodi_mapping.values()}
    }

    for tahun in tahun_list:
        period = f"{tahun}/{int(tahun)+1}"
        result[period] = {prodi: {"aktif": 0, "nonaktif": 0, "total": 0} for prodi in id_prodi_mapping.values()}

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
                        result[period][prodi_name]["aktif"] += 1
                        result["ALL"][prodi_name]["aktif"] += 1
                    elif status == "NON-AKTIF":
                        result[period][prodi_name]["nonaktif"] += 1
                        result["ALL"][prodi_name]["nonaktif"] += 1

                for prodi in id_prodi_mapping.values():
                    result[period][prodi]["total"] = result[period][prodi]["aktif"] + result[period][prodi]["nonaktif"]
                    result["ALL"][prodi]["total"] = result["ALL"][prodi]["aktif"] + result["ALL"][prodi]["nonaktif"]

        except Exception as e:
            print(f"Error fetching data for {tahun}: {e}")

    return result

@statmhs_bp.route('/api/status-mahasiswa', methods=['GET'])
def get_status_mahasiswa():
    angkatan = request.args.get('angkatan')
    all_data = fetch_status_mahasiswa()

    if angkatan:
        return jsonify({angkatan: all_data.get(angkatan, {})})
    else:
        return jsonify({"ALL": all_data.get("ALL", {})})
    
# DETAIL MAHASISWA AKTIF-NON AKTIF
from datetime import datetime
from flask import jsonify
import base64
import requests
import time 

@statmhs_bp.route('/api/mahasiswa-aktif-nonaktif')
def get_mahasiswa_aktif_nonaktif():
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

    tahun_sekarang = datetime.now().year
    bulan_sekarang = datetime.now().month

    for tahun in tahun_list:
        try:
            response = requests.post(url, data={"angkatan": tahun}, headers=headers)
            if response.status_code == 200:
                data = response.json().get("data", [])
                for m in data:
                    status = m.get("status_mahasiswa_terakhir", "").upper()
                    if status in ["AKTIF", "NON-AKTIF"] and int(m.get("id_program_studi", -1)) in id_prodi_diambil:
                        tahun_masuk = int(m.get("angkatan", tahun))
                        jumlah_tahun = tahun_sekarang - tahun_masuk
                        semester = jumlah_tahun * 2 + (1 if 2 <= bulan_sekarang <= 7 else 2)
                        m["semester"] = str(semester)

                        # Ambil IPK langsung dari response list_mahasiswa
                        m["ipk"] = m.get("ipk", "-")

                        nim = m.get("nim")
                        try:
                            time.sleep(0.2)
                            bio_response = requests.post(url_biodata, data={"nim": nim}, headers=headers, timeout=10)
                            if bio_response.status_code == 200:
                                biodata = bio_response.json().get("data", {})
                                alamat = f"{biodata.get('kelurahan', '')}, {biodata.get('kecamatan', '')}, {biodata.get('kotakab', '')}, {biodata.get('propinsi', '')}"
                                m["alamat"] = alamat
                                m["email"] = biodata.get("email", "")
                                m["nomor_telepon"] = biodata.get("hp", "")
                            else:
                                m["alamat"] = m["email"] = m["nomor_telepon"] = "-"
                        except Exception as e:
                            print(f"Error ambil biodata {nim}: {e}")
                            m["alamat"] = m["email"] = m["nomor_telepon"] = "-"
                            angkatan = m.get("angkatan")
                            if not angkatan and m.get("nim") and len(m["nim"]) >= 2:
                                angkatan = "20" + m["nim"][:2]  # Contoh: "21" → "2021"
                            m["angkatan"] = angkatan

                        result.append(m)
        except Exception as e:
            print(f"Error ambil data {tahun}: {e}")
            continue

    return jsonify(result)

# DETAIL MAHASISWA DO & KELUAR
from datetime import datetime
from flask import jsonify
import base64
import requests

@statmhs_bp.route('/api/mahasiswa-do-keluar')
def get_mahasiswa_do_keluar():
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

    tahun_sekarang = datetime.now().year
    bulan_sekarang = datetime.now().month

    for tahun in tahun_list:
        try:
            response = requests.post(url, data={"angkatan": tahun}, headers=headers)
            if response.status_code == 200:
                data = response.json().get("data", [])
                for m in data:
                    status = m.get("status_mahasiswa_terakhir", "").upper()
                    if status in ["DROP-OUT/PUTUS STUDI", "KELUAR"] and int(m.get("id_program_studi", -1)) in id_prodi_diambil:
                        tahun_masuk = int(m.get("angkatan", tahun))
                        jumlah_tahun = tahun_sekarang - tahun_masuk
                        semester = jumlah_tahun * 2 + (1 if 2 <= bulan_sekarang <= 7 else 2)
                        m["semester"] = str(semester)

                        # Ambil IPK langsung dari response list_mahasiswa
                        m["ipk"] = m.get("ipk", "-")

                        nim = m.get("nim")
                        try:
                            bio_response = requests.post(url_biodata, data={"nim": nim}, headers=headers)
                            if bio_response.status_code == 200:
                                biodata = bio_response.json().get("data", {})
                                alamat = f"{biodata.get('kelurahan', '')}, {biodata.get('kecamatan', '')}, {biodata.get('kotakab', '')}, {biodata.get('propinsi', '')}"
                                m["alamat"] = alamat
                                m["email"] = biodata.get("email", "")
                                m["nomor_telepon"] = biodata.get("hp", "")
                            else:
                                m["alamat"] = m["email"] = m["nomor_telepon"] = "-"
                        except Exception as e:
                            print(f"Error ambil biodata {nim}: {e}")
                            m["alamat"] = m["email"] = m["nomor_telepon"] = "-"
                            angkatan = m.get("angkatan")
                            if not angkatan and m.get("nim") and len(m["nim"]) >= 2:
                                angkatan = "20" + m["nim"][:2]  # Contoh: "21" → "2021"
                            m["angkatan"] = angkatan

                        result.append(m)
        except Exception as e:
            print(f"Error ambil data {tahun}: {e}")
            continue

    return jsonify(result)

# PERBANDINGAN MAHASISWA AKTIF, NON AKTIF, DAN CUTI
def fetch_status_mahasiswa2():
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

    result = {
    "ALL": {prodi: {"aktif": 0, "nonaktif": 0, "cuti": 0, "keluar": 0, "dropout": 0, "total": 0} for prodi in id_prodi_mapping.values()}
    }

    for tahun in tahun_list:
        period = f"{tahun}/{int(tahun)+1}"
        result[period] = {prodi: {"aktif": 0, "nonaktif": 0, "cuti": 0, "keluar": 0, "dropout": 0, "total": 0} for prodi in id_prodi_mapping.values()}

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
                        result[period][prodi_name]["aktif"] += 1
                        result["ALL"][prodi_name]["aktif"] += 1
                    elif status == "NON-AKTIF":
                        result[period][prodi_name]["nonaktif"] += 1
                        result["ALL"][prodi_name]["nonaktif"] += 1
                    elif status == "CUTI":
                        result[period][prodi_name]["cuti"] += 1
                        result["ALL"][prodi_name]["cuti"] += 1
                    elif status == "KELUAR":
                        result[period][prodi_name]["keluar"] += 1
                        result["ALL"][prodi_name]["keluar"] += 1
                    elif status == "DROP-OUT/PUTUS STUDI":
                        result[period][prodi_name]["dropout"] += 1
                        result["ALL"][prodi_name]["dropout"] += 1

                for prodi in id_prodi_mapping.values():
                    result[period][prodi]["total"] = sum(result[period][prodi].values()) - result[period][prodi]["total"]
                    result["ALL"][prodi]["total"] = sum(result["ALL"][prodi].values()) - result["ALL"][prodi]["total"]

        except Exception as e:
            print(f"Error fetching data for {tahun}: {e}")

    return result

@statmhs_bp.route('/api/status-mahasiswa2', methods=['GET'])
def get_status_mahasiswa2():
    angkatan = request.args.get('angkatan')
    all_data = fetch_status_mahasiswa2()

    if angkatan:
        return jsonify({angkatan: all_data.get(angkatan, {})})
    else:
        return jsonify({"ALL": all_data.get("ALL", {})})
    
# MAHASISWA CUTI
import requests
from flask import jsonify, request

def fetch_status_mahasiswa3(angkatan=None):
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

    result = {}

    # Cek apakah ada parameter angkatan yang diteruskan, jika ada hanya ambil data untuk angkatan tersebut
    tahun_list = [angkatan] if angkatan else tahun_list

    # Looping melalui semua tahun yang terpilih
    for tahun in tahun_list:
        period = f"{tahun}/{int(tahun)+1}"
        result[period] = {prodi: {"cuti": 0} for prodi in id_prodi_mapping.values()}

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
                    # Cek jika mahasiswa statusnya "CUTI"
                    if status == "CUTI":
                        result[period][prodi_name]["cuti"] += 1

        except Exception as e:
            print(f"Error fetching data for {tahun}: {e}")

    return result

@statmhs_bp.route('/api/status-mahasiswa3', methods=['GET'])
def get_status_mahasiswa3():
    angkatan = request.args.get('angkatan')  # Mengambil parameter angkatan dari query string
    all_data = fetch_status_mahasiswa3(angkatan)  # Mengambil data sesuai angkatan atau semua angkatan
    return jsonify({"ALL": all_data})

#DETAIL MAHASISWA CUTI
from datetime import datetime
from flask import jsonify
import base64
import requests

@statmhs_bp.route('/api/mahasiswa-cuti2')
def get_mahasiswa_cuti2():
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
    mahasiswa_cuti = []

    tahun_sekarang = datetime.now().year
    bulan_sekarang = datetime.now().month

    for tahun in tahun_list:
        try:
            response = requests.post(url, data={"angkatan": tahun}, headers=headers)
            if response.status_code == 200:
                data = response.json().get("data", [])
                for m in data:
                    if m.get("status_mahasiswa_terakhir", "").upper() == "CUTI" and int(m.get("id_program_studi", -1)) in id_prodi_diambil:
                        tahun_masuk = int(m.get("angkatan", tahun))
                        jumlah_tahun = tahun_sekarang - tahun_masuk
                        # Semester ganjil di bulan 8–12 & 1 → semester genap hingga Juli
                        semester = jumlah_tahun * 2 + (1 if bulan_sekarang <= 7 else 2)
                        m["semester"] = str(semester)

                        # IPK dari API langsung
                        m["ipk"] = m.get("ipk", "-")

                        nim = m.get("nim")
                        try:
                            bio_response = requests.post(url_biodata, data={"nim": nim}, headers=headers)
                            if bio_response.status_code == 200:
                                biodata = bio_response.json().get("data", {})
                                alamat = f"{biodata.get('kelurahan', '')}, {biodata.get('kecamatan', '')}, {biodata.get('kotakab', '')}, {biodata.get('propinsi', '')}"
                                m["alamat"] = alamat
                                m["email"] = biodata.get("email", "")
                                m["nomor_telepon"] = biodata.get("hp", "")
                            else:
                                m["alamat"] = m["email"] = m["nomor_telepon"] = "-"
                        except Exception as e:
                            print(f"Error ambil biodata {nim}: {e}")
                            m["alamat"] = m["email"] = m["nomor_telepon"] = "-"

                        mahasiswa_cuti.append(m)
        except Exception as e:
            print(f"Error ambil data {tahun}: {e}")
            continue

    return jsonify(mahasiswa_cuti)

#MAHASISWA MELEBIHI MASA PERIODE
from flask import Flask, jsonify
import requests
import base64
from datetime import datetime

def basic_auth(username, password):
    auth_str = f"{username}:{password}"
    return "Basic " + base64.b64encode(auth_str.encode()).decode()

@statmhs_bp.route('/api/lebih-periode', methods=['GET'])
def get_lebih_periode():
    return jsonify(fetch_mahasiswa_lebih_periode())

def fetch_mahasiswa_lebih_periode():
    url = 'https://api.upnvj.ac.id/data/list_mahasiswa'
    tahun_list = ["2018", "2019", "2020", "2021", "2022"]

    id_prodi_mapping = {
        3: ("S1 Sistem Informasi", 8),
        4: ("S1 Informatika", 8),
        6: ("D3 Sistem Informasi", 6),
        58: ("S1 Sains Data", 8),
    }

    # Kelompok semester masing-masing prodi
    kelompok_semester_s1 = [14, 12, 10]
    kelompok_semester_d3 = [12, 10, 8]

    result = {
        "D3 Sistem Informasi": {str(s): 0 for s in kelompok_semester_d3},
    }

    for s1 in ["S1 Sistem Informasi", "S1 Informatika", "S1 Sains Data"]:
        result[s1] = {str(s): 0 for s in kelompok_semester_s1}

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

    def hitung_semester_saat_ini(tanggal_masuk_str):
            try:
                tanggal_masuk = datetime.strptime(tanggal_masuk_str, "%Y-%m-%d")
                tahun_masuk = tanggal_masuk.year
                bulan_masuk = tanggal_masuk.month

                today = datetime.today()
                tahun_sekarang = today.year
                bulan_sekarang = today.month

                total_semester = (tahun_sekarang - tahun_masuk) * 2

                if bulan_masuk >= 8:  # masuk semester ganjil
                    total_semester -= 1

                if bulan_sekarang >= 8:
                    total_semester += 2
                else:
                    total_semester += 1

                return total_semester + 1  # semester pertama dihitung
            except Exception:
                return 0

    try:
        for tahun in tahun_list:
            response = requests.post(url, data={"angkatan": tahun}, headers=headers)
            if response.status_code == 200:
                mahasiswa_list = response.json().get("data", [])
                for mhs in mahasiswa_list:
                    try:
                        id_prodi = int(mhs.get("id_program_studi", -1))
                        tanggal_masuk = mhs.get("tanggal_mulai_masuk", "")
                        status_terakhir = mhs.get("status_mahasiswa_terakhir", "").upper()

                        if not tanggal_masuk or status_terakhir != "AKTIF":
                            continue

                        semester = hitung_semester_saat_ini(tanggal_masuk)

                        if id_prodi in id_prodi_mapping:
                            prodi_name, batas_semester = id_prodi_mapping[id_prodi]

                            if semester > batas_semester:
                                # Gunakan kelompok yang sesuai
                                if prodi_name == "D3 Sistem Informasi":
                                    kelompok = kelompok_semester_d3
                                else:
                                    kelompok = kelompok_semester_s1

                                for s in kelompok:
                                    if semester >= s:
                                        result[prodi_name][str(s)] += 1
                                        break
                    except Exception:
                        continue
    except Exception as e:
        print(f"Error fetching data: {e}")

    return result

#DETAIL MAHASISWA MELEBIHI PERIODE
from flask import Flask, jsonify, render_template
from datetime import datetime
import base64
import requests

def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

# Konfigurasi API
API_URL_LIST = 'https://api.upnvj.ac.id/data/list_mahasiswa'
API_URL_BIODATA = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'
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

@statmhs_bp.route('/api/mahasiswa-lebih-periode')
def get_mahasiswa_lebih_periode():
    tahun_list = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]
    id_prodi_s1 = [3, 4, 58]  # S1 Informatika, S1 Sistem Informasi, S1 Sains Data
    id_prodi_d3 = [6]         # D3 Sistem Informasi
    mahasiswa_lebih_periode = []

    tahun_sekarang = datetime.now().year
    bulan_sekarang = datetime.now().month

    for tahun in tahun_list:
        try:
            response = requests.post(API_URL_LIST, data={"angkatan": tahun}, headers=HEADERS)
            if response.status_code == 200:
                data = response.json().get("data", [])
                for m in data:
                    id_prodi = int(m.get("id_program_studi", -1))
                    if id_prodi not in id_prodi_s1 + id_prodi_d3:
                        continue

                    status = m.get("status_mahasiswa_terakhir", "").upper()
                    if status not in ["AKTIF", "NON-AKTIF", "CUTI"]:
                        continue

                    tahun_masuk = int(m.get("angkatan", tahun))
                    jumlah_tahun = tahun_sekarang - tahun_masuk

                    semester = jumlah_tahun * 2 if 2 <= bulan_sekarang <= 7 else jumlah_tahun * 2 - 1
                    batas_semester = 8 if id_prodi in id_prodi_s1 else 6

                    if semester > batas_semester:
                        nim = m.get("nim")
                        try:
                            bio_response = requests.post(API_URL_BIODATA, data={"nim": nim}, headers=HEADERS)
                            if bio_response.status_code == 200:
                                biodata = bio_response.json().get("data", {})
                                alamat = f"{biodata.get('kelurahan', '')}, {biodata.get('kecamatan', '')}, {biodata.get('kotakab', '')}, {biodata.get('propinsi', '')}"
                                m.update({
                                    "alamat": alamat,
                                    "email": biodata.get("email", "-"),
                                    "nomor_telepon": biodata.get("hp", "-"),
                                    "ipk": m.get("ipk", biodata.get("ipk", "-"))
                                })
                            else:
                                m.update({"alamat": "-", "email": "-", "nomor_telepon": "-", "ipk": "-"})
                        except Exception as e:
                            m.update({"alamat": "-", "email": "-", "nomor_telepon": "-", "ipk": "-"})
                            print(f"Error ambil biodata {nim}: {e}")

                        mahasiswa_lebih_periode.append({
                            "nim": m.get("nim"),
                            "nama": m.get("nama_mahasiswa"),
                            "prodi": m.get("nama_program_studi"),
                            "semester": semester,
                            "alamat": m.get("alamat"),
                            "email": m.get("email"),
                            "telp": m.get("nomor_telepon"),
                            "status": status,
                            "ipk": m.get("ipk"),
                            "angkatan": "20" + m.get("nim", "")[:2],
                            "catatan": "MAHASISWA MELEBIHI PERIODE"
                        })
        except Exception as e:
            print(f"Error ambil data {tahun}: {e}")
            continue

    return jsonify(mahasiswa_lebih_periode)

@statmhs_bp.route('/dekanstatdetaillebihperiode')
def show_mahasiswa_lebih_periode():
    response = get_mahasiswa_lebih_periode()
    mahasiswa_list = response.get_json()
    return render_template("dekan_stat_detail_lebihperiode.html", mahasiswa_list=mahasiswa_list)