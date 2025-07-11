# 🎓 Dashboard Akademik Berbasis Flask

A Flask-based dashboard untuk memantau data mahasiswa, status akademik, KRS, dan UKT berdasarkan peran pengguna (dekan, kaprodi, admin, dll). Aplikasi ini juga mengintegrasikan API eksternal dan menyajikan visualisasi data secara dinamis.

## 📦 Fitur Utama

* Login dan otentikasi berdasarkan peran (role-based access)
* Visualisasi data mahasiswa dalam bentuk chart
* Integrasi API eksternal (UPNVJ) dengan autentikasi dasar (Basic Auth)
* Statistik mahasiswa (aktif, nonaktif, status per angkatan)
* Status pengisian KRS & prediksi mahasiswa
* Informasi nilai dan detail akademik mahasiswa per program studi
* Manajemen tampilan modular dengan Flask Blueprint

## 🚀 Cara Menjalankan

Ikuti langkah-langkah di bawah untuk menjalankan aplikasi secara lokal.

### 1. Clone Repository

```bash
git clone https://github.com/username/nama-repo.git
cd nama-repo
```

### 2. Install Flask

```bash
pip install flask
```

### 3. Install Library Tambahan

```bash
pip install pandas numpy requests
```

**Catatan:**

* Library `base64`, `datetime`, dan `functools` sudah bawaan Python.
* Gunakan juga `pip install -r requirements.txt` jika tersedia.

Jika belum ada `requirements.txt`, buat dengan:

```bash
pip freeze > requirements.txt
```

### 4. Jalankan Aplikasi

```bash
python app.py
```

## 🔐 Role & Akses Menu

Setiap user memiliki role dengan akses ke menu tertentu:

| Role          | Akses Menu                  |
| ------------- | --------------------------- |
| dekan         | UKT, Status Mhs, Nilai, KRS |
| wakil dekan 1 | Status Mhs, Nilai, KRS      |
| wakil dekan 2 | UKT, Status Mhs             |
| kaprodi       | Status Mhs, Nilai, KRS      |
| tata usaha    | UKT, Status Mhs, KRS        |
| akademik      | Semua                       |
| admin         | Semua                       |

## 📁 Struktur Folder (Disarankan)

```
project/
├── app.py
├── routes/                    # Modularisasi route via Blueprint
│   ├── ukt_routes.py
│   ├── statmhs_routes.py
│   └── ...
├── static/                   # File CSV, JS, CSS
│   ├── mahasiswa_keseluruhan.csv
│   └── Tunggakan.csv
├── templates/                # Template HTML (Jinja2)
├── requirements.txt
└── README.md
```

## 🌐 API Endpoint Contoh

* `GET /api/tunggakan-ukt-angkatan`
* `GET /api/perbandingan-tunggakan-status`
* `GET /get_chart_data`
* `GET /filter_ukt?period=ganjil`

## 🧪 Contoh Login Dummy

Gunakan salah satu akun berikut saat login:

| Username    | Password | Role   |
| ----------- | -------- | ------ |
| dekan       | dekan123 | dekan  |
| wakil dekan | wadek123 | wadek1 |
| tata usaha  | tu123    | ktu    |
| admin       | admin123 | admin  |

## 🛠️ Kontribusi

Pull request dan issue sangat terbuka untuk dikembangkan lebih lanjut. Silakan fork dan ajukan PR jika ingin berkontribusi.

---

🔗 Pastikan kamu telah mengatur `SECRET_KEY` secara aman di environment produksi.
