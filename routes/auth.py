from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import User

# Membuat blueprint bernama 'auth'
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    # Jika sudah login, langsung arahkan ke dashboard kasir
    if session.get('logged_in'):
        return redirect(url_for('kasir.dashboard'))
    return render_template('index.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password_yang_diketik = request.form.get('password', '')

    # 1. Cari data pengguna berdasarkan username
    user = User.query.filter_by(username=username).first()

    # 2. Validasi Login
    # Cek apakah user ditemukan di database DAN apakah password yang diketik cocok dengan acakan (hash)
    if user and check_password_hash(user.password, password_yang_diketik):
        # Jika cocok, buat sesi login
        session['logged_in'] = True
        session['username'] = user.username
        session['role'] = user.role # Menyimpan hak akses (misal: 'kasir' atau 'admin')
        return redirect(url_for('kasir.dashboard'))
    else:
        # Jika salah username atau salah password
        flash('Username atau password salah.', 'danger')
        return redirect(url_for('auth.index'))

@auth_bp.route('/logout')
def logout():
    # Hapus semua data sesi saat logout
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.index'))
