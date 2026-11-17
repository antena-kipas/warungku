"""Menyiapkan database: membuat semua tabel dan akun login pertama.

Cara pakai:
    python init_db.py            -> membuat tabel yang belum ada (aman dijalankan berulang kali)
    python init_db.py --reset    -> MENGHAPUS SEMUA DATA lalu membuat tabel dari nol

Username dan password akun pertama bisa diatur lewat ADMIN_USERNAME dan ADMIN_PASSWORD di .env.
"""
import os
import sys

from werkzeug.security import generate_password_hash

from app import app
from database import db, User

reset = '--reset' in sys.argv

with app.app_context():
    if reset:
        db.drop_all()
        print('Semua tabel lama dihapus.')

    # 1. Buat semua tabel yang didefinisikan di database.py
    db.create_all()

    # 2. Buat akun pertama (akun kasir nenek) kalau belum ada
    username = os.getenv('ADMIN_USERNAME', 'warungku')
    password_asli = os.getenv('ADMIN_PASSWORD', 'password')

    if User.query.filter_by(username=username).first():
        print(f"Akun '{username}' sudah ada, tidak dibuat ulang.")
    else:
        db.session.add(User(
            username=username,
            password=generate_password_hash(password_asli),
            role='admin',
        ))
        db.session.commit()
        print(f"Akun berhasil ditambahkan -> Username: {username}")
        if password_asli == 'password':
            print("PERINGATAN: password masih bawaan ('password'). Ganti lewat ADMIN_PASSWORD sebelum aplikasi dipakai online.")

    alamat = db.engine.url
    if alamat.get_backend_name() == 'sqlite':
        print(f"Database siap dipakai: SQLite di {alamat.database}")
    else:
        print(f"Database siap dipakai: {alamat.get_backend_name()} di {alamat.host}/{alamat.database}")
