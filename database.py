import sqlite3

def get_db_connection():
    # Akan membuat file kasir.db secara otomatis jika belum ada
    conn = sqlite3.connect('kasir.db')
    # Mengatur agar hasil query berbentuk dictionary (seperti dict di MySQL)
    conn.row_factory = sqlite3.Row
    return conn