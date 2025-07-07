from flask import Blueprint, jsonify, request
import base64
import requests
import re
from datetime import datetime

nilai_bp = Blueprint('nilai_bp', __name__)

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

# PERBANDINGAN IPK TERTINGGI, TERENDAH, RATA-RATA
@nilai_bp.route('/api/ipk-mahasiswa', methods=['GET'])
def get_ipk_mahasiswa():
    url = 'https://api.upnvj.ac.id/data/list_mahasiswa'
    tahun = request.args.get('angkatan')  # Ambil dari parameter dropdown
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

    result = {prodi: [] for prodi in id_prodi_mapping.values()}
    try:
        # If no tahun specified (Semua Angkatan), we need to fetch data for all batches
        if not tahun:
            # Define all possible batches you want to include
            all_batches = ['2020', '2021', '2022', '2023', '2024']
            for batch in all_batches:
                payload = {"angkatan": batch}
                response = requests.post(url, data=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json().get("data", [])
                    for mhs in data:
                        id_prodi = int(mhs.get("id_program_studi", -1))
                        prodi_name = id_prodi_mapping.get(id_prodi)
                        if not prodi_name:
                            continue
                        ipk = mhs.get("ipk", None)
                        if ipk:
                            try:
                                ipk_float = float(ipk)
                                if 0 <= ipk_float <= 4:  # Validasi IPK antara 0-4
                                    result[prodi_name].append(ipk_float)
                            except:
                                continue
        else:
            # If specific tahun is selected
            payload = {"angkatan": tahun}
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                data = response.json().get("data", [])
                for mhs in data:
                    id_prodi = int(mhs.get("id_program_studi", -1))
                    prodi_name = id_prodi_mapping.get(id_prodi)
                    if not prodi_name:
                        continue
                    ipk = mhs.get("ipk", None)
                    if ipk:
                        try:
                            ipk_float = float(ipk)
                            if 0 <= ipk_float <= 4:  # Validasi IPK antara 0-4
                                result[prodi_name].append(ipk_float)
                        except:
                            continue

        final_result = {}
        for prodi, ipks in result.items():
            if ipks:
                final_result[prodi] = {
                    "tertinggi": max(ipks),
                    "terendah": min(ipks),
                    "rata_rata": round(sum(ipks) / len(ipks), 2)
                }
            else:
                final_result[prodi] = {
                    "tertinggi": 0,
                    "terendah": 0,
                    "rata_rata": 0
                }

        return jsonify(final_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# # RATA-RATA IPS MAHASISWA PER SEMESTER
# from flask import Flask, jsonify, request
# import requests
# import base64
# from collections import defaultdict

# # API credentials
# API_LIST_HISTORI = 'https://api.upnvj.ac.id/data/list_histori_mahasiswa'
# API_REF_PERIODE = 'https://api.upnvj.ac.id/data/ref_periode'
# USERNAME = "uakademik"
# PASSWORD = "VTUzcjRrNGRlbTFrMjAyNCYh"
# API_KEY = "X-UPNVJ-API-KEY"
# API_SECRET = "Cspwwxq5SyTOMkq8XYcwZ1PMpYrYCwrv"

# def basic_auth(username, password):
#     credentials = f"{username}:{password}"
#     return "Basic " + base64.b64encode(credentials.encode()).decode()

# HEADERS = {
#     "API_KEY_NAME": API_KEY,
#     "API_KEY_SECRET": API_SECRET,
#     "Accept": "application/json",
#     "Authorization": basic_auth(USERNAME, PASSWORD)
# }

# TARGET_PRODI_IDS = {
#     3: "S1 Informatika",
#     4: "S1 Sistem Informasi",
#     6: "D3 Sistem Informasi",
#     58: "S1 Sains Data"
# }

# @nilai_bp.route("/api/ipk-rerata-per-semester")
# def ipk_rerata_per_semester():
#     angkatan_awal = 2020
#     angkatan_terkini = 2026  # Angkatan terkini sesuai data yang ada atau sesuai data periode

#     try:
#         # 1. Ambil data periode
#         periode_resp = requests.post(API_REF_PERIODE, headers=HEADERS, json={})
#         periode_resp.raise_for_status()

#         # print("DEBUG: Response periode:")
#         # print(periode_resp.status_code)
#         # print(periode_resp.text)

#         periode_json = periode_resp.json()
#         if "data" not in periode_json or not isinstance(periode_json["data"], list):
#             return jsonify({"error": "Respons dari ref_periode tidak berisi data yang valid"}), 500

#         periode_data = periode_json["data"]
#         periode_map = {
#             str(p["id_periode"]): p
#             for p in periode_data if "id_periode" in p
#         }

#         # 2. Loop untuk mengambil data dari angkatan 2020 sampai angkatan terkini
#         filtered_data = []
#         for angkatan in range(angkatan_awal, angkatan_terkini + 1):
#         #     # Ambil id_periode untuk angkatan saat ini (perlu looping untuk beberapa semester)
#             for periode in periode_data:
#                 id_periode = str(periode["id_periode"])
#                 # print(f"DEBUG: Mengambil data untuk id_periode: {id_periode}, angkatan: {angkatan}")

#                 # 3. Ambil data histori mahasiswa untuk setiap angkatan dan periode
#                 for id_program_studi in [4, 3, 6, 58]:  # ID prodi yang relevan
#                     # print(f"DEBUG: Mengambil data untuk id_prodi: {id_program_studi}")

#                     # Dinamis generate NIM
#                     # nim = generate_nim(angkatan)  # Fungsi untuk menghasilkan NIM secara dinamis
#                     # print(nim)

#                     # histori_resp = requests.post(API_LIST_HISTORI, headers=HEADERS, json={
#                         # "id_periode": id_periode,  # Kirimkan id_periode yang valid
#                         # "id_program_studi": str(id_program_studi),  # Kirimkan ID Prodi yang valid
#                         # "nim": nim  # Kirimkan NIM yang valid
#                     # })
#                     histori_resp = requests.post(API_LIST_HISTORI, data={
#                         "id_periode": id_periode
#                     }, headers=HEADERS)
#                     histori_resp.raise_for_status()

#                     # print(f"DEBUG: Response histori untuk angkatan {angkatan} dan prodi {id_program_studi}:")
#                     # print(histori_resp.status_code)
#                     # print(histori_resp.text)

#                     histori_json = histori_resp.json()
#                     if "data" in histori_json and isinstance(histori_json["data"], list):
#                         histori_data = histori_json["data"]

#                         # Filter berdasarkan angkatan dan program studi
#                         for m in histori_data:
#                             nim = m.get("nim", "")
#                             if len(nim) >= 4:
#                                 mahasiswa_angkatan = nim[:2]  # 2 digit pertama untuk angkatan
#                                 if mahasiswa_angkatan == str(angkatan)[2:4]:  # Cek jika angkatan cocok
#                                     filtered_data.append(m)
#                                     # print(filtered_data)
#                                     ips_raw = m.get("ips")
#                                     # print(ips_raw)

#                                     try:
#                                         ips = float(ips_raw)
#                                     except (TypeError, ValueError):
#                                         continue

#                                     prodi_id = str(m.get("id_program_studi"))
#                                     prodi_name = TARGET_PRODI_IDS.get(int(prodi_id))

#                                     if not id_periode or not prodi_name or id_periode not in periode_map:
#                                         continue

#                                     periode = periode_map[id_periode]
#                                     semester_label = f"{periode['tahun_periode']}-S{periode['semester_periode']}"
#                                     # print(semester_label)
#                                     ipk_by_prodi_semester = defaultdict(lambda: defaultdict(list))
#                                     ipk_by_prodi_semester[prodi_name][semester_label].append(ips)
#                                     # print(ipk_by_prodi_semester)

#                                     result = {}
#                                     if prodi_name in ipk_by_prodi_semester:
#                                         result[prodi_name] = []
#                                         sorted_semesters = sorted(
#                                             ipk_by_prodi_semester[prodi_name].keys(),
#                                             key=lambda x: (int(x.split('-')[0]), int(x.split('-S')[1]))
#                                         )
                                        
#                                         for semester in sorted_semesters:
#                                             ips_list = ipk_by_prodi_semester[prodi_name][semester]
#                                             if not ips_list:
#                                                 continue
#                                             avg_ips = round(sum(ips_list) / len(ips_list), 2)
#                                             result[prodi_name].append({
#                                                 "semester": semester,
#                                                 "rata_rata_ips": avg_ips
#                                             })

#                                             if not result:
#                                                 return jsonify({"error": "Tidak ada data IPS yang valid untuk program studi yang dipilih"}), 404

#                                             # return jsonify(result)
#                                     print(result)
    
#         if not filtered_data:
#             return jsonify({
#                 "error": f"Tidak ada data untuk angkatan dari 2020 sampai {angkatan_terkini} pada program studi yang dipilih"
#             }), 404
        
#         return jsonify(result)

#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": f"Gagal mengambil data dari API: {str(e)}"}), 500
#     except Exception as e:
#         print(f"Server error: {str(e)}")
#         return jsonify({"error": f"Terjadi kesalahan server: {str(e)}"}), 500