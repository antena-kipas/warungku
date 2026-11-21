from flask import Flask, flash, redirect, request, url_for
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()

from database import db, alamat_database, opsi_engine
from helpers import format_rupiah, url_gambar

# Mengimpor blueprints dari folder routes
from routes.auth import auth_bp
from routes.kasir import kasir_bp
from routes.inventori import inventori_bp

app = Flask(__name__)

# Kunci untuk mengamankan sesi login. Wajib diisi di .env, tidak ada nilai bawaan di kode.
app.secret_key = os.getenv('SECRET_KEY', '').strip()
if not app.secret_key:
    raise SystemExit('Gagal: SECRET_KEY belum diisi di file .env. Lihat contohnya di .env.example.')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Database: PostgreSQL di komputer kasir, alamatnya dari DATABASE_URL di .env
app.config['SQLALCHEMY_DATABASE_URI'] = alamat_database()
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = opsi_engine()
db.init_app(app)

# Batas ukuran upload gambar barang
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB

# Bisa dipakai di semua template: {{ harga|rupiah }} dan {{ url_gambar(item.gambar) }}
app.jinja_env.filters['rupiah'] = format_rupiah
app.jinja_env.globals['url_gambar'] = url_gambar

# Mendaftarkan blueprints ke dalam aplikasi utama
app.register_blueprint(auth_bp)
app.register_blueprint(kasir_bp)
app.register_blueprint(inventori_bp)


@app.errorhandler(413)
def berkas_terlalu_besar(error):
    flash('Gagal: ukuran gambar terlalu besar (maksimal 8 MB).', 'danger')
    return redirect(request.referrer or url_for('inventori.daftar_produk'))


if __name__ == '__main__':
    app.run(debug=True)
