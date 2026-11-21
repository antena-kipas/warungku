"""Memindahkan semua data dari SQLite (kasir.db) ke PostgreSQL.

Cukup dijalankan SEKALI, saat pertama kali pindah dari SQLite ke PostgreSQL.

Cara pakai:
    1. Isi DATABASE_URL di file .env dengan alamat PostgreSQL
    2. python migrasi_sqlite_ke_postgres.py               -> ambil data dari kasir.db
       python migrasi_sqlite_ke_postgres.py lokasi/lain.db -> ambil dari file SQLite lain

Aman: kalau database PostgreSQL tujuan sudah berisi data, migrasi dibatalkan
supaya tidak ada data yang tertimpa atau dobel. File SQLite tidak diubah sama sekali.
"""
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, func, select, text

load_dotenv()

from database import db, alamat_database

# Urutan penting: tabel induk dulu, baru tabel yang menunjuk ke induknya (foreign key).
URUTAN_TABEL = ['users', 'supplier', 'barang', 'penjualan', 'detail_penjualan', 'pembelian', 'detail_pembelian']


def main():
    folder_proyek = os.path.dirname(os.path.abspath(__file__))
    file_sqlite = sys.argv[1] if len(sys.argv) > 1 else os.path.join(folder_proyek, 'kasir.db')
    if not os.path.isfile(file_sqlite):
        sys.exit(f'File SQLite tidak ditemukan: {file_sqlite}')

    alamat_tujuan = alamat_database()  # berhenti sendiri kalau DATABASE_URL belum benar

    sumber = create_engine('sqlite:///' + file_sqlite.replace('\\', '/'))
    tujuan = create_engine(alamat_tujuan)
    tabel = db.metadata.tables

    # 1. Buat semua tabel di PostgreSQL (yang sudah ada tidak diubah)
    db.metadata.create_all(tujuan)

    # 2. Pastikan PostgreSQL masih kosong
    with tujuan.connect() as koneksi:
        sudah_ada = {nama: koneksi.scalar(select(func.count()).select_from(tabel[nama])) for nama in URUTAN_TABEL}
    if any(sudah_ada.values()):
        isi = ', '.join(f'{nama}={jumlah}' for nama, jumlah in sudah_ada.items() if jumlah)
        sys.exit(f'Dibatalkan: database PostgreSQL sudah berisi data ({isi}).')

    # 3. Salin data tabel per tabel, semuanya dalam satu transaksi:
    #    kalau ada satu yang gagal, PostgreSQL kembali kosong seperti semula.
    jumlah_disalin = {}
    with sumber.connect() as baca, tujuan.begin() as tulis:
        for nama in URUTAN_TABEL:
            baris = [dict(b._mapping) for b in baca.execute(select(tabel[nama]))]
            if baris:
                tulis.execute(tabel[nama].insert(), baris)
            jumlah_disalin[nama] = len(baris)

            # Nomor otomatis (id) di PostgreSQL harus dilanjutkan dari nomor terbesar yang disalin.
            # Kalau tidak, transaksi baru akan mencoba memakai id 1 lagi dan gagal.
            kolom_id = tabel[nama].primary_key.columns.values()[0].name
            tulis.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{nama}', '{kolom_id}'), "
                f"COALESCE((SELECT MAX({kolom_id}) FROM {nama}), 1), "
                f"(SELECT MAX({kolom_id}) FROM {nama}) IS NOT NULL)"
            ))

    # 4. Cocokkan jumlah baris sumber dan tujuan
    print('Tabel               SQLite  PostgreSQL')
    semua_cocok = True
    with sumber.connect() as baca, tujuan.connect() as cek:
        for nama in URUTAN_TABEL:
            jumlah_sumber = baca.scalar(select(func.count()).select_from(tabel[nama]))
            jumlah_tujuan = cek.scalar(select(func.count()).select_from(tabel[nama]))
            tanda = 'OK' if jumlah_sumber == jumlah_tujuan else 'BEDA!'
            semua_cocok &= jumlah_sumber == jumlah_tujuan
            print(f'{nama:<18}{jumlah_sumber:>7}{jumlah_tujuan:>12}  {tanda}')

    if semua_cocok:
        print('\nMigrasi selesai. Aplikasi sekarang memakai PostgreSQL; file kasir.db boleh disimpan sebagai cadangan.')
    else:
        sys.exit('\nAda jumlah baris yang tidak cocok. Periksa pesan di atas.')


if __name__ == '__main__':
    main()
