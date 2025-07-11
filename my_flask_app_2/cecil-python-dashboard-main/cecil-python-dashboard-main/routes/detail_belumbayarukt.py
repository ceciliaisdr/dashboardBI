from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import os
import base64
import requests
import time
import re # Import re for regex in replace

belumbayar_bp = Blueprint('belumbayar_bp', __name__)

# === Global Auth & API Configuration ===
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"
API_BIODATA_URL = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'

def get_basic_auth_header(USERNAME,PASSWORD):
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

COMMON_HEADERS = {
    "X-UPNVJ-API-KEY": API_SECRET,
    "Accept": 'application/json',
    "Authorization": get_basic_auth_header(USERNAME,PASSWORD),
    "User-Agent": "Thunder Client (https://www.thunderclient.com)"
}

# === Global Cache ===
BELUM_BAYAR_CACHE = None
BELUM_BAYAR_LAST_FETCH = 0
CACHE_DURATION_SECONDS = 600  # 10 minutes

BIODATA_CACHE = {}  # key: NIM, value: biodata dict

@belumbayar_bp.route('/detail-belum-bayar')
def detail_belum_bayar():
    global BELUM_BAYAR_CACHE, BELUM_BAYAR_LAST_FETCH, BIODATA_CACHE

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 15))
        
        now = time.time()
        if BELUM_BAYAR_CACHE is not None and (now - BELUM_BAYAR_LAST_FETCH) < CACHE_DURATION_SECONDS:
            grouped = BELUM_BAYAR_CACHE["grouped"]
            tahun_list = BELUM_BAYAR_CACHE["tahun_list"]
            print("[INFO] Using cached CSV data.")
        else:
            print("[INFO] Re-reading and processing CSV...")
            file_path = os.path.join('static', 'Rincian_per_mhs.csv')
            
            if not os.path.exists(file_path):
                return "CSV file not found.", 404

            df = pd.read_csv(file_path)

            # Preprocessing
            df['Tunggakan'] = df['Tunggakan'].astype(str).str.strip()
            df['Tahun Akademik'] = df['Tahun Akademik'].astype(str).str.strip()
            # Ensure 'Total Tunggakan' is handled for non-numeric values
            df['Total Tunggakan'] = df['Total Tunggakan'].astype(str).str.replace(r'[^\d]', '', regex=True)
            df['Total Tunggakan'] = pd.to_numeric(df['Total Tunggakan'], errors='coerce').fillna(0) # Convert to numeric, handle errors
            
            df_ukt = df[df['Tunggakan'] == 'UKT'].copy()
            if df_ukt.empty:
                # Cache empty data if no UKT found, to avoid reprocessing immediately
                BELUM_BAYAR_CACHE = {"grouped": pd.DataFrame(), "tahun_list": []}
                BELUM_BAYAR_LAST_FETCH = now
                return render_template(
                    'dekandetail_belumbayarukt.html',
                    data=[],
                    tahun_list=[],
                    total_data=0,
                    page=1,
                    per_page=per_page,
                    total_pages=0
                )

            grouped = df_ukt.groupby(['NIM', 'Tahun Akademik']).agg(
                Nama=('Nama', 'first'),
                Program_Studi=('Program Studi', 'first'),
                Status_Akademik=('Status Akademik', 'first'),
                Total_Tunggakan=('Total Tunggakan', 'sum')
            ).reset_index()
            # Rename columns to match expected keys if necessary, or adjust template
            grouped.rename(columns={'Program_Studi': 'Program Studi', 'Status_Akademik': 'Status Akademik', 'Total_Tunggakan': 'Total Tunggakan'}, inplace=True)


            tahun_list = sorted(grouped['Tahun Akademik'].dropna().unique())

            # Store in cache
            BELUM_BAYAR_CACHE = {
                "grouped": grouped,
                "tahun_list": tahun_list
            }
            BELUM_BAYAR_LAST_FETCH = now

        # Process biodata and merge with data
        enriched_data = []
        for _, row in grouped.iterrows():
            nim = row['NIM']

            # Check biodata cache
            if nim in BIODATA_CACHE:
                bio = BIODATA_CACHE[nim]
            else:
                try:
                    res = requests.post(API_BIODATA_URL, data={"nim": nim}, headers=COMMON_HEADERS, timeout=10)
                    res.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    bio = res.json().get("data", {})
                except requests.exceptions.RequestException as e:
                    print(f"[ERROR] Failed to fetch biodata for {nim}: {e}")
                    bio = {}
                except ValueError as e:
                    print(f"[ERROR] Failed to parse JSON for biodata {nim}: {e}")
                    bio = {}
                
                BIODATA_CACHE[nim] = bio

            alamat_parts = [
                bio.get('kelurahan', ''),
                bio.get('kecamatan', ''),
                bio.get('kotakab', ''),
                bio.get('propinsi', '')
            ]
            alamat = ", ".join(filter(None, alamat_parts))
            if not alamat.strip():
                alamat = "-"

            email = bio.get("email", "-")
            telp = bio.get("hp", "-")

            enriched_data.append({
                'Tahun Akademik': row['Tahun Akademik'],
                'NIM': nim,
                'Nama': row['Nama'],
                'Program Studi': row['Program Studi'],
                'Status Akademik': row['Status Akademik'],
                'Total Tunggakan': int(row['Total Tunggakan']),
                'Alamat': alamat,
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

    except FileNotFoundError:
        return "CSV file 'Rincian_per_mhs.csv' not found in static directory.", 500
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500