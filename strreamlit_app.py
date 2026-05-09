import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(page_title="MDMS - CV Amal Mulia", layout="wide", page_icon="🌿")

# ==================== CSS TEMA HIJAU & EMAS ====================
st.markdown("""
<style>
    /* Warna dasar */
    :root {
        --hijau: #1e3c2c;
        --emas: #D4AF37;
    }
    /* Background utama */
    .stApp {
        background-color: #f5f0e6;
    }
    /* Sidebar hijau gelap */
    .css-1d391kg, .css-12oz5g0 {
        background-color: var(--hijau) !important;
    }
    .sidebar-content {
        color: white;
    }
    /* Judul sidebar */
    .css-1d391kg h2, .css-12oz5g0 h2 {
        color: var(--emas) !important;
    }
    /* Tombol umum */
    .stButton button {
        background-color: var(--emas);
        color: var(--hijau);
        border-radius: 30px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #b8942e;
        color: white;
    }
    /* Card putih untuk konten */
    .white-card {
        background-color: white;
        border-radius: 24px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-top: 5px solid var(--emas);
    }
    /* Metric */
    .metric-box {
        background: linear-gradient(135deg, #ffffff, #f9f7f0);
        border-radius: 20px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e0d5b5;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: var(--hijau);
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0ede5;
        border-radius: 40px;
        padding: 8px 24px;
        font-weight: 600;
        color: var(--hijau);
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--hijau);
        color: white;
    }
    /* Tabel */
    .dataframe {
        background: white;
        border-radius: 16px;
        overflow: hidden;
    }
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: #7c6e3c;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOGO PERUSAHAAN (opsional) ====================
# Letakkan file logo.png di folder yang sama, atau ganti dengan URL gambar
try:
    st.sidebar.image("logo.png", use_column_width=True)  # ganti dengan path logo Anda
except:
    st.sidebar.markdown("## 🌿 **CV AMAL MULIA**")
    st.sidebar.markdown("<hr style='border-color:#D4AF37'>", unsafe_allow_html=True)

# ==================== FUNGSI DATABASE ====================
def get_connection():
    return sqlite3.connect('makloon.db', check_same_thread=False)

def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS produk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT UNIQUE,
                    stok INTEGER,
                    stok_minimum INTEGER DEFAULT 50,
                    harga_jual INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pesanan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    klien TEXT,
                    produk TEXT,
                    jumlah INTEGER,
                    status TEXT,
                    tanggal_masuk TEXT,
                    jenis_pesanan TEXT,
                    created_by TEXT,
                    tanggal_konfirmasi TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    role TEXT)''')
        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()[0] == 0:
            users_data = [('pabrik', 'pabrik123', 'pabrik'),
                          ('distributor1', 'dist123', 'distributor'),
                          ('klien1', 'klien123', 'klien')]
            c.executemany("INSERT INTO users VALUES (?,?,?)", users_data)
        c.execute("SELECT COUNT(*) FROM produk")
        if c.fetchone()[0] == 0:
            produk_data = [('Sari Kurma Alami', 500, 50, 15000),
                           ('Sari Kurma Madu', 300, 50, 25000)]
            c.executemany("INSERT INTO produk (nama, stok, stok_minimum, harga_jual) VALUES (?,?,?,?)", produk_data)
        conn.commit()

def run_query(query, params=()):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()

def get_df(query, params=()):
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

init_db()

# ==================== LOGIN & REGISTER ====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏭 MDMS - CV Amal Mulia")
    menu = st.radio("", ["Masuk", "Daftar"], horizontal=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if menu == "Masuk":
            with st.form("login"):
                st.subheader("🔐 Login")
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Masuk", use_container_width=True):
                    res = get_df("SELECT role FROM users WHERE username=? AND password=?", (u, p))
                    if not res.empty:
                        st.session_state.authenticated = True
                        st.session_state.username = u
                        st.session_state.role = res.iloc[0]['role']
                        st.rerun()
                    else:
                        st.error("Username atau password salah")
        else:
            with st.form("register"):
                st.subheader("📝 Daftar")
                new_u = st.text_input("Username baru")
                new_p = st.text_input("Password", type="password")
                role = st.selectbox("Daftar sebagai", ["distributor", "klien"])
                if st.form_submit_button("Daftar", use_container_width=True):
                    if new_u and new_p:
                        cek = get_df("SELECT * FROM users WHERE username=?", (new_u,))
                        if cek.empty:
                            run_query("INSERT INTO users VALUES (?,?,?)", (new_u, new_p, role))
                            st.success("Akun berhasil dibuat, silakan login")
                        else:
                            st.error("Username sudah terdaftar")
    st.stop()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown(f"### 👤 **{st.session_state.username}**")
    st.markdown(f"**Role:** `{st.session_state.role.upper()}`")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ==================== AREA UTAMA ====================
# Card putih untuk selamat datang
st.markdown(f"""
<div class="white-card">
    <h2>🌿 Selamat datang, {st.session_state.username}</h2>
    <p>{datetime.now().strftime('%A, %d %B %Y')}</p>
</div>
""", unsafe_allow_html=True)

role = st.session_state.role
username = st.session_state.username

# ============= DASHBOARD PABRIK =============
if role == "pabrik":
    # Metrics
    total_stok = get_df("SELECT SUM(stok) FROM produk").iloc[0,0] or 0
    pesanan_makloon = get_df("SELECT SUM(jumlah) FROM pesanan WHERE jenis_pesanan='makloon' AND status='Proses Produksi'").iloc[0,0] or 0
    order_wait = get_df("SELECT SUM(jumlah) FROM pesanan WHERE jenis_pesanan='order_stok' AND status='Menunggu Konfirmasi'").iloc[0,0] or 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-box"><div class="metric-value">{total_stok}</div><div>📦 Total Stok</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><div class="metric-value">{pesanan_makloon}</div><div>🏭 Pesanan Makloon</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><div class="metric-value">{order_wait}</div><div>⏳ Order Menunggu</div></div>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📦 Manajemen Stok", "🏭 Pesanan Makloon", "🛒 Order Stok Masuk"])
    
    with tab1:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.subheader("Stok Produk")
        df_produk = get_df("SELECT nama, stok, stok_minimum, harga_jual FROM produk")
        st.dataframe(df_produk, use_container_width=True, hide_index=True)
        
        with st.expander("✏️ Update Stok"):
            pilih = st.selectbox("Produk", df_produk['nama'])
            stok_baru = st.number_input("Stok baru", min_value=0, step=1)
            if st.button("Perbarui Stok"):
                run_query("UPDATE produk SET stok = ? WHERE nama = ?", (stok_baru, pilih))
                st.success("Stok diperbarui")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        st.subheader("Tambah Pesanan Makloon")
        with st.form("form_makloon"):
            klien = st.text_input("Nama Klien")
            produk = st.selectbox("Produk", df_produk['nama'])
            jumlah = st.number_input("Jumlah", 1, 10000)
            if st.form_submit_button("Simpan"):
                if klien:
                    run_query("""INSERT INTO pesanan (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                 VALUES (?,?,?,?,?,?,?)""",
                              (klien, produk, jumlah, "Proses Produksi", datetime.now().strftime("%Y-%m-%d %H:%M"), "makloon", username))
                    st.success("Pesanan tersimpan")
                    st.rerun()
        st.divider()
        df_mak = get_df("SELECT klien, produk, jumlah, status, tanggal_masuk FROM pesanan WHERE jenis_pesanan='makloon'")
        st.dataframe(df_mak, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="white-card">', unsafe_allow_html=True)
        df_order = get_df("SELECT * FROM pesanan WHERE jenis_pesanan='order_stok' AND status='Menunggu Konfirmasi'")
        if df_order.empty:
            st.info("Tidak ada order menunggu")
        else:
            for _, row in df_order.iterrows():
                with st.expander(f"Order dari {row['klien']} - {row['produk']} x {row['jumlah']}"):
                    stok_skrg = get_df("SELECT stok FROM produk WHERE nama=?", (row['produk'],)).iloc[0]['stok']
                    colA, colB = st.columns(2)
                    with colA:
                        if st.button("✅ Setujui", key=f"ok_{row['id']}"):
                            if row['jumlah'] <= stok_skrg:
                                run_query("UPDATE produk SET stok = stok - ? WHERE nama=?", (row['jumlah'], row['produk']))
                                run_query("UPDATE pesanan SET status='Disetujui', tanggal_konfirmasi=? WHERE id=?", (datetime.now().strftime("%Y-%m-%d %H:%M"), row['id']))
                                st.success("Order disetujui, stok berkurang")
                                st.rerun()
                            else:
                                st.error("Stok tidak cukup")
                    with colB:
                        if st.button("❌ Tolak", key=f"no_{row['id']}"):
                            run_query("UPDATE pesanan SET status='Ditolak' WHERE id=?", (row['id'],))
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============= DASHBOARD DISTRIBUTOR =============
elif role == "distributor":
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.subheader("🏪 Portal Distributor")
    tabA, tabB = st.tabs(["Lihat Stok", "Order Stok"])
    with tabA:
        df = get_df("SELECT nama, stok, harga_jual FROM produk")
        st.dataframe(df, use_container_width=True, hide_index=True)
    with tabB:
        produk = st.selectbox("Produk", get_df("SELECT nama FROM produk")['nama'])
        stok_tersedia = get_df("SELECT stok FROM produk WHERE nama=?", (produk,)).iloc[0]['stok']
        st.write(f"Stok tersedia: {stok_tersedia}")
        jumlah = st.number_input("Jumlah", 1, stok_tersedia)
        if st.button("Kirim Order"):
            run_query("""INSERT INTO pesanan (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                         VALUES (?,?,?,?,?,?,?)""",
                      (username, produk, jumlah, "Menunggu Konfirmasi", datetime.now().strftime("%Y-%m-%d %H:%M"), "order_stok", username))
            st.success("Order dikirim")
    st.markdown('</div>', unsafe_allow_html=True)

# ============= DASHBOARD KLIEN =============
elif role == "klien":
    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.subheader("🤝 Klien")
    tabC, tabD = st.tabs(["Status Pesanan Makloon", "Order Stok"])
    with tabC:
        df = get_df("SELECT produk, jumlah, status, tanggal_masuk FROM pesanan WHERE klien=? AND jenis_pesanan='makloon'", (username,))
        if df.empty:
            st.info("Belum ada pesanan makloon")
        else:
            st.dataframe(df, use_container_width=True)
    with tabD:
        produk = st.selectbox("Pilih Produk", get_df("SELECT nama FROM produk")['nama'])
        stok = get_df("SELECT stok, harga_jual FROM produk WHERE nama=?", (produk,)).iloc[0]
        st.metric("Stok tersedia", stok['stok'])
        st.caption(f"Harga: Rp {stok['harga_jual']:,.0f}")
        jumlah = st.number_input("Jumlah", 1, stok['stok'])
        if st.button("Order Sekarang"):
            run_query("""INSERT INTO pesanan (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                         VALUES (?,?,?,?,?,?,?)""",
                      (username, produk, jumlah, "Menunggu Konfirmasi", datetime.now().strftime("%Y-%m-%d %H:%M"), "order_stok", username))
            st.success("Order stok dikirim")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">© 2025 CV Amal Mulia — Sistem Manajemen Produksi & Distribusi</div>', unsafe_allow_html=True)
