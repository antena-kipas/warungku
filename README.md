warungku is software for home grocery (neighborhood grocery)

## Menjalankan di laptop sendiri

### 1. Siapkan alat

- Python 3.11 atau lebih baru
- PostgreSQL (versi 15 ke atas). Saat memasang, kamu akan diminta membuat password
  untuk user `postgres`. Catat password ini, dipakai di langkah 2.

### 2. Membuat database

Buka terminal, lalu masuk ke PostgreSQL sebagai `postgres`
(sesuaikan angka 19 dengan versi PostgreSQL yang kamu pasang):

```
& 'C:\Program Files\PostgreSQL\19\bin\psql.exe' -U postgres -h localhost
```

Masukkan password `postgres`, lalu ketik dua perintah ini.
Ganti `password_database_kamu` dengan password buatanmu sendiri:

```sql
CREATE ROLE warungku LOGIN PASSWORD 'password_database_kamu';
CREATE DATABASE warungku OWNER warungku ENCODING 'UTF8' TEMPLATE template0;
```

Ketik `\q` untuk keluar.

### 3. Isi pengaturan (.env)

```
Copy-Item .env.example .env
```

Buka `.env`, lalu isi `SECRET_KEY`, `DATABASE_URL`, `ADMIN_USERNAME`, dan `ADMIN_PASSWORD`.
Penjelasan tiap isian ada di dalam file `.env.example`.

### 4. Pasang library dan siapkan tabel

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
```

Opsional, untuk melihat tampilan dengan data contoh (24 barang, transaksi 14 hari):
`python seed_demo.py`

### 5. Jalankan

```
python app.py
```

Buka http://localhost:5000 lalu login dengan `ADMIN_USERNAME` dan `ADMIN_PASSWORD` dari `.env`.

## Perintah lain

- `python init_db.py --reset` menghapus SEMUA data lalu membuat tabel dari nol.
- `python migrasi_sqlite_ke_postgres.py` hanya untuk yang masih punya data lama di `kasir.db`
  (versi Warungku sebelum memakai PostgreSQL). Isinya disalin ke PostgreSQL, cukup sekali,
  dan dibatalkan otomatis kalau PostgreSQL tujuan sudah berisi data.

## Susunan kode

| File | Isi |
|---|---|
| `database.py` | Koneksi database dan definisi tabel |
| `routes/auth.py` | Login dan logout |
| `routes/kasir.py` | Dashboard, layar kasir, simpan transaksi (`/api/penjualan`, `/api/dashboard`) |
| `routes/inventori.py` | Data barang dan unggah foto barang |
| `seed_demo.py` | Pengisi data contoh untuk demo |
| `migrasi_sqlite_ke_postgres.py` | Pemindah data dari SQLite ke PostgreSQL (sekali pakai) |
