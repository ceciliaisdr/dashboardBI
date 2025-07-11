from flask import Blueprint, render_template, request
import pandas as pd
import os
import base64
import requests

tunggakan_bp = Blueprint('tunggakan_bp', __name__)

# === Konfigurasi Auth & API ===
API_BIODATA_URL = 'https://api.upnvj.ac.id/data/get_biodata_mahasiswa'
USERNAME = "uakademik"
PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

def get_basic_auth_header(USERNAME,PASSWORD):
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

COMMON_HEADERS = {
    "X-UPNVJ-API-KEY": API_SECRET,
    "Accept": 'application/json',
    "Authorization": get_basic_auth_header(USERNAME,PASSWORD),
    "User-Agent": "Thunder Client (https://www.thunderclient.com)" # Opsional, bisa dihapus jika tidak diperlukan oleh API
}

@tunggakan_bp.route('/detail_tunggakan')
def detail_tunggakan():
    try:
        file_path = os.path.join('static', 'Rincian_per_mhs.csv')
        
        # Pastikan file ada sebelum mencoba membaca
        if not os.path.exists(file_path):
            return f"Error: File CSV tidak ditemukan di {file_path}", 500

        df = pd.read_csv(file_path)

        # Bersihkan dan filter
        df['Tunggakan'] = df['Tunggakan'].astype(str).str.strip()
        df['Tahun Akademik'] = df['Tahun Akademik'].astype(str).str.strip()
        
        # Menangani potensi nilai non-numerik sebelum konversi ke float
        df['Total Tunggakan'] = df['Total Tunggakan'].astype(str).str.replace(r'[^0-9]', '', regex=True)
        df['Total Tunggakan'] = pd.to_numeric(df['Total Tunggakan'], errors='coerce').fillna(0) # Konversi ke numerik, ganti non-numerik dengan 0

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
                # Menggunakan COMMON_HEADERS yang sudah disatukan
                res = requests.post(API_BIODATA_URL, data={"nim": nim}, headers=COMMON_HEADERS, timeout=10)
                res.raise_for_status() # Tangani status kode HTTP error
                bio = res.json().get("data", {})
                
                # Membangun alamat dengan lebih rapi, menghindari koma ganda jika ada bagian yang kosong
                alamat_parts = [
                    bio.get('kelurahan', ''),
                    bio.get('kecamatan', ''),
                    bio.get('kotakab', ''),
                    bio.get('propinsi', '')
                ]
                alamat = ", ".join(filter(None, alamat_parts)) if any(alamat_parts) else "-" # Gabungkan yang tidak kosong
                
                email = bio.get("email", "-")
                telp = bio.get("hp", "-")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching biodata for NIM {nim}: {e}")
            except ValueError as e:
                print(f"Error parsing biodata JSON for NIM {nim}: {e}")
            except Exception as e:
                print(f"Error processing biodata for NIM {nim}: {e}")

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

        # --- Pagination ---
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        total_rows = len(enriched_data)
        total_pages = (total_rows + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = enriched_data[start:end]

        # --- Filter dropdown ---
        # Gunakan df_ukt yang sudah difilter atau df awal untuk mendapatkan semua opsi unik
        tahun_list = sorted(df['Tahun Akademik'].dropna().unique())
        status_list = sorted(df['Status Akademik'].dropna().unique())

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

    except FileNotFoundError:
        return f"Error: File 'Rincian_per_mhs.csv' tidak ditemukan di direktori 'static'. Pastikan file sudah diunggah dengan benar.", 500
    except pd.errors.EmptyDataError:
        return "Error: File 'Rincian_per_mhs.csv' kosong.", 500
    except pd.errors.ParserError:
        return "Error: Gagal membaca file CSV. Periksa format file.", 500
    except Exception as e:
        return f"Terjadi kesalahan: {e}", 500