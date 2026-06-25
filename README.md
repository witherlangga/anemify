# Anemify - Anemia Risk Prediction System

Aplikasi web berbasis Flask untuk memprediksi risiko anemia menggunakan machine learning models (KNN, Random Forest, Voting Classifier). Dilengkapi dengan sistem autentikasi pengguna, manajemen riwayat prediksi per-akun, dan profil pengguna dengan upload gambar.

## Fitur

- Autentikasi pengguna (Register & Login)
- Prediksi anemia dengan 3 model ML berbeda
- Mode "All Models" untuk membandingkan hasil dari semua model
- Dashboard riwayat prediksi per pengguna
- Export riwayat ke format CSV

## Persyaratan

- Python 3.10+
- MySQL Server atau SQLite
- pip (Python Package Manager)

## Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/your-username/anemify.git
cd anemify
```

### 2. Setup Virtual Environment

Windows:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Auto Setup Database (PENTING)

Jalankan script auto_setup untuk membuat database dan tabel secara otomatis:

```bash
python auto_setup.py
```

Script ini akan:
- Membuat database MySQL `anemiadb` otomatis
- Membuat tabel-tabel yang diperlukan

Jika ada error koneksi, pastikan:
- MySQL server sedang berjalan
- Username/password MySQL benar
- Edit variabel di awal file `auto_setup.py` jika perlu menggunakan user/password berbeda

### 5. Jalankan Aplikasi

```bash
python app.py
```

Buka browser: http://127.0.0.1:5000

## Cara Menggunakan

1. Register akun baru di halaman register
2. Login dengan username dan password
3. Masukkan data medis di halaman prediksi
4. Pilih model (KNN, Random Forest, Voting Clasifier dan All Models)
5. Lihat hasil prediksi dengan probabilitas
6. Akses Dashboard untuk melihat riwayat semua prediksi
7. Download riwayat dalam format CSV
8. Edit profil dan upload foto di halaman profil

## Model Machine Learning

Aplikasi menggunakan 3 model untuk prediksi:
- KNN (K-Nearest Neighbors)
- Random Forest
- Voting Classifier (kombinasi 3 model)

Hasil prediksi ditampilkan dengan probabilitas dalam format persentase.

## Dependencies

- Flask >= 3.1
- Flask-SQLAlchemy >= 3.1
- Flask-Login >= 0.6
- PyMySQL >= 1.1
- Werkzeug >= 3.0
- pandas >= 2.0
- numpy >= 1.24
- scikit-learn >= 1.9
- joblib >= 1.4
- matplotlib >= 3.7
- seaborn >= 0.13
- Pillow >= 10.0

## Team
Anggota 1
       - 2301010
Anggota 2
       - 2301010
Anggota 3
       - 2301010
Anggota 4
       - 2301010
Anggota 5
       - 2301010
Anggota 6
       - 2301010