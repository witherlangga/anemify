#!/usr/bin/env python
"""
Setup Script untuk Anemify
Membuat database MySQL dan tabel secara otomatis
"""

import pymysql
import sys
import os

# Konfigurasi Database
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'anemiadb'

def create_database():
    """Membuat database jika belum ada"""
    try:
        # Koneksi ke MySQL tanpa database
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cursor = conn.cursor()
        
        # Buat database
        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS {DB_NAME} 
            CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[OK] Database '{DB_NAME}' berhasil dibuat/sudah ada")
        return True
    except pymysql.Error as e:
        print(f"[ERROR] Gagal membuat database: {e}")
        return False

def create_tables():
    """Membuat tabel-tabel yang diperlukan"""
    try:
        from app import app, db
        
        with app.app_context():
            # Buat semua tabel dari model
            db.create_all()
            print("[OK] Tabel-tabel berhasil dibuat")
            return True
    except Exception as e:
        print(f"[ERROR] Gagal membuat tabel: {e}")
        return False

def test_connection():
    """Test koneksi ke database"""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.close()
        print("[OK] Koneksi database berhasil")
        return True
    except pymysql.Error as e:
        print(f"[ERROR] Koneksi database gagal: {e}")
        return False

def main():
    print("="*50)
    print("Anemify Database Setup")
    print("="*50)
    
    # Step 1: Buat database
    print("\n[1/3] Membuat database...")
    if not create_database():
        sys.exit(1)
    
    # Step 2: Test koneksi
    print("\n[2/3] Testing koneksi...")
    if not test_connection():
        print("[WARNING] Koneksi gagal, pastikan MySQL berjalan")
    
    # Step 3: Buat tabel
    print("\n[3/3] Membuat tabel...")
    if not create_tables():
        sys.exit(1)
    
    print("\n" + "="*50)
    print("Setup selesai! Database siap digunakan.")
    print("="*50)
    print("\nUntuk menjalankan aplikasi:")
    print("  python app.py")

if __name__ == '__main__':
    main()
