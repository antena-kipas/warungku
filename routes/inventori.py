from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from database import get_db_connection

inventori_bp = Blueprint('inventori', __name__)

@inventori_bp.route('/produk', methods=['GET', 'POST'])
def daftar_produk():
    # Cek apakah user sudah login
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.index'))
    
    conn = get_db_connection()
    
    # JIKA ADA PENGIRIMAN DATA BARANG BARU (POST)
    if request.method == 'POST':
        barcode = request.form['barcode']
        nama_barang = request.form['nama_barang']
        stok = request.form['stok']
        harga_beli = request.form['harga_beli']
        harga_eceran = request.form['harga_eceran']
        harga_grosir = request.form['harga_grosir']
        
        try:
            conn.execute('''
                INSERT INTO barang (barcode, nama_barang, stok, harga_beli, harga_eceran, harga_grosir)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (barcode, nama_barang, stok, harga_beli, harga_eceran, harga_grosir))
            conn.commit()
            flash('Barang berhasil ditambahkan!', 'success')
        except sqlite3.IntegrityError:
            # Jika barcode yang discan sudah ada di database
            flash('Gagal: Barcode tersebut sudah terdaftar di sistem!', 'danger')
            
        return redirect(url_for('inventori.daftar_produk'))

    # JIKA HANYA MEMBUKA HALAMAN (GET)
    # Ambil semua data barang dari database untuk ditampilkan di tabel
    barang_list = conn.execute('SELECT * FROM barang ORDER BY id_barang DESC').fetchall()
    conn.close()
    
    return render_template('produk.html', barang=barang_list)