from flask import Flask
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Mengimpor blueprints dari folder routes
from routes.auth import auth_bp
from routes.kasir import kasir_bp
from routes.inventori import inventori_bp

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super_rahasia_default_key_yang_harus_diganti') # Ambil dari .env, sediakan nilai default
# app.secret_key = 'kunci_rahasia_warung_nenek' # Ganti dengan yang aman nanti (original comment)

# Mendaftarkan blueprints ke dalam aplikasi utama
app.register_blueprint(auth_bp)
app.register_blueprint(kasir_bp)
app.register_blueprint(inventori_bp)

if __name__ == '__main__':
    app.run(debug=True)