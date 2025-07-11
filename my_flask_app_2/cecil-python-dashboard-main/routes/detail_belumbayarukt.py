from flask import Blueprint, render_template, request
import pandas as pd
import os
import base64
import requests
import time

belumbayar_bp = Blueprint('belumbayar_bp', __name__)

# === Konfigurasi API Biodata ===
API_BIODATA_URL = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

# === Helper Basic Auth ===
def basic_auth(username, password):
    token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

# === Header Lengkap ===
HEADERS = {
    "X-UPNVJ-API-KEY": API_SECRET,
    "Accept": "application/json",
    "Authorization": basic_auth(USERNAME, PASSWORD),
    "User-Agent": "Thunder Client (https://www.thunderclient.com)"
}

# === Global Cache ===
BELUM_BAYAR_CACHE = None
BELUM_BAYAR_LAST_FETCH = 0
CACHE_DURATION_SECONDS = 600  # 10 menit
BIODATA_CACHE = {}  # key: NIM, value: biodata dict


@belumbayar_bp.route('/detail-belum-bayar')
def detail_belum_bayar():
    global BELUM_BAYAR_CACHE, BELUM_BAYAR_LAST_FETCH, BIODATA_CACHE

    try:
        # Ambil parameter dari query string
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 15))

        now = time.time()
        if BELUM_BAYAR_CACHE is not None and (now - BELUM_BAYAR_LAST_FETCH) < CACHE_DURATION_SECONDS:
            grouped = BELUM_BAYAR_CACHE["grouped"]
            tahun_list = BELUM_BAYAR_CACHE["tahun_list"]
            print("[INFO] Menggunakan cache data CSV.")
        else:
            print("[INFO] Membaca ulang CSV dan memproses...")
            file_path = os.path.join('static', 'Rincian_per_mhs.csv')
            df = pd.read_csv(file_path)

            # Preprocessing
            df['Tunggakan'] = df['Tunggakan'].astype(str).str.strip()
            df['Tahun Akademik'] = df['Tahun Akademik'].astype(str).str.strip()
            df['Total Tunggakan'] = df['Total Tunggakan'].astype(str).str.replace(r'[^0-9]', '', regex=True).astype(float)

            df_ukt = df[df['Tunggakan'] == 'UKT'].copy()
            if df_ukt.empty:
                return "Tidak ada data UKT.", 404

            grouped = df_ukt.groupby(['NIM', 'Tahun Akademik']).agg({
                'Nama': 'first',
                'Program Studi': 'first',
                'Status Akademik': 'first',
                'Total Tunggakan': 'sum'
            }).reset_index()

            tahun_list = sorted(grouped['Tahun Akademik'].dropna().unique())

            # Simpan ke cache
            BELUM_BAYAR_CACHE = {
                "grouped": grouped,
                "tahun_list": tahun_list
            }
            BELUM_BAYAR_LAST_FETCH = now

        # Proses biodata dan gabung ke data
        enriched_data = []
        for _, row in grouped.iterrows():
            nim = row['NIM']

            # Cek cache biodata
            if nim in BIODATA_CACHE:
                bio = BIODATA_CACHE[nim]
            else:
                try:
                    res = requests.post(API_BIODATA_URL, data={"nim": nim}, headers=HEADERS)
                    if res.status_code == 200:
                        bio = res.json().get("data", {})
                        if not bio:
                            print(f"[WARN] Biodata kosong untuk NIM {nim}")
                    else:
                        print(f"[ERROR] Gagal ambil biodata {nim}: status {res.status_code}")
                        bio = {}
                except Exception as e:
                    print(f"[ERROR] Gagal ambil biodata {nim}: {e}")
                    bio = {}

                BIODATA_CACHE[nim] = bio

            alamat = f"{bio.get('kelurahan', '')}, {bio.get('kecamatan', '')}, {bio.get('kotakab', '')}, {bio.get('propinsi', '')}".strip(', ')
            email = bio.get("email", "-")
            telp = bio.get("hp", "-")

            enriched_data.append({
                'Tahun Akademik': row['Tahun Akademik'],
                'NIM': nim,
                'Nama': row['Nama'],
                'Program Studi': row['Program Studi'],
                'Status Akademik': row['Status Akademik'],
                'Total Tunggakan': int(row['Total Tunggakan']),
                'Alamat': alamat if alamat.strip(', ') else "-",
                'Email': email,
                'Telp': telp
            })

        # Pagination
        total_data = len(enriched_data)
        total_pages = (total_data + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = enriched_data[start:end]

        return render_template(
            'dekandetail_belumbayarukt.html',
            data=paginated_data,
            tahun_list=tahun_list,
            total_data=total_data,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    except Exception as e:
        print(f"[ERROR] {e}")
        return f"Error: {e}", 500
