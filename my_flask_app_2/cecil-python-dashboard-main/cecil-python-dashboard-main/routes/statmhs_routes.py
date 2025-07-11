from flask import Blueprint, jsonify, request, render_template
import base64
import requests
import re
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

statmhs_bp = Blueprint('statmhs_bp', __name__)

# === Global Auth & API Configuration ===
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

API_URL_LIST_MAHASISWA = 'https://api.upnvj.ac.id/data/list_mahasiswa'
API_URL_GET_BIODATA = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'

# Prodii ID Mapping
ID_PRODI_MAPPING = {
    3: "S1 Sistem Informasi",
    4: "S1 Informatika",
    6: "D3 Sistem Informasi",
    58: "S1 Sains Data"
}
# List of Prodi IDs to include (values from keys in ID_PRODI_MAPPING)
ID_PRODI_INCLUDED = set(ID_PRODI_MAPPING.keys())

# Dynamically generate years from 2018 to current year
TAHUN_ANGKATAN_LIST = [str(year) for year in range(2018, datetime.now().year + 1)]

# === Setup Common Headers ===
def get_basic_auth_header(USERNAME,PASSWORD):
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

COMMON_HEADERS = {
    "X-UPNVJ-API-KEY": API_SECRET,
    "Accept": 'application/json',
    "Authorization": get_basic_auth_header(USERNAME,PASSWORD),
    "User-Agent": "Thunder Client (https://www.thunderclient.com)"
}

# === Global Cache for Student List Data ===
ALL_MAHASISWA_DATA = None
LAST_DATA_FETCH_TIME = 0
CACHE_DURATION_LIST_SECONDS = 600  # 10 minutes for student list

# === Global Cache for Biodata Data (per NIM) ===
BIODATA_CACHE = {}
BIODATA_LAST_FETCH_TIME = {}
CACHE_DURATION_BIODATA_SECONDS = 3600 # 1 hour for biodata

# === Helper Function: Calculate Current Semester ===
def calculate_current_semester(angkatan_tahun_masuk):
    """
    Calculates the current active semester number for a student.
    Assumes academic years typically start with an odd semester (e.g., August/September).
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    angkatan_tahun_masuk = int(angkatan_tahun_masuk)

    years_diff = current_year - angkatan_tahun_masuk
    
    # Base semester number from full academic years completed
    current_semester_number = years_diff * 2
    
    # Adjust for the current period within the academic year
    # August (8) to December (12) and January (1) are typically Ganjil semester
    # February (2) to July (7) are typically Genap semester
    if current_month >= 8 or current_month == 1:
        current_semester_number += 1 # It's an odd semester (1, 3, 5, ...)
    elif current_month >= 2 and current_month <= 7:
        current_semester_number += 2 # It's an even semester (2, 4, 6, ...)
    
    # Ensure minimum semester is 1 if student is already enrolled (years_diff is 0, but month implies start)
    if current_semester_number == 0 and years_diff == 0:
        return 1 # If in their first year and before August, consider them in semester 1 soon
    
    return max(1, current_semester_number)


# === Fetch and Cache All Student List Data ===
def fetch_and_cache_all_mahasiswa_data():
    global ALL_MAHASISWA_DATA, LAST_DATA_FETCH_TIME

    now = time.time()
    if ALL_MAHASISWA_DATA is not None and (now - LAST_DATA_FETCH_TIME) < CACHE_DURATION_LIST_SECONDS:
        logging.info("Using cached student list data.")
        return ALL_MAHASISWA_DATA

    logging.info("Fetching fresh student list data from API...")
    data_per_tahun = {}
    for tahun in TAHUN_ANGKATAN_LIST:
        try:
            response = requests.post(API_URL_LIST_MAHASISWA, data={"angkatan": tahun}, headers=COMMON_HEADERS, timeout=30)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data_per_tahun[tahun] = response.json().get("data", [])
            logging.info(f"Successfully fetched data for angkatan {tahun}.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching student list data for angkatan {tahun}: {e}")
            data_per_tahun[tahun] = []
        except ValueError as e:
            logging.error(f"Error parsing JSON for student list angkatan {tahun}: {e}")
            data_per_tahun[tahun] = []

    ALL_MAHASISWA_DATA = data_per_tahun
    LAST_DATA_FETCH_TIME = now
    return data_per_tahun

# === Fetch and Cache Individual Biodata ===
def fetch_and_cache_biodata_by_nim(nim):
    now = time.time()
    if nim in BIODATA_CACHE and (now - BIODATA_LAST_FETCH_TIME.get(nim, 0)) < CACHE_DURATION_BIODATA_SECONDS:
        logging.debug(f"Using cached biodata for NIM: {nim}")
        return BIODATA_CACHE[nim]

    logging.info(f"Fetching fresh biodata for NIM: {nim}")
    try:
        # Add a small delay to respect API rate limits
        time.sleep(0.1) 

        response = requests.post(API_URL_GET_BIODATA, data={"nim": nim}, headers=COMMON_HEADERS, timeout=15)
        response.raise_for_status()
        biodata = response.json().get("data", {})
        
        BIODATA_CACHE[nim] = biodata
        BIODATA_LAST_FETCH_TIME[nim] = now
        return biodata
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching biodata for NIM {nim}: {e}")
        return {} # Return empty dict on error
    except ValueError as e:
        logging.error(f"Error parsing JSON for biodata NIM {nim}: {e}")
        return {}


# === Endpoint: PERBANDINGAN MAHASISWA AKTIF, NON AKTIF, DAN TOTALNYA ===
@statmhs_bp.route('/api/status-mahasiswa', methods=['GET'])
def get_status_mahasiswa():
    angkatan_param = request.args.get('angkatan')
    all_mahasiswa_data = fetch_and_cache_all_mahasiswa_data()

    result = {
        "ALL": {prodi: {"aktif": 0, "nonaktif": 0, "total": 0} for prodi in ID_PRODI_MAPPING.values()}
    }

    # Initialize result structure for specific years if angkatan_param is provided
    target_tahun_list = [angkatan_param] if angkatan_param else TAHUN_ANGKATAN_LIST
    for tahun in target_tahun_list:
        period = f"{tahun}/{int(tahun)+1}"
        result[period] = {prodi: {"aktif": 0, "nonaktif": 0, "total": 0} for prodi in ID_PRODI_MAPPING.values()}

    for tahun, mahasiswa_list in all_mahasiswa_data.items():
        if angkatan_param and tahun != angkatan_param:
            continue # Skip if specific angkatan requested and this is not it

        period = f"{tahun}/{int(tahun)+1}"
        # Ensure the period exists in result (it will if angkatan_param is None or matches)
        if period not in result: 
            result[period] = {prodi: {"aktif": 0, "nonaktif": 0, "total": 0} for prodi in ID_PRODI_MAPPING.values()}


        for mhs in mahasiswa_list:
            try:
                id_prodi = int(mhs.get("id_program_studi", -1))
                prodi_name = ID_PRODI_MAPPING.get(id_prodi)
                if not prodi_name:
                    continue

                status = mhs.get("status_mahasiswa_terakhir", "").upper()
                if status == "AKTIF":
                    result[period][prodi_name]["aktif"] += 1
                    result["ALL"][prodi_name]["aktif"] += 1
                elif status == "NON-AKTIF":
                    result[period][prodi_name]["nonaktif"] += 1
                    result["ALL"][prodi_name]["nonaktif"] += 1
            except ValueError:
                logging.warning(f"Invalid id_program_studi for student: {mhs.get('nim')}")
                continue

        for prodi in ID_PRODI_MAPPING.values():
            result[period][prodi]["total"] = result[period][prodi]["aktif"] + result[period][prodi]["nonaktif"]
            # "ALL" totals are accumulated across all years, so no need to sum them here again per year
            # The 'ALL' total is continuously updated inside the loop

    # Finalize "ALL" total after iterating all years
    for prodi in ID_PRODI_MAPPING.values():
        result["ALL"][prodi]["total"] = result["ALL"][prodi]["aktif"] + result["ALL"][prodi]["nonaktif"]


    if angkatan_param:
        return jsonify({angkatan_param: result.get(f"{angkatan_param}/{int(angkatan_param)+1}", {})})
    else:
        # For 'ALL' request, include all periods and the 'ALL' summary
        return jsonify(result)
    
# === Endpoint: DETAIL MAHASISWA AKTIF-NON AKTIF ===
@statmhs_bp.route('/api/mahasiswa-aktif-nonaktif')
def get_mahasiswa_aktif_nonaktif():
    all_mahasiswa_data = fetch_and_cache_all_mahasiswa_data()
    result = []

    for tahun_angkatan, mahasiswa_list in all_mahasiswa_data.items():
        for m in mahasiswa_list:
            try:
                status = m.get("status_mahasiswa_terakhir", "").upper()
                if status in ["AKTIF", "NON-AKTIF"] and int(m.get("id_program_studi", -1)) in ID_PRODI_INCLUDED:
                    tahun_masuk = int(m.get("angkatan", tahun_angkatan))
                    m["semester"] = str(calculate_current_semester(tahun_masuk))

                    # IPK should already be in list_mahasiswa response
                    m["ipk"] = m.get("ipk", "-")

                    nim = m.get("nim")
                    biodata = fetch_and_cache_biodata_by_nim(nim)
                    
                    alamat = f"{biodata.get('kelurahan', '')}, {biodata.get('kecamatan', '')}, {biodata.get('kotakab', '')}, {biodata.get('propinsi', '')}"
                    m["alamat"] = alamat.strip(", ") if alamat.strip(", ") else "-"
                    m["email"] = biodata.get("email", "-")
                    m["nomor_telepon"] = biodata.get("hp", "-")
                    
                    result.append(m)
            except ValueError as e:
                logging.warning(f"Invalid 'angkatan' or 'id_program_studi' for student: {m.get('nim')}. Error: {e}")
                continue
            except Exception as e:
                logging.error(f"Unexpected error processing student {m.get('nim')}: {e}")
                continue

    return jsonify(result)

# === Endpoint: DETAIL MAHASISWA DO & KELUAR ===
@statmhs_bp.route('/api/mahasiswa-do-keluar')
def get_mahasiswa_do_keluar():
    all_mahasiswa_data = fetch_and_cache_all_mahasiswa_data()
    result = []

    for tahun_angkatan, mahasiswa_list in all_mahasiswa_data.items():
        for m in mahasiswa_list:
            try:
                status = m.get("status_mahasiswa_terakhir", "").upper()
                if status in ["DROP-OUT/PUTUS STUDI", "KELUAR"] and int(m.get("id_program_studi", -1)) in ID_PRODI_INCLUDED:
                    tahun_masuk = int(m.get("angkatan", tahun_angkatan))
                    m["semester"] = str(calculate_current_semester(tahun_masuk))

                    m["ipk"] = m.get("ipk", "-")

                    nim = m.get("nim")
                    biodata = fetch_and_cache_biodata_by_nim(nim)
                    
                    alamat = f"{biodata.get('kelurahan', '')}, {biodata.get('kecamatan', '')}, {biodata.get('kotakab', '')}, {biodata.get('propinsi', '')}"
                    m["alamat"] = alamat.strip(", ") if alamat.strip(", ") else "-"
                    m["email"] = biodata.get("email", "-")
                    m["nomor_telepon"] = biodata.get("hp", "-")
                    
                    result.append(m)
            except ValueError as e:
                logging.warning(f"Invalid 'angkatan' or 'id_program_studi' for student: {m.get('nim')}. Error: {e}")
                continue
            except Exception as e:
                logging.error(f"Unexpected error processing student {m.get('nim')}: {e}")
                continue

    return jsonify(result)

# === Endpoint: PERBANDINGAN MAHASISWA AKTIF, NON AKTIF, DAN CUTI (with more statuses) ===
@statmhs_bp.route('/api/status-mahasiswa2', methods=['GET'])
def get_status_mahasiswa2():
    angkatan_param = request.args.get('angkatan')
    all_mahasiswa_data = fetch_and_cache_all_mahasiswa_data()

    result = {
        "ALL": {prodi: {"aktif": 0, "nonaktif": 0, "cuti": 0, "keluar": 0, "dropout": 0, "total": 0} for prodi in ID_PRODI_MAPPING.values()}
    }

    target_tahun_list = [angkatan_param] if angkatan_param else TAHUN_ANGKATAN_LIST
    for tahun in target_tahun_list:
        period = f"{tahun}/{int(tahun)+1}"
        result[period] = {prodi: {"aktif": 0, "nonaktif": 0, "cuti": 0, "keluar": 0, "dropout": 0, "total": 0} for prodi in ID_PRODI_MAPPING.values()}

    for tahun, mahasiswa_list in all_mahasiswa_data.items():
        if angkatan_param and tahun != angkatan_param:
            continue

        period = f"{tahun}/{int(tahun)+1}"
        if period not in result:
             result[period] = {prodi: {"aktif": 0, "nonaktif": 0, "cuti": 0, "keluar": 0, "dropout": 0, "total": 0} for prodi in ID_PRODI_MAPPING.values()}

        for mhs in mahasiswa_list:
            try:
                id_prodi = int(mhs.get("id_program_studi", -1))
                prodi_name = ID_PRODI_MAPPING.get(id_prodi)
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
            except ValueError:
                logging.warning(f"Invalid id_program_studi for student: {mhs.get('nim')}")
                continue

        for prodi in ID_PRODI_MAPPING.values():
            result[period][prodi]["total"] = sum(result[period][prodi].values()) # Sum all specific status counts
            # result["ALL"]["total"] will be summed up at the end from its components directly.

    # Finalize "ALL" total after iterating all years
    for prodi in ID_PRODI_MAPPING.values():
        result["ALL"][prodi]["total"] = sum(result["ALL"][prodi].values())

    if angkatan_param:
        return jsonify({angkatan_param: result.get(f"{angkatan_param}/{int(angkatan_param)+1}", {})})
    else:
        return jsonify(result)

# === Endpoint: MAHASISWA CUTI (Aggregated Count) ===
@statmhs_bp.route('/api/status-mahasiswa3', methods=['GET'])
def get_status_mahasiswa3():
    angkatan_param = request.args.get('angkatan')
    all_mahasiswa_data = fetch_and_cache_all_mahasiswa_data()

    result = {}

    target_tahun_list = [angkatan_param] if angkatan_param else TAHUN_ANGKATAN_LIST

    for tahun in target_tahun_list:
        period = f"{tahun}/{int(tahun)+1}"
        result[period] = {prodi: {"cuti": 0} for prodi in ID_PRODI_MAPPING.values()}

        mahasiswa_list = all_mahasiswa_data.get(tahun, [])
        for mhs in mahasiswa_list:
            try:
                id_prodi = int(mhs.get("id_program_studi", -1))
                prodi_name = ID_PRODI_MAPPING.get(id_prodi)
                if not prodi_name:
                    continue

                status = mhs.get("status_mahasiswa_terakhir", "").upper()
                if status == "CUTI":
                    result[period][prodi_name]["cuti"] += 1
            except ValueError:
                logging.warning(f"Invalid id_program_studi for student: {mhs.get('nim')}")
                continue

    return jsonify({"ALL": result if not angkatan_param else result.get(f"{angkatan_param}/{int(angkatan_param)+1}", {})})

# === Endpoint: DETAIL MAHASISWA CUTI ===
@statmhs_bp.route('/api/mahasiswa-cuti2')
def get_mahasiswa_cuti2():
    all_mahasiswa_data = fetch_and_cache_all_mahasiswa_data()
    mahasiswa_cuti = []

    for tahun_angkatan, mahasiswa_list in all_mahasiswa_data.items():
        for m in mahasiswa_list:
            try:
                if (m.get("status_mahasiswa_terakhir", "").upper() == "CUTI" and 
                    int(m.get("id_program_studi", -1)) in ID_PRODI_INCLUDED):
                    
                    tahun_masuk = int(m.get("angkatan", tahun_angkatan))
                    m["semester"] = str(calculate_current_semester(tahun_masuk))

                    m["ipk"] = m.get("ipk", "-")

                    nim = m.get("nim")
                    biodata = fetch_and_cache_biodata_by_nim(nim)
                    
                    alamat = f"{biodata.get('kelurahan', '')}, {biodata.get('kecamatan', '')}, {biodata.get('kotakab', '')}, {biodata.get('propinsi', '')}"
                    m["alamat"] = alamat.strip(", ") if alamat.strip(", ") else "-"
                    m["email"] = biodata.get("email", "-")
                    m["nomor_telepon"] = biodata.get("hp", "-")
                    
                    mahasiswa_cuti.append(m)
            except ValueError as e:
                logging.warning(f"Invalid 'angkatan' or 'id_program_studi' for student: {m.get('nim')}. Error: {e}")
                continue
            except Exception as e:
                logging.error(f"Unexpected error processing student {m.get('nim')}: {e}")
                continue

    return jsonify(mahasiswa_cuti)

# === Endpoint: MAHASISWA MELEBIHI MASA PERIODE (Aggregated Count) ===
@statmhs_bp.route('/api/lebih-periode', methods=['GET'])
def get_lebih_periode():
    result = {
        "D3 Sistem Informasi": {str(s): 0 for s in [12, 10, 8]}, # D3 max 6 semesters (3 years x 2 sem) -> so check for 8, 10, 12.
    }
    for s1_prodi in ["S1 Sistem Informasi", "S1 Informatika", "S1 Sains Data"]:
        result[s1_prodi] = {str(s): 0 for s in [14, 12, 10]} # S1 max 8 semesters (4 years x 2 sem) -> so check for 10, 12, 14.

    all_mahasiswa_data = fetch_and_cache_all_mahasiswa_data()

    for tahun, mahasiswa_list in all_mahasiswa_data.items():
        for mhs in mahasiswa_list:
            try:
                id_prodi = int(mhs.get("id_program_studi", -1))
                prodi_name = ID_PRODI_MAPPING.get(id_prodi)
                status_terakhir = mhs.get("status_mahasiswa_terakhir", "").upper()

                # Only consider active students within the included prodi
                if status_terakhir != "AKTIF" or prodi_name not in result:
                    continue

                # Ensure 'angkatan' is used consistently for semester calculation
                angkatan = mhs.get("angkatan", tahun) # Prefer 'angkatan' field from mhs, fallback to list's year
                semester_saat_ini = calculate_current_semester(angkatan)

                batas_semester_normal = 8 if prodi_name != "D3 Sistem Informasi" else 6

                if semester_saat_ini > batas_semester_normal:
                    # Determine which group to increment based on prodi and current semester
                    if prodi_name == "D3 Sistem Informasi":
                        kelompok_semesters = [12, 10, 8]
                    else:
                        kelompok_semesters = [14, 12, 10]
                    
                    for s_threshold in kelompok_semesters:
                        if semester_saat_ini >= s_threshold:
                            result[prodi_name][str(s_threshold)] += 1
                            break # Only count for the highest relevant threshold
            except ValueError:
                logging.warning(f"Invalid numeric data for student: {mhs.get('nim')}")
                continue
            except Exception as e:
                logging.error(f"Error processing student {mhs.get('nim')} for 'lebih-periode': {e}")
                continue

    return jsonify(result)

# === Endpoint: DETAIL MAHASISWA MELEBIHI PERIODE ===
@statmhs_bp.route('/api/mahasiswa-lebih-periode')
def get_mahasiswa_lebih_periode():
    all_mahasiswa_data = fetch_and_cache_all_mahasiswa_data()
    mahasiswa_lebih_periode = []

    for tahun_angkatan, mahasiswa_list in all_mahasiswa_data.items():
        for m in mahasiswa_list:
            try:
                id_prodi = int(m.get("id_program_studi", -1))
                prodi_name = ID_PRODI_MAPPING.get(id_prodi)
                
                # Check if prodi is included in the defined S1/D3 lists
                is_s1 = id_prodi in [3, 4, 58]
                is_d3 = id_prodi in [6]

                if not (is_s1 or is_d3):
                    continue

                status = m.get("status_mahasiswa_terakhir", "").upper()
                # Consider only ACTIVE, NON-ACTIVE, CUTI students for "melebihi periode"
                if status not in ["AKTIF", "NON-AKTIF", "CUTI"]:
                    continue

                tahun_masuk = int(m.get("angkatan", tahun_angkatan))
                semester_saat_ini = calculate_current_semester(tahun_masuk)
                
                batas_semester_normal = 8 if is_s1 else 6

                if semester_saat_ini > batas_semester_normal:
                    nim = m.get("nim")
                    biodata = fetch_and_cache_biodata_by_nim(nim)
                    
                    alamat = f"{biodata.get('kelurahan', '')}, {biodata.get('kecamatan', '')}, {biodata.get('kotakab', '')}, {biodata.get('propinsi', '')}"
                    m["alamat"] = alamat.strip(", ") if alamat.strip(", ") else "-"
                    m["email"] = biodata.get("email", "-")
                    m["nomor_telepon"] = biodata.get("hp", "-")
                    m["ipk"] = m.get("ipk", biodata.get("ipk", "-")) # Prefer list IPK, fallback to biodata

                    mahasiswa_lebih_periode.append({
                        "nim": m.get("nim"),
                        "nama": m.get("nama_mahasiswa"),
                        "prodi": prodi_name, # Use mapped name
                        "semester": semester_saat_ini,
                        "alamat": m.get("alamat"),
                        "email": m.get("email"),
                        "telp": m.get("nomor_telepon"),
                        "status": status,
                        "ipk": m.get("ipk"),
                        "angkatan": tahun_masuk,
                        "catatan": "MAHASISWA MELEBIHI PERIODE"
                    })
            except ValueError as e:
                logging.warning(f"Invalid numeric data for student: {m.get('nim')}. Error: {e}")
                continue
            except Exception as e:
                logging.error(f"Error processing student {m.get('nim')} for 'mahasiswa-lebih-periode' detail: {e}")
                continue

    return jsonify(mahasiswa_lebih_periode)

# === Web Endpoint for Display (requires Flask `render_template` setup) ===
@statmhs_bp.route('/dekanstatdetaillebihperiode')
def show_mahasiswa_lebih_periode():
    # Call the API endpoint within the Flask context to get JSON data
    response = get_mahasiswa_lebih_periode() 
    mahasiswa_list = response.get_json()
    # Ensure you have a 'templates' folder in your Flask app root 
    # and 'dekan_stat_detail_lebihperiode.html' file inside it.
    return render_template("dekan_stat_detail_lebihperiode.html", mahasiswa_list=mahasiswa_list)