"""Mengisi database dengan DATA CONTOH untuk demo dan uji coba tampilan.

Isinya 24 barang khas warung dan transaksi rekaan selama 14 hari terakhir.
Jangan dijalankan di database yang sudah dipakai warung sungguhan.

Cara pakai:
    python init_db.py
    python seed_demo.py
"""
import os
import random
import sys
from datetime import timedelta

from app import app
from database import db, waktu_sekarang, Barang, Penjualan, DetailPenjualan

# (nama, emoji gambar, barcode, harga modal, harga eceran, harga grosir, stok)
# Barcode di sini angka rekaan. Barang curah (telur, beras, bawang) sengaja tanpa barcode.
BARANG_CONTOH = [
    ('Beras Ramos 1 kg',        '🍚', None,            12500, 14000, 13500, 60),
    ('Telur Ayam 1 kg',         '🥚', None,            26000, 29000, 28000, 25),
    ('Minyak Goreng 1 L',       '🫗', '8990001000011', 16000, 18000, 17000, 30),
    ('Gula Pasir 1 kg',         '🧂', '8990001000028', 15500, 17500, 16500, 40),
    ('Mie Instan Goreng',       '🍜', '8990001000035',  2800,  3500,  3100, 120),
    ('Mie Instan Kuah',         '🍲', '8990001000042',  2700,  3500,  3000, 96),
    ('Kopi Sachet',             '☕', '8990001000059',  1300,  2000,  1600, 150),
    ('Teh Celup Kotak',         '🍵', '8990001000066',  6500,  8000,  7200, 18),
    ('Susu Kental Manis',       '🥛', '8990001000073', 10500, 12500, 11500, 20),
    ('Air Mineral 600 ml',      '💧', '8990001000080',  2500,  4000,  3000, 72),
    ('Teh Botol',               '🧃', '8990001000097',  3500,  5000,  4200, 36),
    ('Roti Tawar',              '🍞', '8990001000103', 12000, 15000, 13500, 4),
    ('Biskuit Kaleng Kecil',    '🍪', '8990001000110',  8000, 10000,  9000, 14),
    ('Keripik Singkong',        '🥔', None,             4000,  5000,  4500, 22),
    ('Permen (5 biji)',         '🍬', None,              700,  1000,   800, 200),
    ('Kecap Manis Botol',       '🍶', '8990001000127', 19000, 22000, 20500, 9),
    ('Saus Sambal Botol',       '🌶️', '8990001000134',  9000, 11000, 10000, 3),
    ('Bawang Merah 250 g',      '🧅', None,             8000, 10000,  9000, 12),
    ('Sabun Mandi',             '🧼', '8990001000141',  3200,  4500,  3800, 40),
    ('Sampo Sachet',            '🧴', '8990001000158',   700,  1000,   850, 180),
    ('Pasta Gigi',              '🪥', '8990001000165',  9500, 12000, 10500, 0),
    ('Deterjen Bubuk 800 g',    '🧺', '8990001000172', 17000, 20000, 18500, 11),
    ('Tisu Wajah',              '🧻', '8990001000189',  7500,  9500,  8500, 5),
    ('Korek Api Gas',           '🔥', '8990001000196',  2500,  4000,  3000, 30),
]

# Barang yang sering dibeli bersamaan. Sengaja dibuat supaya nanti fitur
# rekomendasi bundling (Apriori) punya pola yang bisa ditemukan.
PASANGAN = [
    ('Mie Instan Goreng', 'Telur Ayam 1 kg', 0.45),
    ('Mie Instan Kuah', 'Telur Ayam 1 kg', 0.35),
    ('Kopi Sachet', 'Gula Pasir 1 kg', 0.40),
    ('Teh Celup Kotak', 'Gula Pasir 1 kg', 0.50),
    ('Beras Ramos 1 kg', 'Minyak Goreng 1 L', 0.40),
    ('Sabun Mandi', 'Sampo Sachet', 0.45),
    ('Roti Tawar', 'Susu Kental Manis', 0.50),
]

# Seberapa sering tiap barang dibeli (makin besar makin laris)
BOBOT = [9, 8, 6, 6, 14, 10, 12, 3, 4, 9, 6, 3, 2, 4, 6, 2, 2, 4, 5, 7, 2, 3, 2, 4]

# Jam ramai: pagi (06-09) dan sore (16-20)
BOBOT_JAM = {5: 1, 6: 5, 7: 8, 8: 7, 9: 5, 10: 3, 11: 3, 12: 4, 13: 3, 14: 2,
             15: 3, 16: 6, 17: 8, 18: 9, 19: 7, 20: 5, 21: 2}

WARNA_LATAR = ['#fde68a', '#bfdbfe', '#bbf7d0', '#fecaca', '#ddd6fe', '#fed7aa', '#a5f3fc', '#fbcfe8']


def buat_gambar_contoh(nomor, emoji):
    """Membuat gambar SVG sederhana (emoji besar di atas warna polos) sebagai pengganti foto barang."""
    folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(folder, exist_ok=True)
    nama_file = f'contoh-{nomor:02d}.svg'
    warna = WARNA_LATAR[nomor % len(WARNA_LATAR)]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">'
        f'<rect width="200" height="200" fill="{warna}"/>'
        f'<text x="100" y="108" font-size="110" text-anchor="middle" dominant-baseline="middle">{emoji}</text>'
        '</svg>'
    )
    with open(os.path.join(folder, nama_file), 'w', encoding='utf-8') as berkas:
        berkas.write(svg)
    return nama_file


def isi_data_contoh():
    acak = random.Random(2026)  # angka tetap supaya hasilnya sama tiap dijalankan

    # 1. Barang
    daftar_barang = []
    for nomor, (nama, emoji, barcode, modal, eceran, grosir, stok) in enumerate(BARANG_CONTOH):
        barang = Barang(
            nama_barang=nama, barcode=barcode, gambar=buat_gambar_contoh(nomor, emoji),
            stok=stok, harga_beli=modal, harga_eceran=eceran, harga_grosir=grosir,
        )
        db.session.add(barang)
        daftar_barang.append(barang)
    db.session.flush()  # supaya tiap barang sudah punya id_barang
    peta_nama = {b.nama_barang: b for b in daftar_barang}

    # 2. Transaksi 14 hari terakhir (hari ini hanya sampai jam sekarang)
    sekarang = waktu_sekarang()
    awal_hari_ini = sekarang.replace(hour=0, minute=0, second=0, microsecond=0)
    jam_pilihan, bobot_jam = list(BOBOT_JAM.keys()), list(BOBOT_JAM.values())
    jumlah_struk = 0

    for mundur in range(13, -1, -1):
        hari = awal_hari_ini - timedelta(days=mundur)
        waktu_struk = []
        for _ in range(acak.randint(28, 46)):
            waktu = hari + timedelta(hours=acak.choices(jam_pilihan, bobot_jam)[0],
                                     minutes=acak.randint(0, 59), seconds=acak.randint(0, 59))
            if waktu <= sekarang:
                waktu_struk.append(waktu)

        for waktu in sorted(waktu_struk):
            grosir = acak.random() < 0.12
            tipe = 'Grosir' if grosir else 'Eceran'

            # Pilih 1-4 barang, lalu tambahkan pasangannya dengan peluang tertentu
            isi = {}
            for barang in acak.choices(daftar_barang, BOBOT, k=acak.choices([1, 2, 3, 4], [35, 35, 20, 10])[0]):
                isi[barang.id_barang] = barang
            for nama_a, nama_b, peluang in PASANGAN:
                a, b = peta_nama[nama_a], peta_nama[nama_b]
                if a.id_barang in isi and acak.random() < peluang:
                    isi[b.id_barang] = b

            penjualan = Penjualan(waktu_transaksi=waktu, tipe_penjualan=tipe, total_belanja=0)
            for barang in isi.values():
                jumlah = acak.randint(6, 24) if grosir else acak.choices([1, 2, 3, 5], [60, 25, 10, 5])[0]
                harga = barang.harga_untuk(tipe)
                penjualan.detail.append(DetailPenjualan(
                    id_barang=barang.id_barang, jumlah=jumlah, harga_satuan=harga,
                    harga_beli_satuan=barang.harga_beli, subtotal=harga * jumlah,
                ))
                penjualan.total_belanja += harga * jumlah
            db.session.add(penjualan)
            jumlah_struk += 1

    db.session.commit()
    return len(daftar_barang), jumlah_struk


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Barang.query.first() or Penjualan.query.first():
            print('Dibatalkan: database sudah berisi barang atau transaksi.')
            print('Data contoh hanya untuk database kosong. Jalankan "python init_db.py --reset" dulu kalau memang ingin mengulang dari nol.')
            sys.exit(1)
        jumlah_barang, jumlah_struk = isi_data_contoh()
        print(f'Data contoh masuk: {jumlah_barang} barang dan {jumlah_struk} transaksi.')
