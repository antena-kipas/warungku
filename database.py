"""Lapisan database Warungku.

Memakai SQLAlchemy supaya kode yang sama bisa jalan di dua tempat:
- SQLite      -> default, untuk coba-coba di laptop (file kasir.db di folder proyek)
- PostgreSQL  -> untuk online (Supabase, Neon, Railway, dll). Cukup isi DATABASE_URL di file .env
"""
import os
from datetime import datetime, timedelta, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Indonesia bagian barat tidak punya jam musim panas, jadi selisihnya selalu +7 jam dari UTC.
WIB = timezone(timedelta(hours=7))


def waktu_sekarang():
    """Waktu saat ini dalam WIB.

    Server cloud biasanya memakai jam UTC. Dengan fungsi ini jam transaksi tetap jam warung,
    baik aplikasinya jalan di laptop maupun di server.
    """
    return datetime.now(WIB).replace(tzinfo=None)


def alamat_database():
    """Menentukan database yang dipakai berdasarkan DATABASE_URL di .env."""
    url = os.getenv('DATABASE_URL', '').strip()
    if not url:
        # Alamat lengkap ke folder proyek, supaya file database-nya selalu sama
        # dari folder mana pun aplikasinya dijalankan.
        folder_proyek = os.path.dirname(os.path.abspath(__file__))
        return 'sqlite:///' + os.path.join(folder_proyek, 'kasir.db').replace('\\', '/')
    # Penyedia cloud memberi alamat berawalan postgres:// atau postgresql://,
    # sedangkan SQLAlchemy perlu tahu driver yang dipakai (psycopg versi 3).
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    if url.startswith('postgresql://'):
        url = 'postgresql+psycopg://' + url[len('postgresql://'):]
    return url


def opsi_engine(url):
    """Pengaturan koneksi tambahan khusus PostgreSQL di cloud."""
    if not url.startswith('postgresql'):
        return {}
    return {
        # Database gratisan sering memutus koneksi yang menganggur; cek dulu sebelum dipakai.
        'pool_pre_ping': True,
        'pool_recycle': 300,
        # Wajib dimatikan kalau lewat connection pooler (PgBouncer) seperti di Supabase.
        'connect_args': {'prepare_threshold': None},
    }


# ---------------------------------------------------------------------------
# Tabel-tabel
# Semua harga disimpan sebagai bilangan bulat rupiah (tidak ada sen).
# ---------------------------------------------------------------------------

class User(db.Model):
    """Hak akses login."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # berupa hash, bukan password asli
    role = db.Column(db.String(20), nullable=False)


class Barang(db.Model):
    """Master barang."""
    __tablename__ = 'barang'

    id_barang = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(64), unique=True)  # boleh kosong untuk barang tanpa barcode
    nama_barang = db.Column(db.String(150), nullable=False)
    gambar = db.Column(db.String(255))  # nama file di static/uploads
    stok = db.Column(db.Integer, nullable=False, default=0)
    harga_beli = db.Column(db.Integer, nullable=False, default=0)
    harga_eceran = db.Column(db.Integer, nullable=False, default=0)
    harga_grosir = db.Column(db.Integer, nullable=False, default=0)

    def harga_untuk(self, tipe):
        """Harga jual sesuai tipe penjualan.

        Kalau harga untuk tipe itu belum diisi (0), pakai harga yang satunya.
        """
        if tipe == 'Grosir':
            return self.harga_grosir or self.harga_eceran
        return self.harga_eceran or self.harga_grosir


class Penjualan(db.Model):
    """Struk kasir."""
    __tablename__ = 'penjualan'

    id_penjualan = db.Column(db.Integer, primary_key=True)
    waktu_transaksi = db.Column(db.DateTime, nullable=False, default=waktu_sekarang, index=True)
    tipe_penjualan = db.Column(db.String(10), nullable=False)  # 'Eceran' atau 'Grosir'
    total_belanja = db.Column(db.Integer, nullable=False)

    detail = db.relationship('DetailPenjualan', backref='penjualan', cascade='all, delete-orphan')


class DetailPenjualan(db.Model):
    """Isi keranjang belanja dari satu struk."""
    __tablename__ = 'detail_penjualan'

    id_detail = db.Column(db.Integer, primary_key=True)
    id_penjualan = db.Column(db.Integer, db.ForeignKey('penjualan.id_penjualan'), nullable=False, index=True)
    id_barang = db.Column(db.Integer, db.ForeignKey('barang.id_barang'), nullable=False, index=True)
    jumlah = db.Column(db.Integer, nullable=False)
    harga_satuan = db.Column(db.Integer, nullable=False)
    # Harga modal saat barang dijual, disimpan supaya untung tetap benar walau harga modal berubah.
    harga_beli_satuan = db.Column(db.Integer, nullable=False, default=0)
    subtotal = db.Column(db.Integer, nullable=False)

    barang = db.relationship('Barang')


class Supplier(db.Model):
    __tablename__ = 'supplier'

    id_supplier = db.Column(db.Integer, primary_key=True)
    nama_supplier = db.Column(db.String(150), nullable=False)
    kontak = db.Column(db.String(100))


class Pembelian(db.Model):
    """Restok gudang."""
    __tablename__ = 'pembelian'

    id_pembelian = db.Column(db.Integer, primary_key=True)
    id_supplier = db.Column(db.Integer, db.ForeignKey('supplier.id_supplier'))
    waktu_pembelian = db.Column(db.DateTime, nullable=False, default=waktu_sekarang)
    total_biaya = db.Column(db.Integer, nullable=False)


class DetailPembelian(db.Model):
    __tablename__ = 'detail_pembelian'

    id_detail_beli = db.Column(db.Integer, primary_key=True)
    id_pembelian = db.Column(db.Integer, db.ForeignKey('pembelian.id_pembelian'), nullable=False)
    id_barang = db.Column(db.Integer, db.ForeignKey('barang.id_barang'), nullable=False)
    jumlah_masuk = db.Column(db.Integer, nullable=False)
    harga_beli_satuan = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=False)
