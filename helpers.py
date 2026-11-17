"""Fungsi bantu yang dipakai di banyak halaman."""
from functools import wraps

from flask import flash, jsonify, redirect, request, session, url_for


def wajib_login(fungsi):
    """Pasang di atas rute supaya hanya bisa dibuka setelah login."""
    @wraps(fungsi)
    def pembungkus(*args, **kwargs):
        if not session.get('logged_in'):
            # Untuk alamat /api/... balas dengan JSON, bukan halaman login.
            if request.path.startswith('/api/'):
                return jsonify(ok=False, pesan='Sesi habis. Silakan login lagi.'), 401
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('auth.index'))
        return fungsi(*args, **kwargs)
    return pembungkus


def format_rupiah(angka):
    """12500 -> 'Rp 12.500'"""
    return 'Rp ' + f'{int(angka or 0):,}'.replace(',', '.')


def url_gambar(nama_file):
    """Alamat gambar barang, atau None kalau barang belum punya gambar."""
    if not nama_file:
        return None
    return url_for('static', filename=f'uploads/{nama_file}')
