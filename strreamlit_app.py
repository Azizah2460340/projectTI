import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==================== 0. KONFIGURASI HALAMAN & CSS ====================
st.set_page_config(page_title="MDMS - CV Amal Mulia", layout="wide", page_icon="🏭")

# Custom CSS untuk tampilan profesional
st.markdown("""
<style>
    /* Mengatur background utama */
    .stApp {
        background-color: #f5f7fb;
    }
    
    /* Sidebar dengan gradien */
    .css-1d391kg, .css-12oz5g0 {
        background: linear-gradient(135deg, #1e3c2c 0%, #2e5a3a 100%);
    }
    /* Warna teks sidebar */
    .css-1d391kg .sidebar-content, .css-12oz5g0 .sidebar-content {
        color: white;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #1e3c2c, #2e5a3a);
    }
    /* Judul sidebar */
    .css-1d391kg h1, .css-12oz5g0 h1, .css-1d391kg h2, .css-12oz5g0 h2 {
        color: #f5f5f5;
    }
    /* Tombol logout di sidebar */
    .stButton button {
        background-color: #ff6b6b;
        color: white;
        border-radius: 20px;
        border: none;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #ff4757;
        transform: scale(1.02);
    }
    /* Card untuk metric */
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
        transition: 0.3s;
        border-top: 5px solid #2e8b57;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3c2c;
    }
    .metric-label {
        font-size: 1rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }
    /* Card untuk form */
    .custom-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    /* Tabel */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 40px;
        padding: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 32px;
        padding: 8px 20px;
        background-color: #f1f3f5;
        color: #2c3e50;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e8b57;
        color: white;
    }
    /* Info box */
    .custom-info {
        background: #e9f7ef;
        padding: 1rem;
        border-radius: 16px;
        border-left: 5px solid #2e8b57;
    }
    /* Header judul */
    .main-header {
        background: linear-gradient(120deg, #1e3c2c, #2e8b57);
        padding: 1.2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        color: #adb5bd;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 1. FUNGSI DATABASE ====================
def get_connection():
    return sqlite3.connect('makloon.db', check_same_thread=False)

def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS produk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT UNIQUE,
                    stok INTEGER,
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
                          ('distributor', 'dist123', 'distributor'),
                          ('klien', 'klien123', 'klien')]
            c.executemany("INSERT INTO users VALUES (?,?,?)", users_data)
        c.execute("SELECT COUNT(*) FROM produk")
        if c.fetchone()[0] == 0:
            produk_data = [('Saus Sambal', 500, 15000), ('Sirup Markisa', 300, 25000)]
            c.executemany("INSERT INTO produk (nama, stok, harga_jual) VALUES (?,?,?)", produk_data)
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

# ==================== 2. LOGIN ====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="main-header"><h1>🏭 MDMS - CV Amal Mulia</h1><p>Manufacturing & Distribution Management System</p></div>', unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1,2,1])
    with col_l2:
        with st.container():
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("🔐 Login ke Sistem")
            with st.form("login_form"):
                u = st.text_input("Username", placeholder="Masukkan username")
                p = st.text_input("Password", type="password", placeholder="Masukkan password")
                if st.form_submit_button("🚀 Masuk", use_container_width=True):
                    res = get_df("SELECT role FROM users WHERE username=? AND password=?", (u, p))
                    if not res.empty:
                        st.session_state.authenticated = True
                        st.session_state.username = u
                        st.session_state.role = res.iloc[0]['role']
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah!")
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==================== 3. SIDEBAR & HEADER ====================
# Header dengan selamat datang
st.markdown(f'<div class="main-header"><h2>👋 Selamat datang, {st.session_state.username}</h2><p>{datetime.now().strftime("%A, %d %B %Y")}</p></div>', unsafe_allow_html=True)

# Sidebar dengan informasi pengguna
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/factory.png", width=80)  # Ikon online, jika offline bisa dihapus
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"**Role:** `{st.session_state.role.upper()}`")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown("---")
    st.markdown("### 📌 Menu Navigasi")
    st.caption("Gunakan tab di atas untuk mengakses fitur")

# ==================== 4. DASHBOARD BERDASARKAN ROLE ====================
role = st.session_state.role
username = st.session_state.username

# Helper untuk show metrics
def show_metrics():
    col_met1, col_met2, col_met3 = st.columns(3)
    total_produk = get_df("SELECT COUNT(*) as total FROM produk").iloc[0]['total']
    total_pesanan = get_df("SELECT COUNT(*) as total FROM pesanan").iloc[0]['total']
    total_stok = get_df("SELECT SUM(stok) as total FROM produk").iloc[0]['total']
    with col_met1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_produk}</div><div class="metric-label">📦 Total Produk</div></div>', unsafe_allow_html=True)
    with col_met2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_pesanan}</div><div class="metric-label">📝 Total Pesanan</div></div>', unsafe_allow_html=True)
    with col_met3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_stok}</div><div class="metric-label">📊 Total Stok</div></div>', unsafe_allow_html=True)

# -------------------- ROLE PABRIK --------------------
if role == "pabrik":
    show_metrics()
    st.markdown("---")
    t1, t2, t3, t4 = st.tabs(["📊 Manajemen Stok", "📦 Pesanan Makloon", "🛒 Order Stok Masuk", "➕ Tambah Produk"])
    
    with t1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📋 Inventory Real-time")
        df_stok = get_df("SELECT id, nama, stok, harga_jual FROM produk")
        if not df_stok.empty:
            # Tampilkan dengan highlight untuk stok rendah
            def color_stok(val):
                if val < 50:
                    return 'background-color: #ffcccc'
                elif val < 200:
                    return 'background-color: #fff3cd'
                return ''
            styled_df = df_stok.style.applymap(color_stok, subset=['stok'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            with st.expander("✏️ Edit Stok Produk"):
                pilih = st.selectbox("Pilih produk", df_stok['nama'].tolist())
                stok_baru = st.number_input("Stok baru", min_value=0, step=1)
                if st.button("Update Stok", type="primary"):
                    run_query("UPDATE produk SET stok = ? WHERE nama = ?", (stok_baru, pilih))
                    st.success("✅ Stok berhasil diupdate!")
                    st.rerun()
        else:
            st.info("Belum ada data produk.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with t2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("➕ Input Pesanan Makloon Baru")
        with st.form("add_makloon", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                klien_name = st.text_input("Nama Klien", placeholder="ex: Toko Maju")
                produk_name = st.text_input("Nama Produk", placeholder="ex: Saus Sambal")
            with col_b:
                qty = st.number_input("Jumlah", min_value=1, step=1)
                tgl_now = datetime.now().strftime("%d/%m/%Y %H:%M")
            if st.form_submit_button("💾 Simpan Pesanan", use_container_width=True):
                if klien_name and produk_name:
                    try:
                        run_query("""INSERT INTO pesanan (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                     VALUES (?,?,?,?,?,?,?)""",
                                  (klien_name, produk_name, qty, "Proses Produksi", tgl_now, "makloon", username))
                        st.success("Pesanan makloon tercatat!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal: {e}")
                else:
                    st.warning("Lengkapi data!")
        st.divider()
        st.subheader("📋 Daftar Semua Pesanan")
        df_orders = get_df("SELECT id, klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan FROM pesanan ORDER BY id DESC")
        if not df_orders.empty:
            st.dataframe(df_orders, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada pesanan.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with t3:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("⏳ Order Stok Menunggu Konfirmasi")
        df_waiting = get_df("""SELECT * FROM pesanan WHERE jenis_pesanan='order_stok' AND status='Menunggu Konfirmasi' ORDER BY tanggal_masuk""")
        if df_waiting.empty:
            st.info("Tidak ada order stok yang perlu dikonfirmasi.")
        else:
            for _, row in df_waiting.iterrows():
                with st.expander(f"📦 Order dari **{row['klien']}** - {row['produk']} x {row['jumlah']} (Tgl: {row['tanggal_masuk']})"):
                    stok_tersedia = get_df("SELECT stok FROM produk WHERE nama=?", (row['produk'],)).iloc[0]['stok']
                    st.metric("Stok tersedia", stok_tersedia)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Setujui & Kurangi Stok", key=f"approve_{row['id']}"):
                            if row['jumlah'] <= stok_tersedia:
                                run_query("UPDATE produk SET stok = stok - ? WHERE nama=?", (row['jumlah'], row['produk']))
                                run_query("UPDATE pesanan SET status='Disetujui & Siap Kirim', tanggal_konfirmasi=? WHERE id=?", 
                                          (datetime.now().strftime("%d/%m/%Y %H:%M"), row['id']))
                                st.success("Order disetujui! Stok berkurang.")
                                st.rerun()
                            else:
                                st.error(f"Stok tidak cukup! Tersedia {stok_tersedia}.")
                    with col2:
                        if st.button(f"❌ Tolak Order", key=f"reject_{row['id']}"):
                            run_query("UPDATE pesanan SET status='Ditolak', tanggal_konfirmasi=? WHERE id=?", 
                                      (datetime.now().strftime("%d/%m/%Y %H:%M"), row['id']))
                            st.warning("Order ditolak.")
                            st.rerun()
        st.divider()
        st.subheader("📜 Riwayat Konfirmasi Order Stok")
        df_history = get_df("""SELECT id, klien, produk, jumlah, status, tanggal_konfirmasi FROM pesanan 
                               WHERE jenis_pesanan='order_stok' AND status != 'Menunggu Konfirmasi'""")
        if not df_history.empty:
            st.dataframe(df_history, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with t4:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("➕ Registrasi Produk Baru")
        with st.form("new_product"):
            np = st.text_input("Nama Produk", placeholder="ex: Kecap Manis")
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                sp = st.number_input("Stok Awal", min_value=0, step=1)
            with col_h2:
                hp = st.number_input("Harga Jual (Rp)", min_value=0, step=1000)
            if st.form_submit_button("Tambah Produk", use_container_width=True):
                if np:
                    try:
                        run_query("INSERT INTO produk (nama, stok, harga_jual) VALUES (?,?,?)", (np, sp, hp))
                        st.success(f"Produk '{np}' berhasil ditambahkan!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Nama produk sudah ada.")
                else:
                    st.warning("Nama produk harus diisi.")
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- ROLE DISTRIBUTOR --------------------
elif role == "distributor":
    show_metrics()
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📦 Lihat Stok", "🛒 Order Stok", "📋 Riwayat Order Saya"])
    
    with tab1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("Stok Produk Tersedia")
        df_stok = get_df("SELECT nama, stok, harga_jual FROM produk")
        if not df_stok.empty:
            st.dataframe(df_stok.style.format({'harga_jual': 'Rp {:,.0f}'}), use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada produk.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("Buat Order Stok")
        produk_list = get_df("SELECT nama, stok FROM produk")
        if not produk_list.empty:
            with st.form("order_stok_form"):
                pilih = st.selectbox("Pilih Produk", produk_list['nama'].tolist())
                stok_tersedia = produk_list[produk_list['nama']==pilih]['stok'].values[0]
                st.caption(f"Stok saat ini: **{stok_tersedia}**")
                jumlah = st.number_input("Jumlah Order", min_value=1, max_value=1000, step=1)
                if st.form_submit_button("Kirim Order", use_container_width=True):
                    if jumlah <= stok_tersedia:
                        tgl = datetime.now().strftime("%d/%m/%Y %H:%M")
                        run_query("""INSERT INTO pesanan (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                     VALUES (?,?,?,?,?,?,?)""",
                                  (username, pilih, jumlah, "Menunggu Konfirmasi", tgl, "order_stok", username))
                        st.success("Order berhasil dikirim! Menunggu konfirmasi pabrik.")
                        st.rerun()
                    else:
                        st.error(f"Stok tidak cukup. Maksimal {stok_tersedia}.")
        else:
            st.warning("Belum ada produk yang tersedia.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("Riwayat Pesanan Saya")
        df_riwayat = get_df("""SELECT id, produk, jumlah, status, tanggal_masuk, jenis_pesanan, tanggal_konfirmasi
                               FROM pesanan WHERE created_by=? ORDER BY tanggal_masuk DESC""", (username,))
        if df_riwayat.empty:
            st.info("Belum ada pesanan.")
        else:
            st.dataframe(df_riwayat, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- ROLE KLIEN --------------------
elif role == "klien":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Total Pesanan Makloon", get_df("SELECT COUNT(*) FROM pesanan WHERE klien=? AND jenis_pesanan='makloon'", (username,)).iloc[0,0])
    with col2:
        st.metric("🛒 Order Stok Saya", get_df("SELECT COUNT(*) FROM pesanan WHERE created_by=? AND jenis_pesanan='order_stok'", (username,)).iloc[0,0])
    with col3:
        st.metric("⏳ Dalam Proses", get_df("SELECT COUNT(*) FROM pesanan WHERE (klien=? OR created_by=?) AND status NOT IN ('Disetujui & Siap Kirim','Ditolak')", (username,username)).iloc[0,0])
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📋 Status Pesanan Makloon", "🛒 Order Stok", "📜 Riwayat Lengkap"])
    
    with tab1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        df_mak = get_df("""SELECT produk, jumlah, status, tanggal_masuk FROM pesanan 
                           WHERE klien=? AND jenis_pesanan='makloon' ORDER BY tanggal_masuk DESC""", (username,))
        if df_mak.empty:
            st.info("Tidak ada pesanan makloon.")
        else:
            st.dataframe(df_mak, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("Beli Stok Langsung")
        produk_list = get_df("SELECT nama, stok, harga_jual FROM produk")
        if not produk_list.empty:
            with st.form("order_stok_klien"):
                pilih = st.selectbox("Produk", produk_list['nama'].tolist())
                stok_tersedia = produk_list[produk_list['nama']==pilih]['stok'].values[0]
                st.caption(f"Stok: {stok_tersedia}")
                jumlah = st.number_input("Jumlah", 1, 1000)
                if st.form_submit_button("Order Sekarang", use_container_width=True):
                    if jumlah <= stok_tersedia:
                        tgl = datetime.now().strftime("%d/%m/%Y %H:%M")
                        run_query("""INSERT INTO pesanan (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                     VALUES (?,?,?,?,?,?,?)""",
                                  (username, pilih, jumlah, "Menunggu Konfirmasi", tgl, "order_stok", username))
                        st.success("Order stok terkirim!")
                        st.rerun()
                    else:
                        st.error(f"Stok tidak cukup.")
        else:
            st.warning("Belum ada produk.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        df_all = get_df("""SELECT id, produk, jumlah, status, tanggal_masuk, jenis_pesanan FROM pesanan 
                           WHERE created_by=? OR (klien=? AND jenis_pesanan='makloon')
                           ORDER BY tanggal_masuk DESC""", (username,username))
        if df_all.empty:
            st.info("Tidak ada riwayat.")
        else:
            st.dataframe(df_all, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown('<div class="footer">© 2025 CV Amal Mulia - Manufacturing & Distribution System</div>', unsafe_allow_html=True)
