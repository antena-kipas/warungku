from datetime import timedelta

from flask import Blueprint, jsonify, render_template, request
from sqlalchemy.orm import joinedload, selectinload

from database import db, waktu_sekarang, Barang, Penjualan, DetailPenjualan
from helpers import url_gambar, wajib_login

kasir_bp = Blueprint('kasir', __name__)

# Barang dengan stok segini atau kurang dianggap "menipis" di dashboard
BATAS_STOK_MENIPIS = 5

NAMA_HARI = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
NAMA_BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
              'Agustus', 'September', 'Oktober', 'November', 'Desember']


def barang_ke_dict(barang):
    """Bentuk data barang yang dikirim ke layar kasir."""
    return {
        'id': barang.id_barang,
        'barcode': barang.barcode or '',
        'nama': barang.nama_barang,
        'gambar': url_gambar(barang.gambar),
        'stok': barang.stok,
        'harga_eceran': barang.harga_eceran,
        'harga_grosir': barang.harga_grosir,
    }


def ringkasan_dashboard():
    """Mengumpulkan semua angka yang tampil di dashboard.

    Data 7 hari terakhir diambil sekali, lalu dihitung di Python. Untuk ukuran warung
    (puluhan struk per hari) ini ringan dan kodenya lebih mudah dibaca.
    """
    sekarang = waktu_sekarang()
    awal_hari_ini = sekarang.replace(hour=0, minute=0, second=0, microsecond=0)
    awal_kemarin = awal_hari_ini - timedelta(days=1)
    awal_7_hari = awal_hari_ini - timedelta(days=6)

    daftar_penjualan = (
        Penjualan.query
        .options(selectinload(Penjualan.detail).joinedload(DetailPenjualan.barang))
        .filter(Penjualan.waktu_transaksi >= awal_7_hari)
        .order_by(Penjualan.waktu_transaksi.desc(), Penjualan.id_penjualan.desc())
        .all()
    )

    # Wadah hitungan
    hari_ini = {'pendapatan': 0, 'transaksi': 0, 'untung': 0, 'barang_terjual': 0}
    kemarin_jam_segini = 0
    per_hari = {}
    for i in range(7):
        tanggal = (awal_7_hari + timedelta(days=i)).date()
        per_hari[tanggal] = {
            'tanggal': tanggal.isoformat(),
            'label': 'Hari ini' if i == 6 else NAMA_HARI[tanggal.weekday()],
            'keterangan': f'{NAMA_HARI[tanggal.weekday()]}, {tanggal.day} {NAMA_BULAN[tanggal.month - 1]}',
            'pendapatan': 0,
            'transaksi': 0,
        }
    per_jam = [0] * 24
    terlaris = {}

    for penjualan in daftar_penjualan:
        waktu = penjualan.waktu_transaksi
        hari = per_hari.get(waktu.date())
        if hari is None:
            continue
        hari['pendapatan'] += penjualan.total_belanja
        hari['transaksi'] += 1
        per_jam[waktu.hour] += 1

        ini_hari_ini = waktu >= awal_hari_ini
        if ini_hari_ini:
            hari_ini['pendapatan'] += penjualan.total_belanja
            hari_ini['transaksi'] += 1
        # Pembanding yang adil: penjualan kemarin sampai jam yang sama dengan sekarang
        elif awal_kemarin <= waktu <= sekarang - timedelta(days=1):
            kemarin_jam_segini += penjualan.total_belanja

        for baris in penjualan.detail:
            if ini_hari_ini:
                hari_ini['untung'] += (baris.harga_satuan - baris.harga_beli_satuan) * baris.jumlah
                hari_ini['barang_terjual'] += baris.jumlah
            catatan = terlaris.setdefault(baris.id_barang, {
                'nama': baris.barang.nama_barang, 'jumlah': 0, 'pendapatan': 0,
            })
            catatan['jumlah'] += baris.jumlah
            catatan['pendapatan'] += baris.subtotal

    # Persen naik/turun dibanding kemarin (None kalau kemarin belum ada penjualan)
    selisih_persen = None
    if kemarin_jam_segini > 0:
        selisih_persen = round((hari_ini['pendapatan'] - kemarin_jam_segini) / kemarin_jam_segini * 100)

    # Rentang jam di grafik: minimal 05.00-22.00, melebar kalau ada transaksi di luar itu
    jam_terisi = [jam for jam, jumlah in enumerate(per_jam) if jumlah]
    jam_awal = min([5] + jam_terisi)
    jam_akhir = max([22] + jam_terisi)

    stok_menipis = (
        Barang.query.filter(Barang.stok <= BATAS_STOK_MENIPIS)
        .order_by(Barang.stok, Barang.nama_barang).all()
    )

    return {
        'tanggal': f'{NAMA_HARI[sekarang.weekday()]}, {sekarang.day} {NAMA_BULAN[sekarang.month - 1]} {sekarang.year}',
        'diperbarui': sekarang.strftime('%H.%M.%S'),
        'hari_ini': hari_ini,
        'kemarin_jam_segini': kemarin_jam_segini,
        'selisih_persen': selisih_persen,
        'per_hari': list(per_hari.values()),
        'per_jam': [{'jam': jam, 'transaksi': per_jam[jam]} for jam in range(jam_awal, jam_akhir + 1)],
        'terlaris': sorted(terlaris.values(), key=lambda b: b['jumlah'], reverse=True)[:5],
        'stok_menipis': [{'nama': b.nama_barang, 'stok': b.stok} for b in stok_menipis[:8]],
        'jumlah_stok_menipis': len(stok_menipis),
        'jumlah_barang': Barang.query.count(),
        'transaksi_terakhir': [{
            'id': p.id_penjualan,
            'tanggal': 'Hari ini' if p.waktu_transaksi >= awal_hari_ini else f'{p.waktu_transaksi.day} {NAMA_BULAN[p.waktu_transaksi.month - 1][:3]}',
            'jam': p.waktu_transaksi.strftime('%H.%M'),
            'tipe': p.tipe_penjualan,
            'jumlah_barang': sum(d.jumlah for d in p.detail),
            'total': p.total_belanja,
        } for p in daftar_penjualan[:8]],
    }


# Rute untuk Dashboard (Analitik & Menu)
@kasir_bp.route('/dashboard')
@wajib_login
def dashboard():
    return render_template('dashboard.html', data=ringkasan_dashboard())


# Data dashboard dalam bentuk JSON. Dipakai halaman dashboard untuk memperbarui angka
# secara otomatis tanpa memuat ulang halaman.
@kasir_bp.route('/api/dashboard')
@wajib_login
def api_dashboard():
    return jsonify(ringkasan_dashboard())


# Rute KHUSUS untuk Layar Kasir / Melayani Pembeli
@kasir_bp.route('/transaksi')
@wajib_login
def transaksi():
    barang_list = Barang.query.order_by(Barang.nama_barang).all()
    return render_template('kasir.html', barang=[barang_ke_dict(b) for b in barang_list])


# Menyimpan satu transaksi dari layar kasir
@kasir_bp.route('/api/penjualan', methods=['POST'])
@wajib_login
def simpan_penjualan():
    data = request.get_json(silent=True) or {}
    tipe = 'Grosir' if data.get('tipe') == 'Grosir' else 'Eceran'

    # 1. Rapikan isi keranjang: gabungkan barang yang sama, tolak jumlah yang tidak masuk akal
    jumlah_per_barang = {}
    for item in data.get('items') or []:
        try:
            id_barang = int(item.get('id_barang'))
            jumlah = int(item.get('jumlah'))
        except (TypeError, ValueError, AttributeError):
            return jsonify(ok=False, pesan='Isi keranjang tidak terbaca.'), 400
        if jumlah < 1 or jumlah > 9999:
            return jsonify(ok=False, pesan='Jumlah barang tidak wajar.'), 400
        jumlah_per_barang[id_barang] = jumlah_per_barang.get(id_barang, 0) + jumlah

    if not jumlah_per_barang:
        return jsonify(ok=False, pesan='Keranjang masih kosong.'), 400

    # 2. Ambil barangnya dari database. Harga SELALU diambil dari database,
    #    bukan dari kiriman layar kasir, supaya tidak bisa diubah-ubah dari browser.
    barang_list = Barang.query.filter(Barang.id_barang.in_(list(jumlah_per_barang))).all()
    peta_barang = {b.id_barang: b for b in barang_list}
    if len(peta_barang) != len(jumlah_per_barang):
        return jsonify(ok=False, pesan='Ada barang yang sudah tidak terdaftar. Muat ulang halaman kasir.'), 400

    # 3. Susun struk
    penjualan = Penjualan(waktu_transaksi=waktu_sekarang(), tipe_penjualan=tipe, total_belanja=0)
    rincian = []
    for id_barang, jumlah in jumlah_per_barang.items():
        barang = peta_barang[id_barang]
        harga = barang.harga_untuk(tipe)
        subtotal = harga * jumlah
        penjualan.detail.append(DetailPenjualan(
            id_barang=id_barang,
            jumlah=jumlah,
            harga_satuan=harga,
            harga_beli_satuan=barang.harga_beli,
            subtotal=subtotal,
        ))
        penjualan.total_belanja += subtotal
        # Stok dikurangi tapi penjualan tidak ditolak walau catatan stoknya kurang:
        # barangnya nyata ada di tangan pembeli, berarti catatan stoknya yang perlu dibetulkan.
        barang.stok = max(barang.stok - jumlah, 0)
        rincian.append({'nama': barang.nama_barang, 'jumlah': jumlah, 'harga_satuan': harga, 'subtotal': subtotal})

    db.session.add(penjualan)
    db.session.commit()

    return jsonify(
        ok=True,
        id_penjualan=penjualan.id_penjualan,
        waktu=penjualan.waktu_transaksi.strftime('%d/%m/%Y %H.%M'),
        tipe=tipe,
        total=penjualan.total_belanja,
        items=rincian,
        stok={str(b.id_barang): b.stok for b in barang_list},
    )
