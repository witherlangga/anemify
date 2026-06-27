# 🩺 Anemify - Anemia Risk Prediction System

**Anemify** adalah aplikasi web interaktif berbasis **Flask** dan **Machine Learning** yang dirancang untuk menganalisis dan memprediksi risiko anemia berdasarkan indikator medis darah (hematologi). Aplikasi ini dilengkapi dengan sistem manajemen pengguna, perbandingan multi-model ML, riwayat prediksi terintegrasi, serta fitur ekspor data.

---

## ✨ Fitur Utama

- 🔐 **Autentikasi Pengguna**: Sistem pendaftaran (Register) dan masuk (Login) yang aman dengan enkripsi kata sandi.
- 🤖 **Multi-Model Machine Learning**: Prediksi risiko anemia menggunakan 3 algoritma ML berbeda:
  - **KNN (K-Nearest Neighbors)**
  - **Random Forest Classifier**
  - **Voting Classifier** (Ensemble Learning)
- ⚖️ **Mode Komparasi ("All Models")**: Bandingkan hasil prediksi dan tingkat probabilitas dari ketiga model sekaligus dalam satu kali analisis.
- 📊 **Dashboard Riwayat Prediksi**: Menyimpan seluruh catatan medis dan hasil analisis prediksi per akun secara personal.
- 📥 **Export Data CSV**: Ekspor seluruh riwayat analisis ke dalam file `.csv` untuk keperluan dokumentasi medis.
- 👤 **Manajemen Profil**: Pengguna dapat memperbarui informasi akun serta mengunggah foto profil.

---

## 🔬 Parameter Input Medis

Aplikasi ini membutuhkan 5 indikator medis utama untuk melakukan analisis:

| Parameter | Nama Indikator | Satuan | Deskripsi |
| :--- | :--- | :--- | :--- |
| **Gender** | Jenis Kelamin | Male / Female | Jenis kelamin pasien |
| **Hemoglobin** | Kadar Hemoglobin | g/dL | Protein eritrosit pembawa oksigen |
| **MCH** | Mean Corpuscular Hemoglobin | pg | Jumlah rata-rata hemoglobin per sel darah merah |
| **MCHC** | Mean Corpuscular Hemoglobin Concentration | g/dL | Konsentrasi rata-rata hemoglobin dalam sel darah merah |
| **MCV** | Mean Corpuscular Volume | fL | Ukuran atau volume rata-rata sel darah merah |

---

## 🛠️ Teknologi & Dependencies

- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login
- **Database**: MySQL / MariaDB (via PyMySQL)
- **Machine Learning & Data Processing**: Scikit-Learn, Pandas, NumPy, Joblib
- **Visualisasi & Utilities**: Matplotlib, Seaborn, Pillow (PIL), Python-Dotenv

---

## 📁 Struktur Proyek

```text
anemify/
├── data/                       # Dataset latih dan uji (CSV)
│   └── ANEMIA_DATASEST_DML_UAS.csv
├── models/                     # Model Machine Learning & Scaler (.pkl)
│   ├── knn_model.pkl
│   ├── random_forest_model.pkl
│   ├── voting_classifier_model.pkl
│   └── scaler.pkl
├── static/                     # Assets statis (CSS, JS, Gambar & Uploads)
│   └── uploads/                # Direktori pasfoto profil pengguna
├── templates/                  # Template HTML (Jinja2)
├── utils/                      # Helper & modul prediksi
│   └── prediction.py
├── .env.example                # Template konfigurasi environment variables
├── .gitignore                  # Berkas pengecualian Git
├── app.py                      # Main application & routing Flask
├── auto_setup.py               # Skrip otomatisasi pembuatan database & tabel
├── config.py                   # Konfigurasi aplikasi & database
├── README.md                   # Dokumentasi proyek
└── requirements.txt            # Daftar pustaka / dependensi Python
```

---

## 🚀 Panduan Instalasi & Setup

### 1. Prasyarat Sistem
- Python 3.10 atau versi lebih baru
- MySQL Server / MariaDB (misal via XAMPP / Laragon / MySQL Service)
- Git & Pip package manager

### 2. Clone Repository
```bash
git clone https://github.com/your-username/anemify.git
cd anemify
```

### 3. Membuat & Mengaktifkan Virtual Environment

**Windows (PowerShell / CMD):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(Jika muncul kendala Script Execution Policy di PowerShell, jalankan `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` terlebih dahulu)*

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Konfigurasi Environment (`.env`)
Salin berkas `.env.example` menjadi `.env` dan sesuaikan kredensial database MySQL Anda:
```bash
cp .env.example .env
```
Isi konfigurasi pada `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=anemiadb
SECRET_KEY=anemify-secret-key-super-secret
```

### 6. Auto Setup Database (PENTING)
Jalankan skrip otomatisasi untuk membuat database `anemiadb` dan tabel yang dibutuhkan:
```bash
python auto_setup.py
```
*Pastikan layanan MySQL server Anda sudah dalam keadaan aktif sebelum menjalankan langkah ini.*

### 7. Jalankan Aplikasi
```bash
python app.py
```
Akses aplikasi melalui peramban web di: `http://127.0.0.1:5000`

---

## 💡 Cara Penggunaan

1. Buka aplikasi di browser dan masuk ke halaman **Register** untuk membuat akun baru.
2. Silakan **Login** menggunakan nama pengguna dan kata sandi yang telah didaftarkan.
3. Buka menu **Prediksi**, masukkan indikator medis darah (Gender, Hemoglobin, MCH, MCHC, MCV).
4. Pilih algoritma model yang diinginkan (KNN, Random Forest, Voting Classifier, atau All Models) lalu klik **Prediksi**.
5. Lihat hasil estimasi risiko anemia beserta persentase probabilitasnya.
6. Pantau seluruh data riwayat pemeriksaan melalui menu **Dashboard**.
7. Klik tombol **Export CSV** di Dashboard untuk mengunduh laporan riwayat medis.
8. Perbarui informasi diri dan pasfoto melalui menu **Profil**.

---

## 👥 Tim Pengembang

- **Erlangga Syafutra** - 2301010192

---

## 📄 Lisensi

Proyek ini dikembangkan untuk keperluan akademik dan penelitian Data Mining / Machine Learning.