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
app.secret_key = os.getenv('SECRET_KEY', 'super_rahasia_default_key_yang_harus_diganti') # Ambil dari .env, sediakan nilai default
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Database: SQLite kalau DATABASE_URL kosong, PostgreSQL kalau diisi
alamat_db = alamat_database()
app.config['SQLALCHEMY_DATABASE_URI'] = alamat_db
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = opsi_engine(alamat_db)
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
