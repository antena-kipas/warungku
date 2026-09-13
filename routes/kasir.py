from flask import Blueprint, render_template, session, redirect, url_for, flash
from database import get_db_connection # 1. Tambahkan baris impor ini
import datetime

kasir_bp = Blueprint('kasir', __name__)

# Rute untuk Dashboard (Analitik & Menu)
@kasir_bp.route('/dashboard')
def dashboard():
    if 'logged_in' not in session or not session['logged_in']:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('auth.index'))
    
    conn = get_db_connection()

    # 1. Ambil Pendapatan (Kotor) Hari Ini
    pendapatan_query = conn.execute('''
        SELECT SUM(total_belanja) as total 
        FROM penjualan 
        WHERE date(waktu_transaksi) = date('now', 'localtime')
    ''').fetchone()
    pendapatan = pendapatan_query['total'] if pendapatan_query['total'] else 0

    # 2. Ambil Total Transaksi Hari Ini
    transaksi_query = conn.execute('''
        SELECT COUNT(id_penjualan) as jumlah 
        FROM penjualan 
        WHERE date(waktu_transaksi) = date('now', 'localtime')
    ''').fetchone()
    total_transaksi = transaksi_query['jumlah'] if transaksi_query['jumlah'] else 0

    # 3. Cari Barang Terlaris
    terlaris_query = conn.execute('''
        SELECT b.nama_barang, SUM(dp.jumlah) as total_terjual
        FROM detail_penjualan dp
        JOIN barang b ON dp.id_barang = b.id_barang
        GROUP BY dp.id_barang
        ORDER BY total_terjual DESC
        LIMIT 1
    ''').fetchone()
    barang_terlaris = terlaris_query['nama_barang'] if terlaris_query else "Belum ada transaksi"

    # 4. Ambil 5 Transaksi Terakhir
    transaksi_terakhir = conn.execute('''
        SELECT waktu_transaksi, tipe_penjualan, total_belanja
        FROM penjualan
        ORDER BY waktu_transaksi DESC
        LIMIT 5
    ''').fetchall()

    conn.close()

    # Format Tanggal Hari Ini ke bahasa Indonesia
    bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    now = datetime.datetime.now()
    tanggal_hari_ini = f"{now.day} {bulan_indo[now.month-1]} {now.year}"

    # Kirim semua variabel ke template
    return render_template('dashboard.html', 
                           tanggal=tanggal_hari_ini,
                           pendapatan=pendapatan,
                           total_transaksi=total_transaksi,
                           barang_terlaris=barang_terlaris,
                           transaksi_terakhir=transaksi_terakhir)
# Rute KHUSUS untuk Layar Kasir / Melayani Pembeli
@kasir_bp.route('/transaksi')
def transaksi():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.index'))
    
    # 2. Buka koneksi dan ambil data barang
    conn = get_db_connection()
    barang_list = conn.execute('SELECT * FROM barang ORDER BY nama_barang ASC').fetchall()
    conn.close()

    # 3. Transmisikan variabel barang_list ke templat kasir.html
    return render_template('kasir.html', barang=barang_list)