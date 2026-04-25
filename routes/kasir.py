from flask import Blueprint, render_template, session, redirect, url_for, flash

kasir_bp = Blueprint('kasir', __name__)

# Rute untuk Dashboard (Analitik & Menu)
@kasir_bp.route('/dashboard')
def dashboard():
    if 'logged_in' not in session or not session['logged_in']:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('auth.index'))
    return render_template('dashboard.html')

# Rute KHUSUS untuk Layar Kasir / Melayani Pembeli
@kasir_bp.route('/transaksi')
def transaksi():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.index'))
    return render_template('kasir.html')