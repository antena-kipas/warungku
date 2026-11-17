import os
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from database import db, Barang
from helpers import wajib_login

inventori_bp = Blueprint('inventori', __name__)

EKSTENSI_GAMBAR = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


def folder_gambar():
    folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(folder, exist_ok=True)
    return folder


def simpan_gambar(berkas):
    """Menyimpan gambar barang ke static/uploads. Mengembalikan nama filenya, atau None kalau tidak ada gambar."""
    if not berkas or not berkas.filename:
        return None
    ekstensi = berkas.filename.rsplit('.', 1)[-1].lower() if '.' in berkas.filename else ''
    if ekstensi not in EKSTENSI_GAMBAR:
        raise ValueError('Format gambar harus JPG, PNG, WEBP, atau GIF.')
    # Nama file diacak supaya tidak bentrok dan tidak bisa ditebak
    nama_file = f'{uuid.uuid4().hex}.{ekstensi}'
    berkas.save(os.path.join(folder_gambar(), nama_file))
    return nama_file


def hapus_gambar(nama_file):
    """Menghapus file gambar lama setelah diganti."""
    if not nama_file:
        return
    jalur = os.path.join(folder_gambar(), os.path.basename(nama_file))
    if os.path.isfile(jalur):
        os.remove(jalur)


def angka(nilai):
    """Mengubah isian form menjadi bilangan bulat. Kosong atau tidak valid dianggap 0."""
    try:
        return max(int(float(nilai)), 0)
    except (TypeError, ValueError):
        return 0


def isi_dari_form(barang):
    """Mengisi kolom barang dari form tambah/ubah."""
    barang.barcode = request.form.get('barcode', '').strip() or None  # kosong = tanpa barcode
    barang.nama_barang = request.form.get('nama_barang', '').strip()
    barang.stok = angka(request.form.get('stok'))
    barang.harga_beli = angka(request.form.get('harga_beli'))
    barang.harga_eceran = angka(request.form.get('harga_eceran'))
    barang.harga_grosir = angka(request.form.get('harga_grosir'))


def simpan_barang(barang, pesan_sukses):
    """Validasi lalu simpan barang (baru maupun hasil ubahan)."""
    gambar_lama = barang.gambar
    gambar_baru = None
    try:
        isi_dari_form(barang)
        if not barang.nama_barang:
            raise ValueError('Nama barang wajib diisi.')
        if not barang.harga_eceran and not barang.harga_grosir:
            raise ValueError('Isi minimal salah satu harga jual (eceran atau grosir).')
        gambar_baru = simpan_gambar(request.files.get('gambar'))
        if gambar_baru:
            barang.gambar = gambar_baru
        db.session.add(barang)
        db.session.commit()
    except ValueError as galat:
        db.session.rollback()
        hapus_gambar(gambar_baru)
        flash(f'Gagal: {galat}', 'danger')
        return
    except IntegrityError:
        # Jika barcode yang discan sudah ada di database
        db.session.rollback()
        hapus_gambar(gambar_baru)
        flash('Gagal: Barcode tersebut sudah terdaftar di sistem!', 'danger')
        return

    if gambar_baru:
        hapus_gambar(gambar_lama)
    flash(pesan_sukses, 'success')


@inventori_bp.route('/produk', methods=['GET', 'POST'])
@wajib_login
def daftar_produk():
    # JIKA ADA PENGIRIMAN DATA BARANG BARU (POST)
    if request.method == 'POST':
        simpan_barang(Barang(), 'Barang berhasil ditambahkan!')
        return redirect(url_for('inventori.daftar_produk'))

    # JIKA HANYA MEMBUKA HALAMAN (GET)
    barang_list = Barang.query.order_by(Barang.id_barang.desc()).all()
    return render_template('produk.html', barang=barang_list)


@inventori_bp.route('/produk/<int:id_barang>/ubah', methods=['POST'])
@wajib_login
def ubah_produk(id_barang):
    barang = db.session.get(Barang, id_barang)
    if barang is None:
        flash('Gagal: barang tidak ditemukan.', 'danger')
    else:
        simpan_barang(barang, 'Perubahan barang berhasil disimpan!')
    return redirect(url_for('inventori.daftar_produk'))
