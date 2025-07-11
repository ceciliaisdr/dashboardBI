from flask import Blueprint, render_template, request
import pandas as pd
import os
import base64
import requests

tunggakan_bp = Blueprint('tunggakan_bp', __name__)

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


@tunggakan_bp.route('/detail_tunggakan')
def detail_tunggakan():
    try:
        file_path = os.path.join('static', 'Rincian_per_mhs.csv')
        df = pd.read_csv(file_path)

        # Bersihkan & filter
        df['Tunggakan'] = df['Tunggakan'].astype(str).str.strip()
        df['Tahun Akademik'] = df['Tahun Akademik'].astype(str).str.strip()
        df['Total Tunggakan'] = df['Total Tunggakan'].astype(str).str.replace(r'[^0-9]', '', regex=True).astype(float)
        df_ukt = df[df['Tunggakan'] == 'UKT'].copy()

        # Ambil parameter filter
        tahun = request.args.get('tahun')
        status = request.args.get('status')
        if tahun:
            df_ukt = df_ukt[df_ukt['Tahun Akademik'] == tahun]
        if status:
            df_ukt = df_ukt[df_ukt['Status Akademik'] == status]

        # Gabungkan per mahasiswa
        grouped = df_ukt.groupby(['NIM', 'Tahun Akademik']).agg({
            'Nama': 'first',
            'Program Studi': 'first',
            'Status Akademik': 'first',
            'Total Tunggakan': 'sum'
        }).reset_index()

        # Enrichment biodata
        enriched_data = []
        for _, row in grouped.iterrows():
            nim = row['NIM']
            alamat, email, telp = '-', '-', '-'
            try:
                res = requests.post(API_BIODATA_URL, data={"nim": nim}, headers=HEADERS)
                if res.status_code == 200:
                    bio = res.json().get("data", {})
                    if bio:
                        alamat = f"{bio.get('kelurahan', '')}, {bio.get('kecamatan', '')}, {bio.get('kotakab', '')}, {bio.get('propinsi', '')}".strip(', ')
                        email = bio.get("email", "-")
                        telp = bio.get("hp", "-")
                    else:
                        print(f"[WARN] Biodata kosong untuk NIM {nim}")
                else:
                    print(f"[ERROR] Gagal ambil biodata {nim}: status {res.status_code}")
            except Exception as e:
                print(f"[ERROR] Gagal ambil biodata {nim}: {e}")

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

        # --- Pagination ---
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        total_rows = len(enriched_data)
        total_pages = (total_rows + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = enriched_data[start:end]

        # --- Filter dropdown ---
        tahun_list = sorted(df_ukt['Tahun Akademik'].dropna().unique())
        status_list = sorted(df_ukt['Status Akademik'].dropna().unique())

        return render_template(
            'dekandetail_tunggakanaktifnon.html',
            data=paginated_data,
            tahun_list=tahun_list,
            status_list=status_list,
            selected_tahun=tahun,
            selected_status=status,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total_rows=total_rows
        )

    except Exception as e:
        print(f"[ERROR] {e}")
        return f"Error: {e}", 500
