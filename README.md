warungku is software for home grocery (neighborhood grocery)

## Menjalankan di laptop

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python app.py
```

Buka http://localhost:5000 lalu login dengan akun yang dicetak oleh `init_db.py`.

Tanpa pengaturan apa pun, data disimpan di SQLite (file `kasir.db`).
Untuk melihat tampilan dengan data contoh (24 barang, transaksi 14 hari): `python seed_demo.py`.

## Memakai PostgreSQL (online)

1. Buat database PostgreSQL (misalnya di Supabase atau Neon) dan salin alamat koneksinya.
2. Salin `.env.example` menjadi `.env`, isi `DATABASE_URL`, `SECRET_KEY`, dan `ADMIN_PASSWORD`.
3. Jalankan `python init_db.py` sekali untuk membuat tabel dan akun login.

`python init_db.py --reset` menghapus SEMUA data lalu membuat tabel dari nol.

## Susunan kode

| File | Isi |
|---|---|
| `database.py` | Koneksi database dan definisi tabel |
| `routes/auth.py` | Login dan logout |
| `routes/kasir.py` | Dashboard, layar kasir, simpan transaksi (`/api/penjualan`, `/api/dashboard`, `/api/barang`) |
| `routes/inventori.py` | Data barang dan unggah foto barang |
| `seed_demo.py` | Pengisi data contoh untuk demo |
