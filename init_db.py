import sqlite3
from werkzeug.security import generate_password_hash

# 1. Buka koneksi ke database
conn = sqlite3.connect('kasir.db')

# 2. Buka dan baca file schema.sql
with open('schema.sql') as f:
    conn.executescript(f.read())

# 3. Buat cursor untuk mengeksekusi perintah SQL
cur = conn.cursor()

# 4. Buat akun pertama (Akun Admin/Kasir Nenek)
# Kita akan buatkan username 'admin' dengan password 'rahasia'
password_asli = 'Warungku-ada-di-sukabumi'
password_acak = generate_password_hash(password_asli)

cur.execute(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    ('warungku', password_acak, 'admin')
)

# 5. Simpan (Commit) dan tutup koneksi
conn.commit()
conn.close()

print("Database 'kasir.db' berhasil dibuat beserta tabel-tabelnya!")
print(f"Akun berhasil ditambahkan -> Username: admin | Password: {password_asli}")