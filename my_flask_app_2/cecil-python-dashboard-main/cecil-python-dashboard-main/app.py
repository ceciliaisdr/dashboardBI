from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, flash, session
import pandas as pd
import base64, requests
import numpy as np
from functools import wraps
from datetime import datetime
from collections import defaultdict
import re 
import time 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy users untuk login
dummy_users = [
    {"username": "dekan", "password": "dekanfik", "role": "dekan"},
    {"username": "wakil dekan", "password": "wadek1fik", "role": "wadek1"},
    {"username": "wakil dekan 2", "password": "wadek2fik", "role": "wadek2"},
    {"username": "tata usaha", "password": "tatausahafik", "role": "ktu"},
    {"username": "koordinator program studi", "password": "kaprodifik", "role": "kaprodi"},
    {"username": "akademik mahasiswa", "password": "mikmasfik", "role": "akademik"},
    {"username": "admin", "password": "admin123", "role": "admin"}
]


role_menu_access = {
    "dekan": ["ukt", "statmhs", "nilai", "krs"],
    "wadek1": ["statmhs", "nilai", "krs"],
    "wadek2": ["ukt", "statmhs"],
    "kaprodi": ["statmhs", "nilai", "krs"],
    "ktu": ["ukt", "statmhs", "krs"],
    "akademik": ["ukt", "statmhs", "nilai", "krs"],
    "admin": ["ukt", "statmhs", "nilai", "krs"]  # opsional
}

def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'role' not in session or session['role'] not in allowed_roles:
                flash("Anda tidak memiliki akses ke halaman ini.", "error")
                return redirect(url_for('home'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

# --- Global Data Cache ---
ALL_MAHASISWA_DATA = None
LAST_DATA_FETCH_TIME = 0
CACHE_DURATION_SECONDS = 3600 # Cache data for 1 hour (3600 seconds)

# Base URL for the external API
API_BASE_URL = "http://localhost:9000" # Define this for consistency

def fetch_all_mahasiswa_data():
    """
    Fetches all student data from the external API and caches it.
    It will only re-fetch if the cache is empty or has expired.
    Returns: tuple (list_of_mahasiswa_dicts, error_dict or None)
    """
    global ALL_MAHASISWA_DATA, LAST_DATA_FETCH_TIME

    current_time = time.time()
    if ALL_MAHASISWA_DATA is None or (current_time - LAST_DATA_FETCH_TIME) > CACHE_DURATION_SECONDS:
        print("Fetching fresh data from http://localhost:9000/api/mahasiswa...")
        temp_all_data = []
        page = 1
        limit = 99999

        try:
            while True:
                res = requests.get(f"{API_BASE_URL}/api/mahasiswa", params={"page": page, "limit": limit}, timeout=30)
                res.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
                json_data = res.json()
                data = json_data.get("data", []) # Get the list of students from 'data' key

                if not data: # No more data on this page
                    break

                temp_all_data.extend(data)

                # Check for pagination information if provided by the API
                # Assuming "pagination" is a top-level key in json_data
                if not json_data.get("pagination", {}).get("has_next", False):
                    break
                
                page += 1
            
            ALL_MAHASISWA_DATA = temp_all_data
            LAST_DATA_FETCH_TIME = current_time
            # Update: SISFO_MAHASISWA_DATA should be derived when needed, or kept separate if always needed
            # print(f"Data successfully fetched and cached. Total students: {len(ALL_MAHASISWA_DATA)}, S1 Sistem Informasi: {len(SISFO_MAHASISWA_DATA)}")
            print(f"Data successfully fetched and cached. Total students: {len(ALL_MAHASISWA_DATA)}")
            return ALL_MAHASISWA_DATA, None # SUCCESS: Return data and no error
        
        except requests.exceptions.RequestException as e:
            error_message = f"Error fetching data from external API: {e}"
            print(error_message)
            # If no data was ever fetched successfully, ALL_MAHASISWA_DATA might still be None.
            # We need to make sure we return something meaningful for the caller.
            if ALL_MAHASISWA_DATA is None: 
                ALL_MAHASISWA_DATA = [] # Initialize if it was never populated
            print("Using stale or empty cache due to fetch error.")
            return ALL_MAHASISWA_DATA, {"error": error_message} # ERROR: Return current data (could be empty) and error dict
        except ValueError as e: # Catch JSON decoding errors
            error_message = f"Error decoding JSON response from API: {e}"
            print(error_message)
            if ALL_MAHASISWA_DATA is None: 
                ALL_MAHASISWA_DATA = []
            print("Using stale or empty cache due to JSON error.")
            return ALL_MAHASISWA_DATA, {"error": error_message}
        except Exception as e:
            error_message = f"An unexpected error occurred during data fetch: {e}"
            print(error_message)
            if ALL_MAHASISWA_DATA is None: 
                ALL_MAHASISWA_DATA = []
            print("Using stale or empty cache due to unexpected error.")
            return ALL_MAHASISWA_DATA, {"error": error_message}
    else:
        print("Using cached data for mahasiswa.")
        return ALL_MAHASISWA_DATA, None # Using cache: Return cached data and no error

# Call the data fetching function once when the app starts
with app.app_context():
    # We call it, but ignore the returned data/error for startup; 
    # the global ALL_MAHASISWA_DATA will be populated.
    fetch_all_mahasiswa_data() 

# --- Helper Function for Semester Calculation ---
# (Pastikan calculate_current_semester() ada di sini seperti yang Anda berikan)
def calculate_current_semester(mahasiswa_data):
    """
    Calculates the current active semester for a student based on their enrollment year
    and current date, or returns their status if they are not active.
    This function will be used for the list view (dekannilaisisfo).
    """
    status_mahasiswa = mahasiswa_data.get("status_mahasiswa_terakhir", "").upper()

    # If status is not 'AKTIF', return the status string directly
    if status_mahasiswa != 'AKTIF':
        return status_mahasiswa

    tahun_angkatan_str = mahasiswa_data.get("tahun_angkatan")
    if not tahun_angkatan_str:
        return "-"

    try:
        tahun_angkatan = int(tahun_angkatan_str)
    except (ValueError, TypeError):
        return "-"

    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    # Define academic year start and end months
    # Ganjil: Aug - Jan (e.g., Aug 2024 - Jan 2025)
    # Genap: Feb - July (e.g., Feb 2025 - July 2025)
    
    # Determine the current academic year based on the current month
    if current_month >= 8: # If current month is Aug-Dec, current academic year starts in current_year
        current_academic_year_start = current_year
    else: # If current month is Jan-Jul, current academic year started in previous_year
        current_academic_year_start = current_year - 1

    # Calculate years enrolled since their intake academic year
    # E.g., Angkatan 2020. Current academic year 2024/2025. years_enrolled = 2024 - 2020 = 4.
    years_enrolled = current_academic_year_start - tahun_angkatan

    # Calculate the base semester number. Each year adds 2 semesters.
    # Semester 1 (Ganjil) for year_0, Semester 3 (Ganjil) for year_1, etc.
    # The `+1` is for the first (odd) semester of the academic year.
    calculated_semester_base = (years_enrolled * 2) + 1

    # Adjust for current semester period (Ganjil vs Genap)
    # If current month is Feb-July, it's the even semester period.
    if current_month >= 2 and current_month <= 7: # Period for even semesters
        # If the base calculated semester is odd (1, 3, 5...), add 1 to make it even (2, 4, 6...).
        # This means the student is currently in the even semester of that academic year.
        if calculated_semester_base % 2 != 0:
            calculated_semester_base += 1
    # If current month is Aug-Jan, it's the odd semester period, so calculated_semester_base is already correct.

    # Ensure semester is at least 1
    if calculated_semester_base < 1:
        calculated_semester_base = 1

    # It's generally good practice to consider the highest semester from actual grade data
    # to avoid showing a lower semester if the student has completed more.
    max_semester_from_grades = 0
    if mahasiswa_data.get("nilai_mahasiswa"):
        for nilai in mahasiswa_data["nilai_mahasiswa"]:
            if nilai.get("semester"):
                try:
                    max_semester_from_grades = max(max_semester_from_grades, int(nilai["semester"]))
                except (ValueError, TypeError):
                    continue
    
    # Use the higher value between calculated and actual recorded grades
    final_semester = max(calculated_semester_base, max_semester_from_grades)

    return str(final_semester)

# --- Utility functions for slugifying (as provided by you) ---
def slugify_for_url(text):
    if not text: return ""
    text = re.sub(r'\s+', '-', text) 
    text = re.sub(r'[^\w-]', '', text) 
    return text

def unslugify_to_prodi_name(slug):
    if not slug: return ""
    return slug.replace('-', ' ')

# Fungsi untuk membaca file CSV dan menyiapkan data untuk grafik
def load_chart_data(file_path='static/mahasiswa_keseluruhan.csv'):
    """
    Membaca data dari file CSV dan menyiapkan data untuk grafik.
    :param file_path: Lokasi file CSV
    :return: Dictionary dengan data labels dan values
    """
    try:
        # Membaca file CSV
        df = pd.read_csv(file_path)
        
        # Menyiapkan data untuk grafik
        labels = df['Program Studi'].tolist()
        values = df['Jumlah Mahasiswa'].tolist()
        return {'labels': labels, 'values': values}
    except Exception as e:
        raise ValueError(f"Error loading data: {e}")

# Baca file excel ukt
# Banyak mahasiswa yang menunggak
@app.route("/api/tunggakan-ukt-angkatan")
def get_tunggakan_per_angkatan():
    df = pd.read_csv("static/Tunggakan.csv")
    df["NIM"] = df["NIM"].astype(str)

    df = df[df["NIM"].str.len() >= 2]
    df["Angkatan"] = df["NIM"].str[:2].apply(lambda x: f"20{x}" if x.isdigit() else "Unknown")

    selected_prodi = request.args.get("prodi", "all")
    if selected_prodi != "all":
        df = df[df["Program Studi"] == selected_prodi]

    unique_students = df.drop_duplicates(subset="NIM")
    grouped = unique_students.groupby("Angkatan")["NIM"].count().sort_index()

    # Convert ke list of built-in str & int (BUKAN numpy type!)
    return jsonify({
        "labels": [str(k) for k in grouped.index],
        "data": [int(v) for v in grouped.values]
    })

# Banyak tunggakan mahasiswa
@app.route("/api/perbandingan-tunggakan-status")
def get_line_data_by_status():
    from flask import request
    df = pd.read_csv("static/Tunggakan.csv")

    # Bersihkan dan transformasi
    df["Total Tunggakan"] = (
        df["Total Tunggakan"]
        .replace("-", "0")
        .str.replace(".", "", regex=False)
        .astype(float)
    )
    df["NIM"] = df["NIM"].astype(str)
    df = df[df["NIM"].str.len() >= 2]
    df["Angkatan"] = df["NIM"].str[:2].apply(lambda x: f"20{x}" if x.isdigit() else "Unknown")
    df["Status"] = df["Status"].str.strip().str.title()
    df["Program Studi"] = df["Program Studi"].str.strip()

    # Ambil filter prodi dari parameter query
    selected_prodi = request.args.get("prodi", "all")
    if selected_prodi != "all":
        df = df[df["Program Studi"] == selected_prodi]

    # Hitung total tunggakan per angkatan dan status
    grouped = (
        df.groupby(["Angkatan", "Status"])["Total Tunggakan"]
        .sum()
        .unstack(fill_value=0)
        .sort_index()
        / 1_000_000
    )

    # Format response untuk Chart.js
    return jsonify({
        "labels": list(grouped.index),
        "datasets": [
            {
                "label": status,
                "data": [float(v) for v in grouped[status]],
            }
            for status in grouped.columns
        ]
    })

#route
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/afterlogin', methods=['POST'])
def afterlogin():
    username = request.form['username']
    password = request.form['password']

    for user in dummy_users:
        if username == user['username'] and password == user['password']:
            session['username'] = username
            session['role'] = user['role']
            flash("Anda berhasil login", "success")
            return redirect(url_for('home'))

    flash("Username atau Password salah", "error")
    return redirect(url_for('index'))

@app.route('/get_chart_data', methods=['GET'])
def get_chart_data():
    """
    Endpoint untuk mengembalikan data grafik sebagai JSON.
    """
    try:
        data = load_chart_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

#button home
@app.route('/home')
def home():
    return render_template('afterlogin.html')

#button ukt
@app.route('/dekanukt')
@role_required(["dekan", "wadek2", "ktu", "akademik", "admin"])
def dekan_ukt():
    return render_template('dekanukt.html')

#button ukt prediksi
@app.route('/dekanuktprediksi')
def dekan_ukt_prediksi():
    return render_template('dekanuktprediksi.html')

@app.route('/filter_ukt', methods=['GET'])
def filter_ukt():
    period = request.args.get('period')
    # Logika untuk mengambil data berdasarkan periode (Ganjil/Genap)
    if period == 'ganjil':
        data = {"message": "Data untuk periode Ganjil"}
    elif period == 'genap':
        data = {"message": "Data untuk periode Genap"}
    else:
        data = {"message": "Periode tidak valid"}
    return jsonify(data)

#button krs
# @app.route('/dekankrs')
# def dekan_krs():
#     return render_template('dekankrs.html')

# Dummy data untuk jadwal pengisian KRS
jadwal_krs = [
    {"tahun_ajaran": "2020/2021", "semester": "Ganjil", "tanggal_mulai": "01-08-2020", "tanggal_selesai": "15-08-2020"},
    {"tahun_ajaran": "2020/2021", "semester": "Genap", "tanggal_mulai": "10-01-2021", "tanggal_selesai": "25-01-2021"},
    {"tahun_ajaran": "2021/2022", "semester": "Ganjil", "tanggal_mulai": "2021-07-15", "tanggal_selesai": "2021-07-30"},
    {"tahun_ajaran": "2021/2022", "semester": "Genap", "tanggal_mulai": "2022-01-10", "tanggal_selesai": "2022-01-25"},
    {"tahun_ajaran": "2022/2023", "semester": "Ganjil", "tanggal_mulai": "2022-07-18", "tanggal_selesai": "2022-08-01"},
    {"tahun_ajaran": "2022/2023", "semester": "Genap", "tanggal_mulai": "2023-01-12", "tanggal_selesai": "2023-01-26"},
    {"tahun_ajaran": "2023/2024", "semester": "Ganjil", "tanggal_mulai": "2023-07-20", "tanggal_selesai": "2023-08-03"},
    {"tahun_ajaran": "2023/2024", "semester": "Genap", "tanggal_mulai": "2024-01-15", "tanggal_selesai": "2024-01-28"},
    {"tahun_ajaran": "2024/2025", "semester": "Ganjil", "tanggal_mulai": "05-08-2024", "tanggal_selesai": "20-08-2024"},
    {"tahun_ajaran": "2024/2025", "semester": "Genap", "tanggal_mulai": "12-01-2025", "tanggal_selesai": "27-01-2025"},
]

mahasiswa_belum_isi_krs = [
        {"nim": "2110512013", "nama": "Divasya Valentiaji", "semester": 7, "prodi": "S1 Sistem Informasi", "alamat": "Jalan Kenangan", "email": "divasyavalentiaji@gmail.com", "telp": "089273164534", "status":"Tidak Aktif"},
        {"nim": "2210511037", "nama": "Cecilia Isadora Hutagalung", "semester": 5, "prodi": "S1 Informatika"},
        {"nim": "2310510141", "nama": "Natasha Azzahra Azis", "semester": 3, "prodi": "D3 Manajemen Informatika"},
    ]

mahasiswa_belum_isi_krs2 = [
        {"nim": "2110512013", "nama": "Divasya Valentiaji", "semester": 7, "prodi": "S1 Sistem Informasi", "alamat": "Jalan Kenangan", "email": "divasyavalentiaji@gmail.com", "telp": "089273164534", "status":"Tidak Aktif"},
        {"nim": "2210511037", "nama": "Cecilia Isadora Hutagalung", "semester": 5, "prodi": "S1 Informatika"},
        {"nim": "2310510141", "nama": "Natasha Azzahra Azis", "semester": 3, "prodi": "D3 Manajemen Informatika"},
    ]

# @app.route('/dekankrs')
# @role_required(["dekan", "wadek1", "kaprodi", "ktu", "akademik", "admin"])
# def dekan_krs():
#     return render_template('dekankrs.html', jadwal_krs=jadwal_krs, mahasiswa_belum_isi_krs=mahasiswa_belum_isi_krs)
@app.route('/dekankrs')
@role_required(["dekan", "wadek1", "kaprodi", "ktu", "akademik", "admin"])
def dekan_krs():
    return render_template("dekankrs_copy.html", jadwal_krs=jadwal_krs)

@app.route('/api/krs-status-comparison')
def krs_status_comparison():
    global ALL_MAHASISWA_DATA

    if ALL_MAHASISWA_DATA is None:
        fetch_all_mahasiswa_data()
        if ALL_MAHASISWA_DATA is None:
            return jsonify({"error": "Data mahasiswa belum tersedia."}), 503

    all_mahasiswa_list = ALL_MAHASISWA_DATA
    filter_angkatan = request.args.get('angkatan', 'ALL')

    if filter_angkatan != 'ALL':
        all_mahasiswa_list = [
            m for m in all_mahasiswa_list
            if m.get('tahun_angkatan') == filter_angkatan
        ]

    chart_data = {}

    for mhs in all_mahasiswa_list:
        prodi = mhs.get('nama_program_studi', 'Tidak Diketahui')
        status = (mhs.get('status_mahasiswa_terakhir') or '').strip().upper()

        # Inisialisasi struktur jika prodi belum ada
        if prodi not in chart_data:
            chart_data[prodi] = {
                "AKTIF": 0,
                "MENUNGGU ISI KRS": 0,
                "NON-AKTIF": 0
            }

        if status in chart_data[prodi]:
            chart_data[prodi][status] += 1

    return jsonify(chart_data)

# Route untuk halaman daftar mahasiswa belum isi KRS
# @app.route('/dekanbelumisikrs')
# def dekan_krsbelumisi():
#     return render_template('krs_detail_belumisikrs.html', mahasiswa_belum_isi_krs2=mahasiswa_belum_isi_krs2)

@app.route('/dekanbelumisikrs') # New route for "Belum Isi KRS" detail page
def dekanbelumisikrs_page():
    return render_template("dekan_stat_detail_belumisikrs.html")

@app.route('/api/mahasiswa-belum-isi-krs')
def get_mahasiswa_belum_isi_krs():
    global ALL_MAHASISWA_DATA
    if ALL_MAHASISWA_DATA is None:
        fetch_all_mahasiswa_data()
        if ALL_MAHASISWA_DATA is None:
            return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503

    all_mahasiswa_list = ALL_MAHASISWA_DATA

    if not isinstance(all_mahasiswa_list, list):
        return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
    if not all_mahasiswa_list:
        return jsonify([]), 200

    mahasiswa_belum_isi_krs = [
        m for m in all_mahasiswa_list
        if m.get('status_mahasiswa_terakhir', '').upper() == 'MENUNGGU ISI KRS'
    ]

    return jsonify(mahasiswa_belum_isi_krs)

# # Route untuk halaman daftar mahasiswa belum isi KRS
# @app.route('/dekankrsbelumisi')
# def dekan_krsbelumisikrrs():
#     return render_template('krs_detail_belumisikrs.html', mahasiswa_list=mahasiswa_belum_isi_krs)

# Route untuk halaman detail mahasiswa berdasarkan NIM
# @app.route('/mahasiswa/<nim>')
# def mahasiswa_detail(nim):
#     mahasiswa = next((mhs for mhs in mahasiswa_belum_isi_krs if mhs["nim"] == nim), None)
#     if mahasiswa:
#         return render_template('mahasiswadetail.html', mahasiswa=mahasiswa)
#     return "Mahasiswa tidak ditemukan", 404

# # Route untuk halaman detail mahasiswa berdasarkan NIM
# @app.route('/mahasiswa/<nim>')
# def mahasiswa_detail2(nim):
#     mahasiswa = next((mhs for mhs in mahasiswa_belum_isi_krs2 if mhs["nim"] == nim), None)
#     if mahasiswa:
#         return render_template('mahasiswadetail2.html', mahasiswa=mahasiswa)
#     return "Mahasiswa tidak ditemukan", 404

#button status mahasiswa
# @app.route('/dekanstatmhs')
# @role_required(["dekan", "wadek1", "wadek2", "kaprodi", "ktu", "akademik", "admin"])
# def dekan_statmhs():
#     url = 'https://api.upnvj.ac.id/data/list_mahasiswa'
#     username = "uakademik"
#     password = "VTUzcjRrNGRlbTFrMjAyNCYh"
#     api_key = "X-UPNVJ-API-KEY"
#     api_secret = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

#     def basic_auth(username, password):
#         token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
#         return f'Basic {token}'

#     headers = {
#         "API_KEY_NAME": api_key,
#         "API_KEY_SECRET": api_secret,
#         "Accept": 'application/json',
#         "Authorization": basic_auth(username, password),
#     }

#     tahun_list = ["2020", "2021", "2022", "2023", "2024"]
#     id_prodi_diambil = [3, 4, 6, 58]  # S1 SI, S1 IF, D3 SI, S1 SD

#     mahasiswa_nonaktif = []

#     for tahun in tahun_list:
#         try:
#             response = requests.post(url, data={"angkatan": tahun}, headers=headers)
#             if response.status_code == 200:
#                 data = response.json().get("data", [])
#                 for m in data:
#                     if m.get("status_mahasiswa_terakhir", "").upper() == "NON-AKTIF" and int(m.get("id_program_studi", -1)) in id_prodi_diambil:
#                         tahun_masuk = int(m.get("angkatan", tahun))
#                         periode = f"{tahun_masuk}/{tahun_masuk + 1}"

#                         mahasiswa_nonaktif.append({
#                             "periode": periode,
#                             "nim": m.get("nim", "-"),
#                             "nama": m.get("nama_mahasiswa", "-"),
#                             "nama_program_studi": m.get("nama_program_studi", "-")
#                         })
#         except Exception as e:
#             print(f"Error ambil data {tahun}: {e}")
#             continue

#     # Urutkan berdasarkan periode terbaru
#     mahasiswa_nonaktif = sorted(mahasiswa_nonaktif, key=lambda x: x.get("periode", "0/0"), reverse=True)

#     # Ambil 3 mahasiswa non-aktif teratas
#     top_3_mahasiswa_nonaktif = mahasiswa_nonaktif[:3]

#     return render_template('dekanstatmhs.html', top_3_mahasiswa_nonaktif=top_3_mahasiswa_nonaktif)
# Helper function to get unique statuses based on filters
def _get_all_unique_statuses(data_list, angkatan_filter='ALL', prodi_filter='ALL'):
    """
    Mengambil daftar status unik dari data mahasiswa berdasarkan filter.
    """
    filtered_data = data_list
    if angkatan_filter != 'ALL':
        filtered_data = [m for m in filtered_data if m.get('tahun_angkatan') == angkatan_filter]
    if prodi_filter != 'ALL':
        filtered_data = [m for m in filtered_data if m.get('nama_program_studi') == prodi_filter]
    
    status_set = sorted(list(set(
        m.get('status_mahasiswa_terakhir', '').upper()
        for m in filtered_data if m.get('status_mahasiswa_terakhir')
    )))
    return status_set

@app.route('/dekanstatmhs')
@role_required(["dekan", "wadek1", "wadek2", "kaprodi", "ktu", "akademik", "admin"])
def dekanstatmhs_page():
    return render_template("dekanstatmhs_copy.html")

# # ------------------ /api/getdata-aktif-nonaktif ------------------
# @app.route('/api/getdata-aktif-nonaktif')
# def getdata_aktif_nonaktif():
#     all_mahasiswa_list = ALL_MAHASISWA_DATA

#     if all_mahasiswa_list is None:
#         return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
#     if not isinstance(all_mahasiswa_list, list):
#         return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
#     if not all_mahasiswa_list:
#         return jsonify({"aktif": 0, "non_aktif": 0}), 200

#     filter_angkatan = request.args.get('angkatan', 'ALL')
#     filter_prodi = request.args.get('prodi', 'ALL')

#     data = all_mahasiswa_list
#     if filter_angkatan != 'ALL':
#         data = [m for m in data if m.get('tahun_angkatan') == filter_angkatan]
#     if filter_prodi != 'ALL':
#         data = [m for m in data if m.get('nama_program_studi') == filter_prodi]

#     aktif = sum(1 for m in data if m.get('status_mahasiswa_terakhir', '').upper() == 'AKTIF')
#     nonaktif = sum(1 for m in data if m.get('status_mahasiswa_terakhir', '').upper() == 'NON-AKTIF')

#     return jsonify({"aktif": aktif, "non_aktif": nonaktif})

@app.route('/api/getdata-status-counts')
def getdata_status_counts():
    all_mahasiswa_list = ALL_MAHASISWA_DATA

    if all_mahasiswa_list is None:
        return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
    if not isinstance(all_mahasiswa_list, list):
        return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
    if not all_mahasiswa_list:
        return jsonify({}), 200

    filter_angkatan = request.args.get('angkatan', 'ALL')
    filter_prodi = request.args.get('prodi', 'ALL') # Parameter ini tetap ada, akan 'ALL' dari JS

    # Dapatkan semua status unik yang mungkin dari seluruh dataset (tanpa filter angkatan/prodi)
    # Ini akan memastikan label chart konsisten bahkan jika status tertentu tidak ada di data yang difilter.
    known_statuses = _get_all_unique_statuses(all_mahasiswa_list, 'ALL', 'ALL')

    data_for_counts = all_mahasiswa_list
    if filter_angkatan != 'ALL':
        data_for_counts = [m for m in data_for_counts if m.get('tahun_angkatan') == filter_angkatan]
    # Tidak ada filter prodi di sini, sesuai permintaan pengguna untuk menampilkan semua prodi di chart
    # if filter_prodi != 'ALL':
    #     data_for_counts = [m for m in data_for_counts if m.get('nama_program_studi') == filter_prodi]

    status_counts = defaultdict(int)
    for m in data_for_counts:
        status = m.get('status_mahasiswa_terakhir', 'UNKNOWN').upper()
        status_counts[status] += 1
    
    # Pastikan semua status yang diketahui ada dalam hitungan, bahkan jika 0
    for status in known_statuses:
        if status not in status_counts:
            status_counts[status] = 0

    return jsonify(dict(status_counts))

# ------------------ /api/getdata-cuti ------------------
@app.route('/api/getdata-cuti')
def getdata_cuti():
    all_mahasiswa_list = ALL_MAHASISWA_DATA

    if all_mahasiswa_list is None:
        return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
    if not isinstance(all_mahasiswa_list, list):
        return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
    if not all_mahasiswa_list:
        return jsonify([]), 200

    result = [
        m for m in all_mahasiswa_list
        if m.get('status_mahasiswa_terakhir', '').upper() == 'CUTI'
    ]
    return jsonify(result)

# Asumsi fungsi calculate_current_semester sudah didefinisikan
def calculate_current_semester_for_status_mhs(tahun_angkatan):
    try:
        tahun = int(tahun_angkatan.split('/')[0])
    except (ValueError, IndexError):
        return 0 # Return 0 for invalid tahun_angkatan
    
    now = datetime.now()
    semester = 0
    
    # Calculate semesters from the enrollment year
    # Each academic year typically has 2 semesters (Odd: Sep-Feb, Even: Mar-Aug)
    
    # Iterate through years from enrollment year up to current year
    for y in range(now.year - tahun + 1):
        current_iter_year = tahun + y
        
        # Check for Odd Semester (starts Sept)
        if (current_iter_year == tahun and now.month >= 9) or (current_iter_year > tahun):
            semester += 1
        
        # Check for Even Semester (starts Mar)
        # This condition needs to be carefully crafted to avoid double counting or missing semesters
        # If current year, check if month is >= March but before Sept (for current even semester)
        # If past years, if the year is less than current year and month is >= March (meaning the even semester of that year has passed)
        if (current_iter_year == now.year and 3 <= now.month < 9) or \
           (current_iter_year < now.year and now.month >= 3):
            semester += 1
            
    return semester
    
# ------------------ /api/getdata-melebihi-masa-periode ------------------
# @app.route('/api/getdata-melebihi-masa-periode')
# def getdata_melebihi_masa_periode():
#     # Mengambil data mahasiswa dari cache atau sumber data Anda
#     # Pastikan ALL_MAHASISWA_DATA tersedia di konteks aplikasi Anda
#     all_mahasiswa_list = ALL_MAHASISWA_DATA

#     if all_mahasiswa_list is None:
#         return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
#     if not isinstance(all_mahasiswa_list, list):
#         return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
#     if not all_mahasiswa_list:
#         # Mengembalikan struktur kosong untuk prodi yang mungkin ada tapi tanpa data
#         # Ini penting agar chart tetap menampilkan label prodi, termasuk Semester 6
#         return jsonify({
#             "D3 Sistem Informasi": {"Semester 6": 0, "Semester 8": 0, "Semester 10": 0, "Semester 12": 0, "Semester 14": 0},
#             "S1 Informatika": {"Semester 6": 0, "Semester 8": 0, "Semester 10": 0, "Semester 12": 0, "Semester 14": 0},
#             "S1 Sains Data": {"Semester 6": 0, "Semester 8": 0, "Semester 10": 0, "Semester 12": 0, "Semester 14": 0},
#             "S1 Sistem Informasi": {"Semester 6": 0, "Semester 8": 0, "Semester 10": 0, "Semester 12": 0, "Semester 14": 0}
#         }), 200

#     # Batas semester normal untuk setiap program studi
#     # Mahasiswa melebihi batas ini dianggap 'melebihi masa studi normal'
#     normal_study_limits = {
#         'S1 Sistem Informasi': 8, # Normal 4 tahun = 8 semester
#         'S1 Informatika': 8,     # Normal 4 tahun = 8 semester
#         'S1 Sains Data': 8,      # Normal 4 tahun = 8 semester
#         'D3 Sistem Informasi': 6 # Normal 3 tahun = 6 semester
#     }

#     # Menggunakan defaultdict untuk menyimpan hitungan per prodi dan per kategori semester
#     # prodi_semester_counts = { "ProdiA": { "Semester6": X, "Semester8": Y, ... }, "ProdiB": { ... } }
#     prodi_semester_counts = defaultdict(lambda: defaultdict(int))

#     # Kategori semester untuk pengelompokan mahasiswa yang melebihi masa studi
#     # Berdasarkan semester aktual mereka saat ini
#     semester_categories = {
#         'Semester 6': lambda s: s >= 7 and s < 9,  # Mahasiswa di semester 7 atau 8
#         'Semester 8': lambda s: s >= 9 and s < 11, # Mahasiswa di semester 9 atau 10
#         'Semester 10': lambda s: s >= 11 and s < 13,
#         'Semester 12': lambda s: s >= 13 and s < 15,
#         'Semester 14': lambda s: s >= 15
#     }

#     for m in all_mahasiswa_list:
#         angkatan = m.get('tahun_angkatan')
#         prodi = m.get('nama_program_studi')
#         status = m.get('status_mahasiswa_terakhir', '').upper()

#         # Hanya pertimbangkan mahasiswa aktif dengan data angkatan dan prodi yang valid
#         if angkatan and prodi and status == 'AKTIF':
#             current_semester = calculate_current_semester_for_status_mhs(angkatan)
#             normal_limit = normal_study_limits.get(prodi)

#             # Pastikan prodi ada di normal_study_limits dan mahasiswa melebihi batas normal
#             if normal_limit is not None and current_semester > normal_limit:
#                 # Menentukan kategori semester mahasiswa
#                 for category_name, condition_func in semester_categories.items():
#                     if condition_func(current_semester): # Pass only 's' (current_semester)
#                         prodi_semester_counts[prodi][category_name] += 1
#                         break # Setelah menemukan kategori yang cocok, keluar dari loop kategori

#     # Mengonversi defaultdict ke dict biasa untuk jsonify
#     # Dan memastikan semua prodi yang diharapkan ada di output, meskipun nilainya 0
#     final_data = {}
#     all_prodi_in_data = set(normal_study_limits.keys()) # Ambil semua prodi yang relevan
#     # Define all possible semester categories to ensure they are always present in the output
#     all_semester_labels = ['Semester 6', 'Semester 8', 'Semester 10', 'Semester 12', 'Semester 14']

#     for prodi in all_prodi_in_data:
#         final_data[prodi] = {}
#         for semester_label in all_semester_labels:
#             final_data[prodi][semester_label] = prodi_semester_counts[prodi][semester_label]

#     return jsonify(final_data)

# ------------------ /api/getdata-all-status (Updated to use helper) ------------------
@app.route('/api/getdata-all-status')
def getdata_all_status():
    all_mahasiswa_list = ALL_MAHASISWA_DATA

    if all_mahasiswa_list is None:
        return jsonify({"status": [], "error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
    if not isinstance(all_mahasiswa_list, list):
        return jsonify({"status": [], "error": "Data mahasiswa tidak valid (bukan list)."}), 500
    if not all_mahasiswa_list:
        return jsonify({"status": []}), 200

    filter_angkatan = request.args.get('angkatan', 'ALL')
    filter_prodi = request.args.get('prodi', 'ALL')

    # Menggunakan fungsi pembantu untuk mendapatkan status yang difilter
    status_set = _get_all_unique_statuses(all_mahasiswa_list, filter_angkatan, filter_prodi)

    return jsonify({"status": status_set})

#button nilai
# @app.route('/dekannilai')
# @role_required(["dekan", "wadek1", "ktu", "kaprodi", "akademik", "admin"])
# def dekan_nilai():
#     return render_template('dekannilai.html')

#==== HALAMAN DEKAN NILAI ====#
@app.route("/dekannilai")
@role_required(["dekan", "wadek1", "ktu", "kaprodi", "akademik", "admin"])
def dekannilai_page():
    return render_template("dekannilai_template.html")

#==== API UNTUK DROPDOWN DATA DI HALAMAN DEKAN NILAI ====#
@app.route("/api/dropdown-data")
def get_dropdown_data():
    try:
        all_data, error = fetch_all_mahasiswa_data()
        if error:
            return jsonify(error), 500 # Return the error from fetch_all_mahasiswa_data
        
        # Ensure all_data is iterable before proceeding
        if not isinstance(all_data, list):
            return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500

        angkatan_set = {str(m.get("tahun_angkatan")) for m in all_data if isinstance(m, dict) and m.get("tahun_angkatan") is not None and m.get("tahun_angkatan") != ""}
        prodi_set = {m.get("nama_program_studi") for m in all_data if isinstance(m, dict) and m.get("nama_program_studi")}
        
        return jsonify({"angkatan": sorted(list(angkatan_set), reverse=True), "prodi": sorted(list(prodi_set))})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

#==== API UNTUK TABEL CHART DATA DI HALAMAN DEKAN NILAI ====#
@app.route("/api/ipk-statistik")
def get_ipk_statistik():
    try:
        all_data, error = fetch_all_mahasiswa_data()
        if error:
            return jsonify(error), 500 # Return the error from fetch_all_mahasiswa_data
        
        if not isinstance(all_data, list):
            return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500

        angkatan_filter = request.args.get("angkatan")
        if angkatan_filter:
            all_data = [m for m in all_data if isinstance(m, dict) and str(m.get("tahun_angkatan")) == angkatan_filter]

        ipk_stats = defaultdict(lambda: {"max": 0, "min": 4, "sum": 0, "count": 0})
        for m in all_data:
            if not isinstance(m, dict):
                continue
            prodi = m.get("nama_program_studi", "TIDAK DIKETAHUI")
            try:
                ipk = float(m.get("ipk", 0))
                if ipk > 0: # Only consider valid IPK
                    stat = ipk_stats[prodi]
                    stat["max"] = max(stat["max"], ipk)
                    stat["min"] = min(stat["min"], ipk)
                    stat["sum"] += ipk
                    stat["count"] += 1
            except (ValueError, TypeError):
                continue # Skip if IPK is not a valid number
        result = []
        for prodi, stat in ipk_stats.items():
            avg = stat["sum"] / stat["count"] if stat["count"] else 0
            result.append({
                "prodi": prodi,
                "ipk_max": round(stat["max"], 2),
                "ipk_min": round(stat["min"], 2),
                "ipk_avg": round(avg, 2)
            })
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

#button nilai sisfo
# @app.route('/dekannilaisisfo')
# def dekan_nilai_sisfo():
#     return render_template('dekan_nilai_S1sisfo.html')

#==== HALAMAN NILAI PER-PRODI====#
@app.route("/<prodi_slug>/")
def prodi_page(prodi_slug):
    print(f"\n--- Backend: prodi_page called with prodi_slug: '{prodi_slug}' ---")
    
    all_mahasiswa_list, error = fetch_all_mahasiswa_data()
    
    # Correct error handling for fetch_all_mahasiswa_data's return
    if error: 
        print(f"  Backend: Error from fetch_all_mahasiswa_data: {error.get('error', 'Unknown error format')}")
        return f"Gagal memuat data mahasiswa: {error.get('error', 'Terjadi kesalahan tidak dikenal saat mengambil data')}", 500

    if not all_mahasiswa_list: 
        print(f"  Backend: No student data available after fetch for slug: '{prodi_slug}'.")
        return "Tidak ada data mahasiswa yang tersedia.", 404
        
    target_prodi_name = None
    expected_db_format = unslugify_to_prodi_name(prodi_slug)
    print(f"  Backend: Expected DB format for '{prodi_slug}': '{expected_db_format}'")

    for m in all_mahasiswa_list: 
        if not isinstance(m, dict):
            print(f"  Backend Warning: Expected dictionary for mahasiswa entry, but got {type(m)}. Skipping.")
            continue 

        db_prodi_name = m.get("nama_program_studi", "")
        if db_prodi_name == expected_db_format:
            target_prodi_name = db_prodi_name
            print(f"  Backend: MATCH FOUND! Target Prodi Name: '{target_prodi_name}'")
            break
    
    if not target_prodi_name:
        print(f"  Backend: No matching program study found for slug: '{prodi_slug}' (Expected DB format: '{expected_db_format}')")
        return "Program studi tidak ditemukan.", 404

    filtered_prodi_data = [m for m in all_mahasiswa_list if m.get("nama_program_studi") == target_prodi_name]
    
    tahun_set = set()
    semester_set = set()
    
    for m in filtered_prodi_data:
        if not isinstance(m, dict):
            continue
        
        nilai_mahasiswa_list = m.get("nilai_mahasiswa", [])
        if not isinstance(nilai_mahasiswa_list, list):
            print(f"  Backend Warning: 'nilai_mahasiswa' for {m.get('nim', 'unknown')} is not a list ({type(nilai_mahasiswa_list)}). Skipping.")
            continue

        for nilai in nilai_mahasiswa_list:
            if not isinstance(nilai, dict):
                print(f"  Backend Warning: Expected dictionary for nilai entry, but got {type(nilai)}. Skipping.")
                continue
            
            if "tahun_akademik" in nilai and nilai["tahun_akademik"]:
                tahun_set.add(nilai["tahun_akademik"])
            if "semester" in nilai and nilai["semester"] is not None:
                semester_set.add(str(nilai["semester"]))
    
    sorted_tahun = sorted(list(tahun_set), reverse=True)
    sorted_semester = sorted(list(semester_set))

    requested_tahun = request.args.get("tahun")
    default_tahun = sorted_tahun[0] if sorted_tahun else None
    selected_periode = requested_tahun if requested_tahun and requested_tahun in sorted_tahun else default_tahun

    requested_semester = request.args.get("semester")
    default_semester = '1' 
    selected_semester = requested_semester if requested_semester and requested_semester in sorted_semester else default_semester
    
    mata_kuliah_set = set()
    if selected_periode and selected_semester:
        for m in filtered_prodi_data:
            if not isinstance(m, dict):
                continue
            
            nilai_mahasiswa_list = m.get("nilai_mahasiswa", [])
            if not isinstance(nilai_mahasiswa_list, list):
                continue

            for nilai in nilai_mahasiswa_list:
                if not isinstance(nilai, dict):
                    continue
                
                if str(nilai.get("tahun_akademik")) == str(selected_periode) and \
                   str(nilai.get("semester")) == str(selected_semester):
                    if "nama_mk" in nilai and nilai["nama_mk"]:
                        mata_kuliah_set.add(nilai["nama_mk"])
    
    print(f"  Backend: Rendering nilai_prodi_template.html for '{target_prodi_name}' (Slug: '{prodi_slug}')")
    return render_template("nilai_prodi_template.html", 
                           prodi_name=target_prodi_name,
                           prodi_slug=prodi_slug,
                           tahun_akademik_list=sorted_tahun,
                           semester_list=sorted_semester,
                           mata_kuliah_list=sorted(list(mata_kuliah_set)), 
                           selected_semester=selected_semester,
                           selected_periode=selected_periode)

#==== API UNTUK DROPDOWN DATA DI HALAMAN NILAI PER-PRODI====#
@app.route("/api/mata-kuliah-by-filter/<prodi_slug>")
def get_mata_kuliah_by_filter_prodi(prodi_slug):
    tahun_akademik = request.args.get("tahun")
    semester = request.args.get("semester")

    if not tahun_akademik or not semester:
        return jsonify([])

    try:
        all_mahasiswa_list, error = fetch_all_mahasiswa_data()
        if error:
            return jsonify(error), 500
        
        target_prodi_name = None
        expected_db_format = unslugify_to_prodi_name(prodi_slug) # Use unslugify here
        for m in all_mahasiswa_list: 
            if isinstance(m, dict) and m.get("nama_program_studi") == expected_db_format: # Compare
                target_prodi_name = m.get("nama_program_studi")
                break
        
        if not target_prodi_name:
            return jsonify({"error": "Program studi tidak ditemukan."}), 404

        filtered_prodi_data = [m for m in all_mahasiswa_list if m.get("nama_program_studi") == target_prodi_name]

        filtered_mata_kuliah = set()
        for m in filtered_prodi_data:
            if not isinstance(m, dict): continue
            for nilai in m.get("nilai_mahasiswa", []):
                if not isinstance(nilai, dict): continue
                if str(nilai.get("tahun_akademik")) == tahun_akademik and \
                   str(nilai.get("semester")) == semester and \
                   nilai.get("nama_mk"):
                    filtered_mata_kuliah.add(nilai["nama_mk"])
        return jsonify(sorted(list(filtered_mata_kuliah)))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Gagal mengambil mata kuliah: {str(e)}"}), 500

#==== API UNTUK TABEL CHART DATA DI HALAMAN NILAI PER-PRODI====#
@app.route("/api/chart-data-nilai/<prodi_slug>")
def get_chart_data_nilai_prodi(prodi_slug):
    periode = request.args.get("periode")
    matkul = request.args.get("matkul")
    semester = request.args.get("semester")

    if not all([periode, matkul, semester]):
        return jsonify({"error": "Parameter periode, matkul, dan semester diperlukan."}), 400

    try:
        all_mahasiswa_list, error = fetch_all_mahasiswa_data()
        if error:
            return jsonify(error), 500

        target_prodi_name = None
        expected_db_format = unslugify_to_prodi_name(prodi_slug) # Use unslugify here
        for m in all_mahasiswa_list: 
            if isinstance(m, dict) and m.get("nama_program_studi") == expected_db_format: # Compare
                target_prodi_name = m.get("nama_program_studi")
                break
        
        if not target_prodi_name:
            return jsonify({"error": "Program studi tidak ditemukan."}), 404

        filtered_prodi_data = [m for m in all_mahasiswa_list if m.get("nama_program_studi") == target_prodi_name]

        nilai_counts_per_kelas = defaultdict(lambda: {h: 0 for h in ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "E"]})
        huruf_labels = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "E"]

        for m in filtered_prodi_data:
            if not isinstance(m, dict): continue
            for nilai in m.get("nilai_mahasiswa", []):
                if not isinstance(nilai, dict): continue
                if str(nilai.get("tahun_akademik")) == periode and \
                   nilai.get("nama_mk") == matkul and \
                   str(nilai.get("semester")) == semester:
                    
                    kelas = m.get("kelas")
                    if not kelas:
                        kelas = nilai.get("kelas", "Tidak diketahui") 

                    nilai_huruf = nilai.get("nilai_huruf")

                    if kelas and nilai_huruf in huruf_labels:
                        nilai_counts_per_kelas[kelas][nilai_huruf] += 1
        
        chart_data = []
        for kelas, counts in sorted(nilai_counts_per_kelas.items()):
            item = {"kelas": kelas}
            item.update(counts)
            chart_data.append(item)

        return jsonify(chart_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Gagal memuat data chart: {str(e)}"}), 500
    
#==== HALAMAN DETAIL NILAI PER-PRODI====#
@app.route("/<prodi_slug>/detail-perolehan-nilai")
def detail_perolehan_nilai_prodi(prodi_slug):
    periode = request.args.get("periode")
    semester = request.args.get("semester")
    matkul = request.args.get("matkul")
    kelas_filter = request.args.get("kelas")

    try:
        all_mahasiswa_list = ALL_MAHASISWA_DATA 
        
        # Check if cache is empty (e.g., if initial fetch failed or is still in progress)
        if all_mahasiswa_list is None:
            # Optionally, you could try to re-fetch here if you want to be super resilient,
            # but per your request, we'll assume it should primarily use the pre-loaded cache.
            # For this scenario, just return an error if the cache is truly empty.
            return "Data mahasiswa belum tersedia. Coba lagi nanti atau periksa koneksi API.", 503 # Service Unavailable

        if not all_mahasiswa_list:
            return "Tidak ada data mahasiswa yang tersedia di cache.", 404
        
        target_prodi_name = None
        expected_db_format = unslugify_to_prodi_name(prodi_slug) 
        
        # Cari nama program studi yang tepat dari data yang di-cache
        # Gunakan lower() untuk perbandingan case-insensitive
        for m in all_mahasiswa_list: 
            if isinstance(m, dict) and m.get("nama_program_studi", "").lower() == expected_db_format.lower(): 
                target_prodi_name = m.get("nama_program_studi")
                break
        
        if not target_prodi_name:
            return "Program studi tidak ditemukan untuk slug ini.", 404

        # Filter data yang di-cache berdasarkan nama program studi
        # Gunakan lower() untuk perbandingan case-insensitive
        filtered_prodi_data = [
            m for m in all_mahasiswa_list 
            if isinstance(m, dict) and m.get("nama_program_studi", "").lower() == target_prodi_name.lower()
        ]

        hasil = []
        nilai_counter = defaultdict(int)
        kelas_tersedia = set()

        for m in filtered_prodi_data:
            if not isinstance(m, dict): continue
            for nilai in m.get("nilai_mahasiswa", []):
                if not isinstance(nilai, dict): continue
                if (
                    str(nilai.get("tahun_akademik")) == periode and
                    str(nilai.get("semester")) == semester and
                    nilai.get("nama_mk") == matkul
                ):
                    kelas = m.get("kelas")
                    if not kelas:
                        kelas = nilai.get("kelas")

                    # Pastikan kelas tidak None atau string kosong sebelum ditambahkan ke set
                    if kelas:
                        kelas_tersedia.add(kelas)

                    if kelas_filter and kelas != kelas_filter:
                        continue

                    huruf = nilai.get("nilai_huruf", "").strip()
                    nilai_counter[huruf] += 1

                    dosen_info = nilai.get("dosen", {})
                    nama_dosen = f"{dosen_info.get('title_depan', '')} {dosen_info.get('nama_dosen', '')} {dosen_info.get('title_belakang', '')}".strip()
                    nama_dosen = ' '.join(nama_dosen.split()) # Menghilangkan spasi ganda

                    hasil.append({
                        "nim": m.get("nim"),
                        "nama": m.get("nama_mahasiswa"),
                        "kelas": kelas,
                        "nilai": huruf,
                        "dosen": nama_dosen
                    })

        total = sum(nilai_counter.values())
        distribusi = []
        nilai_huruf_order = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "E"]
        for grade in nilai_huruf_order:
            jumlah = nilai_counter.get(grade, 0)
            persen = round((jumlah / total) * 100, 2) if total else 0
            distribusi.append({
                "grade": grade,
                "jumlah": jumlah,
                "persen": f"{persen} %"
            })

        return render_template(
            "detail_perolehan_nilai_template.html", 
            mahasiswa=hasil,
            perolehan_nilai=distribusi,
            periode=periode,
            semester=semester,
            matkul=matkul,
            kelas=kelas_filter,
            kelas_list=sorted(list(kelas_tersedia)),
            prodi_name=target_prodi_name, 
            prodi_slug=prodi_slug 
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Gagal memuat data: {e}", 500

#==== HALAMAN DAFTAR MAHASISWA PER-PRODI====#
@app.route("/<prodi_slug>/daftar-mahasiswa")
def daftar_mahasiswa_prodi(prodi_slug):
    try:
        # 1. Read directly from the global cache
        all_mahasiswa_list = ALL_MAHASISWA_DATA 
        
        # Check if cache is empty (e.g., if initial fetch failed or is still in progress)
        if all_mahasiswa_list is None:
            # Optionally, you could try to re-fetch here if you want to be super resilient,
            # but per your request, we'll assume it should primarily use the pre-loaded cache.
            # For this scenario, just return an error if the cache is truly empty.
            return "Data mahasiswa belum tersedia. Coba lagi nanti atau periksa koneksi API.", 503 # Service Unavailable

        if not all_mahasiswa_list:
            return "Tidak ada data mahasiswa yang tersedia di cache.", 404

        target_prodi_name = None
        # Use unslugify to convert the URL slug back to the expected database format for the program study name.
        expected_db_format = unslugify_to_prodi_name(prodi_slug) 
        
        # 2. Find the actual `nama_program_studi` from the cached data
        # Use .lower() for case-insensitive comparison, as unslugify_to_prodi_name now capitalizes each word
        for m in all_mahasiswa_list: 
            if isinstance(m, dict) and m.get("nama_program_studi", "").lower() == expected_db_format.lower(): 
                target_prodi_name = m.get("nama_program_studi")
                break
        
        if not target_prodi_name:
            return "Program studi tidak ditemukan untuk slug ini.", 404

        # 3. Filter the cached data by the determined program study name
        mahasiswa = []
        angkatan_set = set()

        for m in all_mahasiswa_list:
            if not isinstance(m, dict): 
                continue
            # Ensure comparison is robust (case-insensitive)
            if m.get("nama_program_studi", "").lower() != target_prodi_name.lower():
                continue
            
            nim = m.get("nim")
            nama = m.get("nama_mahasiswa")
            angkatan = str(m.get("tahun_angkatan", "-"))
            semester_info = calculate_current_semester(m)

            mahasiswa.append({
                "nim": nim,
                "nama": nama,
                "semester": semester_info,
                "angkatan": angkatan
            })
            angkatan_set.add(angkatan)

        angkatan_list = sorted(list(angkatan_set), reverse=True)

        return render_template("daftar_mahasiswa_template.html", 
                                prodi_name=target_prodi_name, 
                                prodi_slug=prodi_slug, 
                                mahasiswa=mahasiswa,
                                angkatan_list=angkatan_list)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Gagal memuat data: {e}", 500
    
#==== HALAMAN DETAIL MAHASISWA DARI DAFTAR MAHASISWA PER-PRODI====#
@app.route('/<prodi_slug>/detail-mahasiswa/<nim>') 
def detail_mahasiswa(prodi_slug,nim): 
    print("prodi_slug",prodi_slug)
    api_url_mahasiswa = f"{API_BASE_URL}/api/mahasiswa/{nim}"
    
    try:
        response_mahasiswa = requests.get(api_url_mahasiswa)
        response_mahasiswa.raise_for_status()
        api_data_mahasiswa = response_mahasiswa.json()
    except requests.exceptions.RequestException as e:
        print(f"Error mengambil data detail mahasiswa dari API: {e}")
        return "Error saat mengambil data mahasiswa. Pastikan API backend berjalan.", 500
    except ValueError as e: # Catch JSON decoding errors for detail API
        print(f"Error decoding JSON response for detail mahasiswa API: {e}")
        return "Error: Respon API detail mahasiswa tidak valid.", 500

    if not api_data_mahasiswa or not api_data_mahasiswa.get('success') or not api_data_mahasiswa.get('data'):
        return "Data mahasiswa tidak ditemukan atau tidak valid.", 404

    student_api_data = api_data_mahasiswa['data']

    api_url_semester_summary = f"{API_BASE_URL}/api/laporan/semester-summary/{nim}"
    ips_histori_data = []
    try:
        response_ips = requests.get(api_url_semester_summary)
        response_ips.raise_for_status()
        api_data_ips = response_ips.json()
        if api_data_ips.get('success') and api_data_ips.get('data'):
            for item in api_data_ips['data']:
                if isinstance(item, dict): # Add validation here too
                    ips_histori_data.append({
                        'semester': f"{item.get('tahun_akademik')} Semester {item.get('semester')}",
                        'ips': float(item.get('ips', 0.0))
                    })
    except requests.exceptions.RequestException as e:
        print(f"Warning: Error mengambil data IPS histori dari API: {e}")
        pass
    except ValueError as e: # Catch JSON decoding errors for semester summary API
        print(f"Warning: Error decoding JSON response for semester summary API: {e}")
        pass


    raw_tanggal_masuk = student_api_data.get('tanggal_mulai_masuk')
    formatted_tanggal_masuk = 'N/A'
    if raw_tanggal_masuk:
        try:
            dt_object = datetime.fromisoformat(raw_tanggal_masuk.replace('Z', '+00:00'))
            formatted_tanggal_masuk = dt_object.strftime("%d %B %Y")
        except ValueError:
            print(f"Warning: Gagal memparsing tanggal masuk: {raw_tanggal_masuk}")
            formatted_tanggal_masuk = 'Format Tanggal Tidak Valid'

    mahasiswa_for_template = {
        'nama': student_api_data.get('nama_mahasiswa', 'N/A'),
        'nim': student_api_data.get('nim', 'N/A'),
        'semester': calculate_current_semester(student_api_data),
        'prodi': student_api_data.get('nama_program_studi', 'N/A'),
        'alamat': f"{student_api_data.get('kecamatan', '')}, {student_api_data.get('kota_kab', '')}, {student_api_data.get('propinsi', '')}".strip(', '),
        'status_mhs': student_api_data.get('status_mahasiswa_terakhir', 'N/A'),
        'ipk': student_api_data.get('ipk', '-'),
        'tanggal_masuk': formatted_tanggal_masuk,
        'angkatan': student_api_data.get('tahun_angkatan', 'N/A'),
        'ipk_histori': [], 
        'ips_histori': ips_histori_data,
        'nilai_mahasiswa_detail': student_api_data.get('nilai_mahasiswa', []),
        'prodi_slug': prodi_slug 
    }

    overall_grade_counts = defaultdict(int)
    for nilai in mahasiswa_for_template['nilai_mahasiswa_detail']:
        if isinstance(nilai, dict): # Ensure it's a dict
            grade = nilai.get('nilai_huruf')
            if grade:
                overall_grade_counts[grade] += 1

    grade_order = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'E', 'F']
    sorted_grades = sorted(overall_grade_counts.keys(), key=lambda x: grade_order.index(x) if x in grade_order else len(grade_order))

    mahasiswa_for_template['nilai_distribusi_labels'] = sorted_grades
    mahasiswa_for_template['nilai_distribusi_data'] = [overall_grade_counts[grade] for grade in sorted_grades]

    return render_template('detail_mahasiswa_template.html', mahasiswa=mahasiswa_for_template)

#button nilai if
# @app.route('/dekannilaiif')
# def dekan_nilai_if():
#     return render_template('dekan_nilai_S1if.html')

# #button nilai d3
# @app.route('/dekannilaid3')
# def dekan_nilai_d3():
#     return render_template('dekan_nilai_d3.html')

# #button nilai sd
# @app.route('/dekannilaisd')
# def dekan_nilai_sd():
#     return render_template('dekan_nilai_sd.html')

#button help
# @app.route('/help')
# def help():
#     return render_template('help.html')
    

# # Button detail perolehan 
# import random

# import random
# from flask import request, render_template

# # Dosen dan nilai umum
# dosen_map_common = {
#     "Sistem Basis Data": "Dr. Agung Sepriasa, M.Kom",
#     "Pemrograman Berorientasi Objek": "Ir. Dedi Supardi, M.T",
#     "Rekayasa Perangkat Lunak": "Dr. Siti Nurhaliza, M.Kom",
# }

# nilai_map_common = {
#     "A": {"A": 8, "A-": 6, "B+": 4, "B": 4, "C": 3, "D": 2},
#     "B": {"A": 3, "A-": 7, "B+": 6, "B": 5, "C": 4, "E": 1},
#     "C": {"A": 4, "B": 7, "B+": 5, "C": 6, "D": 3, "E": 2},
#     "D": {"A-": 5, "B+": 8, "C": 5, "D": 4},
#     "E": {"A": 1, "B+": 3, "B": 5, "C": 5, "D": 3, "E": 3},
# }


# def generate_data(periode, semester, matkul, kelas, dosen_map, nilai_map):
#     dosen = dosen_map.get(matkul, "Dosen Tidak Diketahui")
#     grade_data = nilai_map.get(kelas, {})
#     total_mhs = sum(grade_data.values())

#     perolehan_nilai = []
#     for grade, jumlah in grade_data.items():
#         persen = f"{(jumlah / total_mhs) * 100:.1f}%"
#         perolehan_nilai.append({
#             "grade": grade,
#             "jumlah": jumlah,
#             "persen": persen
#         })

#     nama_depan = ["Rizki", "Dewi", "Putra", "Siti", "Agus", "Intan", "Bagus", "Lia", "Fajar", "Dian", "Yoga", "Nurul"]
#     nama_belakang = ["Saputra", "Wijaya", "Lestari", "Pratama", "Santoso", "Utami", "Ananda", "Siregar", "Kusuma", "Yuliana"]

#     mahasiswa = []
#     nim_counter = 2310511001
#     for grade in perolehan_nilai:
#         for _ in range(grade["jumlah"]):
#             mahasiswa.append({
#                 "nim": str(nim_counter),
#                 "nama": f"{random.choice(nama_depan)} {random.choice(nama_belakang)}",
#                 "kelas": kelas,
#                 "nilai": grade["grade"],
#                 "dosen": dosen
#             })
#             nim_counter += 1

#     return dosen, perolehan_nilai, mahasiswa


# # S1 Sistem Informasi
# @app.route("/s1sisfo/detail-perolehan-nilai-s1sisfo")
# def detail_perolehan_s1sisfo():
#     periode = request.args.get('periode')
#     semester = request.args.get('semester')
#     matkul = request.args.get('matkul')
#     kelas = request.args.get('kelas', 'A')

#     dosen, perolehan_nilai, mahasiswa = generate_data(
#         periode, semester, matkul, kelas, dosen_map_common, nilai_map_common
#     )

#     return render_template(
#         "detail_perolehan_nilai_s1sisfo.html",
#         periode=periode,
#         semester=semester,
#         matkul=matkul,
#         kelas=kelas,
#         perolehan_nilai=perolehan_nilai,
#         mahasiswa=mahasiswa
#     )


# # S1 Informatika
# @app.route("/s1if/detail-perolehan-nilai-if")
# def detail_perolehan_nilai_if():
#     periode = request.args.get('periode')
#     semester = request.args.get('semester')
#     matkul = request.args.get('matkul')
#     kelas = request.args.get('kelas', 'A')

#     dosen, perolehan_nilai, mahasiswa = generate_data(
#         periode, semester, matkul, kelas, dosen_map_common, nilai_map_common
#     )

#     return render_template(
#         "detail_perolehan_nilai_if.html",
#         periode=periode,
#         semester=semester,
#         matkul=matkul,
#         kelas=kelas,
#         perolehan_nilai=perolehan_nilai,
#         mahasiswa=mahasiswa
#     )


# # D3 Sistem Informasi
# @app.route("/d3sisfo/detail-perolehan-nilai-d3sisfo")
# def detail_perolehan_nilai_d3sisfo():
#     periode = request.args.get('periode')
#     semester = request.args.get('semester')
#     matkul = request.args.get('matkul')
#     kelas = request.args.get('kelas', 'A')

#     dosen, perolehan_nilai, mahasiswa = generate_data(
#         periode, semester, matkul, kelas, dosen_map_common, nilai_map_common
#     )

#     return render_template(
#         "detail_perolehan_nilai_d3.html",
#         periode=periode,
#         semester=semester,
#         matkul=matkul,
#         kelas=kelas,
#         perolehan_nilai=perolehan_nilai,
#         mahasiswa=mahasiswa
#     )


# # S1 Sains Data
# @app.route("/s1sd/detail-perolehan-nilai-s1sd")
# def detail_perolehan_nilai_s1sd():
#     periode = request.args.get('periode')
#     semester = request.args.get('semester')
#     matkul = request.args.get('matkul')
#     kelas = request.args.get('kelas', 'A')

#     dosen, perolehan_nilai, mahasiswa = generate_data(
#         periode, semester, matkul, kelas, dosen_map_common, nilai_map_common
#     )

#     return render_template(
#         "detail_perolehan_nilai_sd.html",
#         periode=periode,
#         semester=semester,
#         matkul=matkul,
#         kelas=kelas,
#         perolehan_nilai=perolehan_nilai,
#         mahasiswa=mahasiswa
#     )

# @app.route("/s1sisfo/detail-perolehan-nilai-s1sisfo")
# def detail_perolehan():
#     periode = request.args.get('periode')
#     semester = request.args.get('semester')
#     matkul = request.args.get('matkul')
#     kelas = request.args.get('kelas', 'A')

#     # Dosen per matkul
#     dosen_pengampu = {
#         "Sistem Basis Data": "Dr. Agung Sepriasa, M.Kom",
#         "Pemrograman Berorientasi Objek": "Ir. Dedi Supardi, M.T",
#         "Rekayasa Perangkat Lunak": "Dr. Siti Nurhaliza, M.Kom",
#         "Analisis dan Perancangan Sistem": "Dra. Fitriani, M.Kom",
#         "Manajemen Proyek TI": "Rizky Maulana, M.Kom",
#     }
#     dosen = dosen_pengampu.get(matkul, "Dosen Tidak Diketahui")

#     # Nilai lengkap
#     nilai_per_kelas = {
#         "A": {"A": 10, "A-": 5, "B+": 7, "B": 4, "C": 2, "D": 2},
#         "B": {"A": 3, "A-": 6, "B+": 8, "B": 7, "C": 5, "E": 1},
#         "C": {"A": 4, "B": 9, "B+": 5, "C": 6, "D": 4, "E": 2},
#         "D": {"A-": 7, "B+": 10, "C": 5, "D": 3},
#         "E": {"A": 2, "B+": 3, "B": 4, "C": 5, "D": 3, "E": 3},
#     }

#     grade_data = nilai_per_kelas.get(kelas, {})
#     total_mhs = sum(grade_data.values())

#     # Format menjadi list of dict dengan persen
#     perolehan_nilai = []
#     for grade, jumlah in grade_data.items():
#         persen = f"{(jumlah / total_mhs) * 100:.1f}%"
#         perolehan_nilai.append({
#             "grade": grade,
#             "jumlah": jumlah,
#             "persen": persen
#         })

#     # Nama dummy generator
#     nama_depan = ["Rizki", "Dewi", "Putra", "Siti", "Agus", "Intan", "Bagus", "Lia", "Fajar", "Dian", "Yoga", "Nurul"]
#     nama_belakang = ["Saputra", "Wijaya", "Lestari", "Pratama", "Santoso", "Utami", "Ananda", "Siregar", "Kusuma", "Yuliana"]

#     mahasiswa = []
#     nim_counter = 2310511001
#     for grade in perolehan_nilai:
#         for _ in range(grade["jumlah"]):
#             mahasiswa.append({
#                 "nim": str(nim_counter),
#                 "nama": f"{random.choice(nama_depan)} {random.choice(nama_belakang)}",
#                 "kelas": kelas,
#                 "nilai": grade["grade"],
#                 "dosen": dosen
#             })
#             nim_counter += 1

#     return render_template(
#         "detail_perolehan_nilai_s1sisfo.html",
#         periode=periode,
#         semester=semester,
#         matkul=matkul,
#         kelas=kelas,
#         perolehan_nilai=perolehan_nilai,
#         mahasiswa=mahasiswa
#     )

# # Button detail perolehan nilai informatika
# @app.route('/s1if/detail-perolehan-nilai-if')
# def detail_perolehan_nilai_if():
#     return render_template('detail_perolehan_nilai_if.html')

# # Button detail perolehan nilai d3sisfo
# @app.route('/d3sisfo/detail-perolehan-nilai-d3sisfo')
# def detail_perolehan_nilai_d3sisfo():
#     return render_template('detail_perolehan_nilai_d3.html')

# # Button detail perolehan nilai s1sd
# @app.route('/s1sd/detail-perolehan-nilai-s1sd')
# def detail_perolehan_nilai_s1sd():
#     return render_template('detail_perolehan_nilai_sd.html')

# get data untuk

#button lihat selengkapnya (UKT Belum Bayar)
# @app.route('/detailbelumbayar')
# def detail_belumbayar():
#     return render_template('dekandetail_belumbayarukt.html')

# @app.route('/detailtunggakan')
# def detail_tunggakan():
#     return render_template('dekandetail_tunggakanaktifnon.html')

@app.route('/detailKIPK')
def detail_kipk():
    return render_template('dekandetail_KIPK.html')

@app.route('/detailpengajuan')
def detail_pengajuan():
    return render_template('dekandetail_pengajuan.html')

# @app.route('/detailaktifnon')
# def detail_aktifnon():
#     return render_template('dekan_stat_detail_aktifnon.html')

@app.route('/detailaktifnon')
def detail_aktif_non_page():
    return render_template("dekan_stat_detail_aktifnon_copy.html")

# ------------------ /api/getdata-aktif-nonaktif ------------------
@app.route('/api/getdata-aktif-nonaktif')
def getdata_aktif_nonaktif():
    angkatan_filter = request.args.get('angkatan', 'ALL')
    prodi_filter = request.args.get('prodi', 'ALL') # Meskipun prodi=ALL akan selalu dikirim dari frontend

    all_mahasiswa_list = ALL_MAHASISWA_DATA
    if all_mahasiswa_list is None:
        return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
    if not isinstance(all_mahasiswa_list, list):
        return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
    
    # Kumpulkan semua prodi unik dari data mahasiswa yang tersedia
    # Hanya prodi yang memiliki status 'AKTIF' atau 'NON-AKTIF' akan dipertimbangkan
    all_known_prodi = sorted(list(set(
        m.get('nama_program_studi') for m in all_mahasiswa_list
        if m.get('nama_program_studi') and m.get('status_mahasiswa_terakhir', '').upper() in ['AKTIF', 'NON-AKTIF']
    )))

    if not all_mahasiswa_list:
        # Mengembalikan objek kosong jika tidak ada data mahasiswa sama sekali
        return jsonify({}), 200

    # Menggunakan defaultdict untuk menyimpan hitungan aktif dan non-aktif per prodi
    prodi_status_counts = defaultdict(lambda: {"aktif": 0, "non_aktif": 0})

    for m in all_mahasiswa_list:
        angkatan = m.get('tahun_angkatan')
        prodi = m.get('nama_program_studi')
        status = m.get('status_mahasiswa_terakhir', '').upper()

        # Filter berdasarkan angkatan jika tidak 'ALL'
        if angkatan_filter != 'ALL' and angkatan != angkatan_filter:
            continue

        # Filter berdasarkan prodi jika tidak 'ALL' (meskipun frontend akan selalu kirim 'ALL')
        if prodi_filter != 'ALL' and prodi != prodi_filter:
            continue

        if prodi: # Pastikan prodi tidak None
            if status == 'AKTIF':
                prodi_status_counts[prodi]["aktif"] += 1
            elif status == 'NON-AKTIF': # Hanya hitung 'NON-AKTIF' secara eksplisit
                prodi_status_counts[prodi]["non_aktif"] += 1
    
    # Memastikan semua prodi yang ditemukan ada di output, meskipun nilainya 0
    final_data = {}
    for prodi_name in all_known_prodi: # Iterasi melalui daftar prodi yang ditemukan secara dinamis
        final_data[prodi_name] = {
            "aktif": prodi_status_counts[prodi_name]["aktif"],
            "non_aktif": prodi_status_counts[prodi_name]["non_aktif"]
        }
    
    return jsonify(final_data)

@app.route('/api/mahasiswa-aktif-nonaktif')
def get_mahasiswa_aktif_nonaktif():
    all_mahasiswa_list = ALL_MAHASISWA_DATA

    if all_mahasiswa_list is None:
        return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
    if not isinstance(all_mahasiswa_list, list):
        return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
    if not all_mahasiswa_list:
        return jsonify([]), 200
    
    # Filter data to include only 'AKTIF' or 'NON-AKTIF' status
    filtered_mahasiswa = [
        m for m in all_mahasiswa_list
        if m.get('status_mahasiswa_terakhir', '').upper() in ['AKTIF', 'NON-AKTIF']
    ]
    
    return jsonify(filtered_mahasiswa)

@app.route('/api/mahasiswa-detail/<nim>') # Menjadikan ini endpoint API
def get_mahasiswa_detail(nim): # Mengubah nama fungsi agar lebih sesuai sebagai endpoint API
    api_url_mahasiswa = f"{API_BASE_URL}/api/mahasiswa/{nim}"
    
    try:
        response_mahasiswa = requests.get(api_url_mahasiswa)
        response_mahasiswa.raise_for_status()
        api_data_mahasiswa = response_mahasiswa.json()
    except requests.exceptions.RequestException as e:
        print(f"Error mengambil data detail mahasiswa dari API: {e}")
        return jsonify({"error": "Error saat mengambil data mahasiswa. Pastikan API backend berjalan."}), 500
    except ValueError as e:
        print(f"Error decoding JSON response for detail mahasiswa API: {e}")
        return jsonify({"error": "Error: Respon API detail mahasiswa tidak valid."}), 500

    if not api_data_mahasiswa or not api_data_mahasiswa.get('success') or not api_data_mahasiswa.get('data'):
        return jsonify({"error": "Data mahasiswa tidak ditemukan atau tidak valid."}), 404

    student_api_data = api_data_mahasiswa['data']

    raw_tanggal_masuk = student_api_data.get('tahun_angkatan')
    formatted_tanggal_masuk = 'N/A'
    if raw_tanggal_masuk:
        try:
            dt_object = datetime.fromisoformat(raw_tanggal_masuk.replace('Z', '+00:00'))
            formatted_tanggal_masuk = dt_object.strftime("%d %B %Y")
        except ValueError:
            print(f"Warning: Gagal memparsing tanggal masuk: {raw_tanggal_masuk}")
            formatted_tanggal_masuk = 'Format Tanggal Tidak Valid'

    mahasiswa_for_response = { # Mengubah nama variabel agar lebih jelas
        'nama': student_api_data.get('nama_mahasiswa', 'N/A'),
        'nim': student_api_data.get('nim', 'N/A'),
        'semester': calculate_current_semester_for_status_mhs(student_api_data.get('tahun_angkatan')),
        'prodi': student_api_data.get('nama_program_studi', 'N/A'),
        'alamat': f"{student_api_data.get('kecamatan', '')}, {student_api_data.get('kota_kab', '')}, {student_api_data.get('propinsi', '')}".strip(', '),
        'status_mhs': student_api_data.get('status_mahasiswa_terakhir', 'N/A'),
        'ipk': student_api_data.get('ipk', '-'),
        'tanggal_masuk': formatted_tanggal_masuk,
        'angkatan': student_api_data.get('tahun_angkatan', 'N/A'),
    }

    return jsonify(mahasiswa_for_response) # Mengembalikan JSON

# @app.route('/detaildokeluar')
# def detail_dokeluar():
#     return render_template('dekan_stat_detail_DOKeluar.html')

# @app.route('/detailajuancuti')
# def detail_ajuancuti():
#     return render_template('dekan_stat_detail_pengajuan.html')
@app.route('/detailajuancuti')
def detail_ajuancuti_page():
    # Ini akan merender template untuk daftar cuti
    return render_template("dekan_stat_detail_cuti.html") # Merender file HTML baru

@app.route('/api/mahasiswa-cuti')
def get_mahasiswa_cuti(): # Renamed function
    all_mahasiswa_list = ALL_MAHASISWA_DATA

    if all_mahasiswa_list is None:
        return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
    if not isinstance(all_mahasiswa_list, list):
        return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
    if not all_mahasiswa_list:
        return jsonify([]), 200

    result = [
        m for m in all_mahasiswa_list
        if m.get('status_mahasiswa_terakhir', '').upper() == 'CUTI'
    ]
    return jsonify(result)

# @app.route('/detaillebihperiode')
# def detail_lebihperiode():
#     return render_template('dekan_stat_detail_lebihperiode.html')

@app.route('/dekanstatdetaillebihperiode')
def dekanstatdetaillebihperiode_page():
    # Ini akan merender template untuk daftar mahasiswa yang melebihi masa periode
    return render_template("dekan_stat_detail_lebihperiode_copy.html")

# ------------------ /api/getdata-melebihi-masa-periode ------------------
# @app.route('/api/mahasiswa-melebihi-periode')
# def getdata_melebihi_masa_periode():
#     # Mengambil data mahasiswa dari cache atau sumber data Anda
#     # Pastikan ALL_MAHASISWA_DATA tersedia di konteks aplikasi Anda
#     all_mahasiswa_list = ALL_MAHASISWA_DATA

#     if all_mahasiswa_list is None:
#         return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
#     if not isinstance(all_mahasiswa_list, list):
#         return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
    
#     # Kumpulkan semua prodi unik dari data mahasiswa yang tersedia
#     # Hanya prodi yang memiliki status 'AKTIF' dan melebihi masa periode akan dipertimbangkan
#     all_known_prodi = sorted(list(set(
#         m.get('nama_program_studi') for m in all_mahasiswa_list
#         if m.get('nama_program_studi') and m.get('status_mahasiswa_terakhir', '').upper() == 'AKTIF'
#     )))

#     # Define all possible semester categories to ensure they are always present in the output
#     all_semester_labels = ['Semester 8', 'Semester 10', 'Semester 12', 'Semester 14']

#     if not all_mahasiswa_list:
#         # Mengembalikan objek kosong jika tidak ada data mahasiswa sama sekali
#         return jsonify({}), 200

#     # Batas semester normal untuk setiap program studi
#     # Mahasiswa melebihi batas ini dianggap 'melebihi masa studi normal'
#     normal_study_limits = {
#         'S1 Sistem Informasi': 8, # Normal 4 tahun = 8 semester
#         'S1 Informatika': 8,     # Normal 4 tahun = 8 semester
#         'S1 Sains Data': 8,      # Normal 4 tahun = 8 semester
#         'DIII Sistem Informasi': 6 # Normal 3 tahun = 6 semester (Diperbarui ke DIII)
#     }

#     # Menggunakan defaultdict untuk menyimpan hitungan per prodi dan per kategori semester
#     # prodi_semester_counts = { "ProdiA": { "Semester6": X, "Semester8": Y, ... }, "ProdiB": { ... } }
#     prodi_semester_counts = defaultdict(lambda: defaultdict(int))

#     # Kategori semester untuk pengelompokan mahasiswa yang melebihi masa studi
#     # Berdasarkan semester aktual mereka saat ini
#     semester_categories = {
#         'Semester 8': lambda s: s >= 7 and s < 9,  # Mahasiswa di semester 7 atau 8
#         'Semester 10': lambda s: s >= 9 and s < 11, # Mahasiswa di semester 9 atau 10
#         'Semester 12': lambda s: s >= 11 and s < 13, # Mahasiswa di semester 11 atau 12
#         'Semester 14': lambda s: s >= 13 and s < 15, # Mahasiswa di semester 13 atau 14
#     }

#     for m in all_mahasiswa_list:
#         angkatan = m.get('tahun_angkatan')
#         prodi = m.get('nama_program_studi')
#         status = m.get('status_mahasiswa_terakhir', '').upper()

#         # Hanya pertimbangkan mahasiswa aktif dengan data angkatan dan prodi yang valid
#         if angkatan and prodi and status == 'AKTIF':
#             current_semester = calculate_current_semester_for_status_mhs(angkatan)
#             normal_limit = normal_study_limits.get(prodi)

#             # Pastikan prodi ada di normal_study_limits dan mahasiswa melebihi batas normal
#             if normal_limit is not None and current_semester > normal_limit:
#                 # Menentukan kategori semester mahasiswa
#                 for category_name, condition_func in semester_categories.items():
#                     if condition_func(current_semester): # Pass only 's' (current_semester)
#                         prodi_semester_counts[prodi][category_name] += 1
#                         break # Setelah menemukan kategori yang cocok, keluar dari loop kategori

#     # Mengonversi defaultdict ke dict biasa untuk jsonify
#     # Dan memastikan semua prodi yang ditemukan ada di output, meskipun nilainya 0
#     final_data = {}
#     for prodi in all_known_prodi: # Iterasi melalui daftar prodi yang ditemukan secara dinamis
#         final_data[prodi] = {}
#         for semester_label in all_semester_labels:
#             final_data[prodi][semester_label] = prodi_semester_counts[prodi][semester_label]

#     return jsonify(final_data)

# ------------------ /api/mahasiswa-melebihi-periode ------------------
@app.route('/api/mahasiswa-melebihi-periode')
def get_mahasiswa_melebihi_periode(): # Nama fungsi diubah
    all_mahasiswa_list =  ALL_MAHASISWA_DATA

    if all_mahasiswa_list is None:
        return jsonify({"error": "Data mahasiswa belum tersedia. Cache kosong."}), 503
    if not isinstance(all_mahasiswa_list, list):
        return jsonify({"error": "Data mahasiswa tidak valid (bukan list)."}), 500
    if not all_mahasiswa_list:
        return jsonify([]), 200

    normal_study_limits = {
        'S1 Sistem Informasi': 8,
        'S1 Informatika': 8,
        'S1 Sains Data': 8,
        'DIII Sistem Informasi': 6 # Diperbarui ke DIII
    }

    mahasiswa_melebihi_periode = []
    for mhs in all_mahasiswa_list:
        angkatan = mhs.get('tahun_angkatan')
        prodi = mhs.get('nama_program_studi')
        status = mhs.get('status_mahasiswa_terakhir', '').upper()

        # Hanya pertimbangkan mahasiswa AKTIF untuk pemeriksaan ini
        if angkatan and prodi and status == 'AKTIF':
            semester_saat_ini = calculate_current_semester_for_status_mhs(angkatan)
            
            # Ambil batas semester normal untuk prodi ini, default ke 14 jika tidak ditemukan
            # Menggunakan .get() untuk menangani prodi yang mungkin tidak ada di batas_semester_normal
            batas_prodi = normal_study_limits.get(prodi, 14) 
            
            # Periksa jika semester saat ini valid dan melebihi batas
            # Asumsi calculate_current_semester_for_status_mhs mengembalikan angka atau 0
            if semester_saat_ini > batas_prodi:
                mahasiswa_melebihi_periode.append(mhs)
    
    return jsonify(mahasiswa_melebihi_periode)


# # Menu Nilai
# #button S1 Sistem Informasi
# @app.route('/s1sisfo')
# def s1sisfo():
#     return render_template('nilai_sisfo.html')

# #button S1 Informatika
# @app.route('/s1if')
# def s1if():
#     return render_template('nilai_if.html')

# #button D3 Sistem Informasi
# @app.route('/d3sisfo')
# def d3sisfo():
#     return render_template('nilai_d3.html')

# #button S1 Sains Data
# @app.route('/s1sd')
# def s1sd():
#     return render_template('nilai_sd.html')

# #button S1 Sistem Informasi
# @app.route('/detailsisfo')
# def s1sisfodetail():
#     return render_template('detail_nilai_sisfo.html')

# #button S1 Informatika
# @app.route('/detailif')
# def s1ifdetail():
#     return render_template('detail_nilai_if.html')

# #button D3 Sistem Informasi
# @app.route('/detaild3')
# def d3sisfodetail():
#     return render_template('detail_nilai_d3.html')

# #button S1 Sains Data
# @app.route('/detailsd')
# def s1sainsdatadetail():
#     return render_template('detail_nilai_sd.html')

#LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash("Anda berhasil logout", "success")
    return redirect(url_for('index'))

# @app.route('/predict_next', methods=['GET'])
# def predict_next():
#     # Data input untuk prediksi (contoh: historis mahasiswa aktif)
#     input_data = [450, 350, 400, 500, 300]

#     try:
#         # Prediksi mahasiswa aktif menggunakan model
#         pred_aktif = int(predict_with_xgboost(input_data))

#         # Dummy prediksi mahasiswa non-aktif (misal, 20% dari total mahasiswa aktif)
#         pred_nonaktif = int(0.2 * pred_aktif)

#         # Tentukan tahun berikutnya berdasarkan tahun terakhir dalam input data
#         next_year = "2025/2026"  # Tahun prediksi berikutnya

#         # Struktur JSON untuk dikirimkan ke client
#         data = {
#             'next_year': next_year,
#             'aktif': pred_aktif,
#             'nonaktif': pred_nonaktif
#         }

#         app.logger.info(f"Data prediksi: {data}")  # Log data prediksi
#         return jsonify(data)

#     except Exception as e:
#         app.logger.error(f"Error during prediction: {e}")
#         return jsonify({'error': str(e)})
    
# @app.route('/detailsisfo/<nim>')
# def detail_sisfo(nim):
#     data_mahasiswa = {
#         "2110512013": {
#             "nama": "Divasya Valentiaji",
#             "nim": "2110512013",
#             "prodi": "S1 Sistem Informasi",
#             "semester": "7",
#             "alamat": "Jalan Kenangan Indah Blok QQ1, Pasar Selasa",
#             "email": "2110512013@mahasiswa.upnvj.ac.id",
#             "telp": "089572761098",
#             "status_mhs": "Tidak Aktif"
#         },
#         "2210511037": {
#             "nama": "Cecilia Isadora Hutagalung",
#             "nim": "2210511037",
#             "prodi": "S1 Informatika",
#             "semester": "5",
#             "alamat": "Jalan Aku Mau Turu Tuhan Blok P15",
#             "email": "22210511037@mahasiswa.upnvj.ac.id",
#             "telp": "082222222222",
#             "status_mhs": "Aktif",
#             "golongan": "7",
#             "ukt": "Rp 8.100.000",
#             "status": "Cicilan UKT"
#         }
#     }

#     # Cek apakah NIM ada dalam data mahasiswa
#     mahasiswa = data_mahasiswa.get(nim)

#     if mahasiswa:
#         return render_template('detail_nilai_sisfo.html', mahasiswa=mahasiswa)
#     else:
#         return "Mahasiswa tidak ditemukan", 404
    
# API REQUEST
# 1. DEKAN UKT
from routes.ukt_routes import ukt_bp
app.register_blueprint(ukt_bp)

# 2. DETAIL BELUM BAYAR
from routes.detail_belumbayarukt import belumbayar_bp
app.register_blueprint(belumbayar_bp)

# 3. DETAIL BELUM BAYAR
from routes.detail_tunggakan import tunggakan_bp
app.register_blueprint(tunggakan_bp)
    
# 2. STATUS MAHASISWA
from routes.statmhs_routes import statmhs_bp
app.register_blueprint(statmhs_bp)

# 3. NILAI MAHASISWA

# keseluruhan
from routes.nilai_routes import nilai_bp
app.register_blueprint(nilai_bp)

#diagram sisfo
from routes.nilai_sisfo import nilaisisfo_bp
app.register_blueprint(nilaisisfo_bp)


# DETAIL MAHASISWA S1 SISTEM INFORMASI (INI DI DEKAN_NILAI_S1SISFO.HTML)
from routes.detail_mahasiswa_S1sisfo_routes import sisfo_bp
app.register_blueprint(sisfo_bp)

# DETAIL MAHASISWA S1 INFORMATIKA (INI DI DEKAN_NILAI_S1IF.HTML)
from routes.detail_mahasiswa_IF_routes import if_bp
app.register_blueprint(if_bp)

# DETAIL MAHASISWA D3 SISTEM INFORMASI (INI DI DEKAN_NILAI_D3.HTML)
from routes.detail_mahasiswa_D3_routes import d3_bp
app.register_blueprint(d3_bp)

# DETAIL MAHASISWA S1 SAINS DATA (INI DI DEKAN_NILAI_SD.HTML)
from routes.detail_mahasiswa_sainsdata_routes import sainsdata_bp
app.register_blueprint(sainsdata_bp)

# 4. KRS MAHASISWA
# HALAMAN DEPAN
from routes.krs_routes import krs_bp
app.register_blueprint(krs_bp)

#DETAIL TABEL MAHASISWA BELUM ISI KRS
from routes.detail_mahasiswa_tidak_isi_krs import detail_krs_bp
app.register_blueprint(detail_krs_bp)

# from flask import Flask, render_template, jsonify
# import requests
# import base64
# from datetime import datetime

# # Fungsi Basic Auth
# def basic_auth(username, password):
#     token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
#     return f"Basic {token}"

# # Konfigurasi API
# API_URL = "https://api.upnvj.ac.id/data/list_mahasiswa"
# USERNAME = "uakademik"
# PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
# API_KEY = "X-UPNVJ-API-KEY"
# API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

# # ID Prodi S1 Sistem Informasi (sesuai sistem)
# NAMA_PRODI = "S1 SISTEM INFORMASI"

# @app.route('/dekannilaisisfo')
# def dekan_nilai_sisfo():
#     return render_template('dekan_nilai_S1sisfo.html')

# @app.route('/api/mahasiswa-sisfo', methods=['GET'])
# def api_mahasiswa_sisfo():
#     import requests
#     import base64
#     from datetime import datetime

#     tahun_sekarang = datetime.now().year
#     angkatan_list = [str(tahun) for tahun in range(2018, tahun_sekarang + 1)]
#     bulan_sekarang = datetime.now().month

#     USERNAME = "uakademik"
#     PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
#     API_KEY = "X-UPNVJ-API-KEY"
#     API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"
#     ID_PRODI_SISFO = 4  # berdasarkan contoh respons JSON

#     def basic_auth(username, password):
#         token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
#         return f'Basic {token}'

#     headers = {
#         "API_KEY_NAME": API_KEY,
#         "API_KEY_SECRET": API_SECRET,
#         "Accept": "application/json",
#         "Authorization": basic_auth(USERNAME, PASSWORD),
#     }

#     result_data = []

#     for angkatan in angkatan_list:
#         try:
#             response = requests.post(
#                 "https://api.upnvj.ac.id/data/list_mahasiswa",
#                 data={"angkatan": angkatan},
#                 headers=headers
#             )
#             response.raise_for_status()
#             data = response.json().get("data", [])

#             for mhs in data:
#                 if (
#                     int(mhs.get("id_program_studi", -1)) == ID_PRODI_SISFO and
#                     mhs.get("status_mahasiswa_terakhir", "").strip().upper() == "AKTIF"
#                 ):
#                     tahun_masuk = int(mhs.get("tahun_angkatan", angkatan))
#                     jumlah_tahun = tahun_sekarang - tahun_masuk
#                     semester = jumlah_tahun * 2 + (1 if 2 <= bulan_sekarang <= 7 else 2)

#                     result_data.append({
#                         "nim": mhs.get("nim"),
#                         "nama": mhs.get("nama_mahasiswa"),
#                         "angkatan": str(tahun_masuk),
#                         "semester": semester
#                     })
#         except Exception as e:
#             print(f"Gagal ambil data angkatan {angkatan}: {e}")

#     return jsonify(result_data)

# # DETAIL MAHASISWA BESERTA DENGAN GRAFIKNYA

# # 1. Nama dan ipk mahasiswanya
# from flask import Flask, jsonify, render_template, request
# from datetime import datetime
# import base64
# import requests

# # AUTH CONFIG
# def basic_auth(username, password):
#     token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
#     return f'Basic {token}'

# API_BIODATA = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'
# API_HISTORI = 'https://api.upnvj.ac.id/data/list_histori_mahasiswa'
# USERNAME = "uakademik"
# PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
# API_KEY = "X-UPNVJ-API-KEY"
# API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

# HEADERS = {
#     "API_KEY_NAME": API_KEY,
#     "API_KEY_SECRET": API_SECRET,
#     "Accept": 'application/json',
#     "Authorization": basic_auth(USERNAME, PASSWORD),
# }

# # Endpoint untuk menampilkan detail mahasiswa
# @app.route('/detailnilaisisfo/<nim>')
# def detail_mahasiswa(nim):
#     try:
#         # Ambil biodata mahasiswa menggunakan API
#         bio_resp = requests.post(API_BIODATA, data={"nim": nim}, headers=HEADERS)
#         bio_data = bio_resp.json().get("data", {}) if bio_resp.status_code == 200 else {}

#         # Hitung semester berdasarkan tahun masuk
#         angkatan = int(bio_data.get("angkatan", 0))
#         now = datetime.now()
#         tahun_sekarang = now.year
#         bulan = now.month
#         semester_now = ((tahun_sekarang - angkatan) * 2) - (0 if bulan < 8 else -1)

#         # Ambil histori akademik mahasiswa
#         histori = []
#         for semester in range(1, semester_now + 1):
#             id_periode = f"{angkatan}{1 if semester % 2 != 0 else 2}"  # 1 untuk ganjil, 2 untuk genap
#             resp = requests.post(API_HISTORI, data={"nim": nim, "id_periode": id_periode}, headers=HEADERS)
#             if resp.status_code == 200 and resp.json().get("data"):
#                 entry = resp.json()["data"][0]
#                 histori.append({
#                     "semester": f"Semester {semester}",
#                     "ips": float(entry.get("ips", 0)),
#                     "ipk": float(entry.get("ipk", 0)) if entry.get("ipk") else None
#                 })

#         # Format alamat dari data
#         alamat = ", ".join(filter(None, [
#             bio_data.get("kelurahan", ""),
#             bio_data.get("kecamatan", ""),
#             bio_data.get("kotakab", ""),
#             bio_data.get("propinsi", "")
#         ]))

#         # Render template dengan data mahasiswa dan histori IPK
#         return render_template("detail_nilai_sisfo.html", mahasiswa={
#             "nama": bio_data.get("nama", "-"),
#             "nim": bio_data.get("nim", "-"),
#             "semester": bio_data.get("semester_mahasiswa", "-"),
#             "prodi": bio_data.get("nama_program_studi", "-"),
#             "alamat": alamat,
#             "status_mhs": bio_data.get("status", "-"),
#             "ipk_histori": histori  # Data histori IPK yang akan digunakan untuk grafik
#         })

#     except Exception as e:
#         return f"Terjadi kesalahan: {str(e)}", 500

# CONNECTION POSTGRESQL
# def get_connection():
#     return psycopg2.connect(
#         dbname="dashboard",         # Ganti dengan nama database kamu
#         user="postgres",            # Ganti dengan user PostgreSQL kamu
#         password="admin123",        # Ganti dengan password user PostgreSQL kamu
#         host="localhost",           # Tetap 'localhost' jika lokal
#         port="5432"                 # Port default PostgreSQL
#     )

if __name__ == '__main__':
    app.run(debug=True)