DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS detail_pembelian;
DROP TABLE IF EXISTS pembelian;
DROP TABLE IF EXISTS supplier;
DROP TABLE IF EXISTS detail_penjualan;
DROP TABLE IF EXISTS penjualan;
DROP TABLE IF EXISTS barang;

-- Tabel untuk hak akses login
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

-- Tabel Master Barang
CREATE TABLE barang (
    id_barang INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    nama_barang TEXT NOT NULL,
    gambar TEXT,
    stok INTEGER DEFAULT 0,
    harga_beli REAL NOT NULL,
    harga_eceran REAL NOT NULL,
    harga_grosir REAL NOT NULL
);

-- Tabel Penjualan (Struk Kasir)
CREATE TABLE penjualan (
    id_penjualan INTEGER PRIMARY KEY AUTOINCREMENT,
    waktu_transaksi DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipe_penjualan TEXT NOT NULL,
    total_belanja REAL NOT NULL
);

-- Tabel Detail Penjualan (Isi keranjang belanja)
CREATE TABLE detail_penjualan (
    id_detail INTEGER PRIMARY KEY AUTOINCREMENT,
    id_penjualan INTEGER,
    id_barang INTEGER,
    jumlah INTEGER NOT NULL,
    harga_satuan REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (id_penjualan) REFERENCES penjualan (id_penjualan),
    FOREIGN KEY (id_barang) REFERENCES barang (id_barang)
);

-- Tabel Supplier
CREATE TABLE supplier (
    id_supplier INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_supplier TEXT NOT NULL,
    kontak TEXT
);

-- Tabel Pembelian (Restok Gudang)
CREATE TABLE pembelian (
    id_pembelian INTEGER PRIMARY KEY AUTOINCREMENT,
    id_supplier INTEGER,
    waktu_pembelian DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_biaya REAL NOT NULL,
    FOREIGN KEY (id_supplier) REFERENCES supplier (id_supplier)
);

-- Tabel Detail Pembelian
CREATE TABLE detail_pembelian (
    id_detail_beli INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pembelian INTEGER,
    id_barang INTEGER,
    jumlah_masuk INTEGER NOT NULL,
    harga_beli_satuan REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (id_pembelian) REFERENCES pembelian (id_pembelian),
    FOREIGN KEY (id_barang) REFERENCES barang (id_barang)
);