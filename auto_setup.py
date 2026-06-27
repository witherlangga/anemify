#!/usr/bin/env python
"""
Auto Setup Script untuk Anemify
Jalankan script ini sekali untuk setup database dan tabel
"""

import pymysql
import sys
import os
import config

# Konfigurasi Database dari config.py / .env
DB_HOST = config.DB_HOST
DB_PORT = config.DB_PORT
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD
DB_NAME = config.DB_NAME

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(step, total, text):
    print(f"\n[{step}/{total}] {text}")

def create_database():
    """Membuat database jika belum ada"""
    try:
        # Koneksi ke MySQL tanpa database
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cursor = conn.cursor()
        
        # Buat database
        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS `{DB_NAME}` 
            CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"    [OK] Database '{DB_NAME}' dibuat/sudah ada")
        return True
    except pymysql.Error as e:
        print(f"    [ERROR] Gagal membuat database: {e}")
        return False

def test_connection():
    """Test koneksi ke database"""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.close()
        print(f"    [OK] Koneksi ke database berhasil")
        return True
    except pymysql.Error as e:
        print(f"    [ERROR] Koneksi gagal: {e}")
        return False

def create_tables():
    """Membuat tabel-tabel yang diperlukan"""
    try:
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print(f"    [OK] Tabel-tabel berhasil dibuat")
            return True
    except Exception as e:
        print(f"    [ERROR] Gagal membuat tabel: {e}")
        return False

def check_dependencies():
    """Cek apakah semua dependency terinstall"""
    required = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'flask_login': 'Flask-Login',
        'pymysql': 'PyMySQL',
        'dotenv': 'python-dotenv',
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(name)
    
    if missing:
        print(f"    [ERROR] Module yang hilang: {', '.join(missing)}")
        print(f"    Jalankan: pip install -r requirements.txt")
        return False
    
    print(f"    [OK] Semua dependency terinstall")
    return True

def main():
    print_header("ANEMIFY - Auto Setup")
    
    print("\nSetup akan melakukan:")
    print("  1. Mengecek dependencies")
    print("  2. Membuat database MySQL")
    print("  3. Membuat tabel-tabel database")
    
    print_step(1, 3, "Checking Dependencies")
    if not check_dependencies():
        sys.exit(1)
    
    print_step(2, 3, "Creating Database")
    if not create_database():
        print("\n    Pastikan:")
        print("    - MySQL server sedang berjalan")
        print("    - Username/password MySQL benar (edit auto_setup.py jika perlu)")
        sys.exit(1)
    
    print_step(3, 3, "Testing Connection & Creating Tables")
    if not test_connection():
        sys.exit(1)
    
    if not create_tables():
        sys.exit(1)
    
    print_header("SETUP SELESAI!")
    
    print("\nLangkah selanjutnya:")
    print("  1. Jalankan aplikasi: python app.py")
    print("  2. Buka browser: http://127.0.0.1:5000")
    print("  3. Buat akun baru di halaman Register")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
