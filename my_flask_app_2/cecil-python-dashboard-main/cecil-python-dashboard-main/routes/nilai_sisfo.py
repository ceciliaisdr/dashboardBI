from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import os

nilaisisfo_bp = Blueprint('nilaisisfo_bp', __name__)

def load_nilai_s1si():
    paths = [
        "static/data/Nilai_2020-2021_Ganjil_S1SI dan S1IF.csv",
        "static/data/Nilai_2020-2021_Genap_S1SI dan S1IF.csv",
        "static/data/Nilai_2021-2022_Ganjil_S1SI dan S1IF.csv",
        "static/data/Nilai_2021-2022_Genap_S1SI dan S1IF.csv",
        "static/data/Nilai_2022-2023_Ganjil_S1SI dan S1IF.csv",
        "static/data/Nilai_2022-2023_Genap_S1SI dan S1IF.csv",
        "static/data/Nilai_2023-2024_Ganjil_S1SI dan S1IF.csv",
        "static/data/Nilai_2023-2024_Genap_S1SI dan S1IF.csv",
        "static/data/Nilai_2024-2025_Ganjil_S1SI dan S1IF.csv"
    ]

    df_list = []
    for path in paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            if 'f_namaprogdi' in df.columns:
                df = df[df['f_namaprogdi'].str.strip() == 'Sistem Informasi']
                df_list.append(df)

    if not df_list:
        return pd.DataFrame()

    return pd.concat(df_list, ignore_index=True)

@nilaisisfo_bp.route("/dekannilaisisfo")
def nilai_sisfo():
    df = load_nilai_s1si()
    tahun = sorted(df['f_thakad'].dropna().unique(), reverse=True)
    semester = sorted(df['f_semester'].dropna().unique())
    matkul = sorted(df['f_namamk'].dropna().unique())
    return render_template("nilai_sisfo.html", tahun=tahun, semester=semester, matkul=matkul)


@nilaisisfo_bp.route("/get_nilai_data", methods=["POST"])
def get_nilai_data():
    data = request.json
    thakad = data.get("thakad")
    semester = int(data.get("semester"))
    matkul = data.get("matkul")

    df = load_nilai_s1si()
    filtered = df[
        (df['f_thakad'] == thakad) &
        (df['f_semester'] == semester) &
        (df['f_namamk'] == matkul)
    ]

    grouped = filtered.groupby(['f_kelas', 'f_nilaihuruf']).size().unstack(fill_value=0)
    return jsonify(grouped.to_dict(orient='index'))
