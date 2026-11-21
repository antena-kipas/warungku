"""Menyiapkan database: membuat semua tabel dan akun login pertama.

Cara pakai:
    python init_db.py            -> membuat tabel yang belum ada (aman dijalankan berulang kali)
    python init_db.py --reset    -> MENGHAPUS SEMUA DATA lalu membuat tabel dari nol

Username dan password akun pertama WAJIB diisi di file .env:
    ADMIN_USERNAME=...
    ADMIN_PASSWORD=...
Tidak ada nilai bawaan di kode ini, supaya tidak ada password yang ikut tersimpan di git.
"""
import os
import sys

from werkzeug.security import generate_password_hash

from app import app
from database import db, User

PANJANG_MINIMAL_PASSWORD = 8


def ambil_dari_env(nama):
    """Ambil isian dari .env. Hentikan program dengan pesan jelas kalau belum diisi."""
    nilai = os.getenv(nama, '').strip()
    if not nilai:
        sys.exit(f"Gagal: {nama} belum diisi di file .env. Lihat contohnya di .env.example.")
    return nilai


reset = '--reset' in sys.argv

with app.app_context():
    if reset:
        db.drop_all()
        print('Semua tabel lama dihapus.')

    # 1. Buat semua tabel yang didefinisikan di database.py
    db.create_all()

    # 2. Buat akun pertama kalau belum ada
    username = ambil_dari_env('ADMIN_USERNAME')

    if User.query.filter_by(username=username).first():
        print(f"Akun '{username}' sudah ada, tidak dibuat ulang.")
    else:
        password_asli = ambil_dari_env('ADMIN_PASSWORD')
        if len(password_asli) < PANJANG_MINIMAL_PASSWORD:
            sys.exit(f"Gagal: ADMIN_PASSWORD minimal {PANJANG_MINIMAL_PASSWORD} karakter.")

        db.session.add(User(
            username=username,
            password=generate_password_hash(password_asli),  # yang disimpan hanya hasil acakannya (hash)
            role='admin',
        ))
        db.session.commit()
        print(f"Akun berhasil ditambahkan -> Username: {username} (password sesuai ADMIN_PASSWORD di .env)")

    alamat = db.engine.url
    print(f"Database siap dipakai: PostgreSQL di {alamat.host}:{alamat.port}/{alamat.database}")
