import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import base64
from pathlib import Path

# ==================== 0. KONFIGURASI HALAMAN & CSS ====================
st.set_page_config(page_title="ABCFN - CV Amal Mulia", layout="wide", page_icon="🏭")

# Fungsi untuk encode gambar ke base64 (untuk background)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Cek apakah file gambar background ada, jika tidak pakai warna solid
try:
    img_path = Path("background.jpg")  # Ganti dengan nama file background Anda
    if img_path.exists():
        bin_str = get_base64_of_bin_file(img_path)
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        /* Overlay agar teks lebih terbaca */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.85);
            z-index: -1;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
except:
    pass

# Custom CSS untuk tampilan profesional
st.markdown("""
<style>
    /* Sidebar dengan warna gelap elegan */
    .css-1d391kg, .css-12oz5g0 {
        background: linear-gradient(135deg, #1e3c2c 0%, #2e5a3a 100%);
    }
    /* Card untuk metric */
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #2e8b57;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1e3c2c;
    }
    /* Custom card untuk form */
    .custom-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    /* Styling tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 40px;
        padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 32px;
        padding: 8px 20px;
        background-color: #f1f3f5;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2e8b57;
        color: white;
    }
    /* Tabel dengan border radius */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }
    /* Teks warning untuk stok rendah */
    .stock-warning {
        background-color: #ffebee;
        padding: 10px;
        border-radius: 10px;
        border-left: 4px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 1. FUNGSI DATABASE ====================
def get_connection():
    return sqlite3.connect('makloon.db', check_same_thread=False)

def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        # Tabel Produk
        c.execute('''CREATE TABLE IF NOT EXISTS produk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT UNIQUE,
                    stok INTEGER,
                    stok_minimum INTEGER DEFAULT 50,
                    harga_jual INTEGER)''')
        # Tabel Pesanan (diperluas)
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
        # Tabel Users
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    role TEXT)''')
        # Tabel Stok Distributor (tracking stok yang sudah dikonfirmasi ke distributor)
        c.execute('''CREATE TABLE IF NOT EXISTS stok_distributor (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    distributor TEXT,
                    produk TEXT,
                    jumlah INTEGER,
                    tanggal_ambil TEXT)''')
        
        # Data default
        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()[0] == 0:
            users_data = [('pabrik', 'pabrik123', 'pabrik'),
                          ('distributor1', 'dist123', 'distributor'),
                          ('distributor2', 'dist123', 'distributor'),
                          ('klien1', 'klien123', 'klien'),
                          ('klien2', 'klien123', 'klien')]
            c.executemany("INSERT INTO users VALUES (?,?,?)", users_data)
        
        c.execute("SELECT COUNT(*) FROM produk")
        if c.fetchone()[0] == 0:
            produk_data = [('Sari Kurma Alami', 500, 50, 15000),
                           ('Sari Kurma Madu', 300, 50, 25000),
                           ('Sari Kurma Herbal', 100, 80, 35000)]
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

# ==================== 2. LOGIN ====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<h1 style="text-align: center; color: #1e3c2c;">🏭 MDMS - CV Amal Mulia</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Manufacturing & Distribution Management System</p>', unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1,2,1])
    with col_l2:
        with st.container():
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("🔐 Login ke Sistem")
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
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
            
            # Demo credentials
            with st.expander("ℹ️ Demo Credentials"):
                st.write("**Pabrik:** pabrik / pabrik123")
                st.write("**Distributor:** distributor1 / dist123")
                st.write("**Klien:** klien1 / klien123")
    st.stop()

# ==================== 3. SIDEBAR & HEADER ====================
with st.sidebar:
    # Coba tampilkan logo jika ada
    try:
        if Path("logo.png").exists():
            st.image("logo.png", width=120)
        else:
            st.markdown('<h3 style="text-align: center; color: white;">🏭 MDMS</h3>', unsafe_allow_html=True)
    except:
        st.markdown('<h3 style="text-align: center; color: white;">🏭 MDMS</h3>', unsafe_allow_html=True)
    
    st.markdown(f"### 👤 {st.session_state.username}")
    st.markdown(f"**Role:** `{st.session_state.role.upper()}`")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Header utama
st.markdown(f'<div style="background: linear-gradient(120deg, #1e3c2c, #2e8b57); padding: 1rem; border-radius: 20px; color: white; margin-bottom: 1.5rem;"><h2>👋 Selamat datang, {st.session_state.username}</h2><p>{datetime.now().strftime("%A, %d %B %Y")}</p></div>', unsafe_allow_html=True)

# ==================== 4. DASHBOARD ====================
role = st.session_state.role
username = st.session_state.username

# Helper untuk menampilkan gambar produk
def tampilkan_gambar_produk(nama_produk):
    """Tampilkan gambar berdasarkan nama produk"""
    try:
        # Coba cari gambar dengan nama produk (case insensitive)
        gambar_path = Path(f"images/{nama_produk.lower().replace(' ', '_')}.png")
        if gambar_path.exists():
            st.image(str(gambar_path), width=100)
        else:
            # Gambar default
            st.image("https://img.icons8.com/fluency/96/date-filled.png", width=80)
    except:
        st.image("https://img.icons8.com/fluency/96/date-filled.png", width=80)

# -------------------- ROLE PABRIK --------------------
if role == "pabrik":
    # Metric cards
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    total_stok = get_df("SELECT SUM(stok) as total FROM produk").iloc[0]['total'] or 0
    total_pesanan_makloon = get_df("SELECT SUM(jumlah) FROM pesanan WHERE jenis_pesanan='makloon' AND status='Proses Produksi'").iloc[0,0] or 0
    total_order_waiting = get_df("SELECT SUM(jumlah) FROM pesanan WHERE jenis_pesanan='order_stok' AND status='Menunggu Konfirmasi'").iloc[0,0] or 0
    produk_terjual = get_df("SELECT COUNT(*) FROM pesanan").iloc[0,0] or 0
    
    with col_m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_stok}</div><div class="metric-label">📦 Total Stok</div></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_pesanan_makloon}</div><div class="metric-label">🏭 Pesanan Makloon</div></div>', unsafe_allow_html=True)
    with col_m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_order_waiting}</div><div class="metric-label">⏳ Order Menunggu</div></div>', unsafe_allow_html=True)
    with col_m4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{produk_terjual}</div><div class="metric-label">📝 Total Transaksi</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    t1, t2, t3, t4, t5 = st.tabs(["📊 Manajemen Stok", "🏭 Pesanan Makloon", "🛒 Order Stok Masuk", "📈 Analisis & Produksi", "➕ Tambah Produk"])
    
    # TAB 1: MANAJEMEN STOK
# TAB 1: MANAJEMEN STOK
    with t1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📋 Inventory Real-time")
        
        df_stok = get_df("SELECT id, nama, stok, stok_minimum, harga_jual FROM produk")
        if not df_stok.empty:
            # Tampilkan peringatan stok rendah
            produk_rendah = df_stok[df_stok['stok'] < df_stok['stok_minimum']]
            if not produk_rendah.empty:
                st.warning(f"⚠️ Stok berikut perlu segera diproduksi: {', '.join(produk_rendah['nama'].tolist())}")
            
            # Jika Anda pakai Streamlit versi lama, hapus 'hide_index=True' jika muncul error
            st.dataframe(df_stok, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("✏️ Update Stok Produk")
            col_up1, col_up2 = st.columns([1,1])
            with col_up1:
                pilih_produk = st.selectbox("Pilih produk", df_stok['nama'].tolist(), key="update_produk")
                # PERBAIKAN: Konversi numpy.int64 ke int standar
                stok_saat_ini = int(df_stok[df_stok['nama']==pilih_produk]['stok'].values[0])
                stok_min = int(df_stok[df_stok['nama']==pilih_produk]['stok_minimum'].values[0])
                st.metric("Stok saat ini", stok_saat_ini)
            with col_up2:
                stok_baru = st.number_input("Stok baru (setelah produksi)", min_value=0, step=1, value=stok_saat_ini)
                if stok_baru > stok_saat_ini:
                    st.success(f"✅ Akan menambah {stok_baru - stok_saat_ini} unit ke stok")
                elif stok_baru < stok_saat_ini:
                    st.warning(f"⚠️ Akan mengurangi {stok_saat_ini - stok_baru} unit dari stok")
                if st.button("💾 Update Stok", type="primary"):
                    run_query("UPDATE produk SET stok = ? WHERE nama = ?", (stok_baru, pilih_produk))
                    st.success("✅ Stok berhasil diupdate!")
                    st.rerun()
        else:
            st.info("Belum ada data produk.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: PESANAN MAKLOON
    with t2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("➕ Input Pesanan Makloon Baru")
        with st.form("add_makloon", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                klien_name = st.text_input("Nama Klien", placeholder="Masukkan nama klien")
                produk_options = get_df("SELECT nama FROM produk")['nama'].tolist()
                produk_name = st.selectbox("Pilih Produk", produk_options)
            with col_b:
                qty = st.number_input("Jumlah", min_value=1, step=1)
                tgl_now = datetime.now().strftime("%d/%m/%Y %H:%M")
            if st.form_submit_button("💾 Simpan Pesanan", use_container_width=True):
                if klien_name:
                    try:
                        run_query("""INSERT INTO pesanan (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                     VALUES (?,?,?,?,?,?,?)""",
                                  (klien_name, produk_name, qty, "Proses Produksi", tgl_now, "makloon", username))
                        st.success(f"✅ Pesanan makloon untuk {klien_name} tercatat!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal: {e}")
                else:
                    st.warning("Nama klien harus diisi!")
        
        st.divider()
        st.subheader("📋 Daftar Pesanan Makloon Aktif")
        df_makloon = get_df("""SELECT id, klien, produk, jumlah, status, tanggal_masuk 
                               FROM pesanan 
                               WHERE jenis_pesanan='makloon' 
                               ORDER BY id DESC""")
        if not df_makloon.empty:
            st.dataframe(df_makloon, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada pesanan makloon.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: ORDER STOK MASUK
    with t3:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("⏳ Order Stok Menunggu Konfirmasi")
        
        df_waiting = get_df("""SELECT * FROM pesanan 
                               WHERE jenis_pesanan='order_stok' 
                               AND status='Menunggu Konfirmasi' 
                               ORDER BY tanggal_masuk ASC""")
        if df_waiting.empty:
            st.info("Tidak ada order stok yang perlu dikonfirmasi")
        else:
            for _, row in df_waiting.iterrows():
                with st.expander(f"📦 Order dari **{row['klien']}** - {row['produk']} x {row['jumlah']}"):
                    stok_tersedia = get_df("SELECT stok FROM produk WHERE nama=?", (row['produk'],)).iloc[0]['stok']
                    st.metric("Stok tersedia", stok_tersedia)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Setujui & Kirim", key=f"approve_{row['id']}"):
                            if row['jumlah'] <= stok_tersedia:
                                run_query("UPDATE produk SET stok = stok - ? WHERE nama=?", (row['jumlah'], row['produk']))
                                run_query("UPDATE pesanan SET status='Disetujui & Siap Kirim', tanggal_konfirmasi=? WHERE id=?", 
                                          (datetime.now().strftime("%d/%m/%Y %H:%M"), row['id']))
                                # Catat ke stok_distributor
                                run_query("INSERT INTO stok_distributor (distributor, produk, jumlah, tanggal_ambil) VALUES (?,?,?,?)",
                                          (row['klien'], row['produk'], row['jumlah'], datetime.now().strftime("%d/%m/%Y %H:%M")))
                                st.success("✅ Order disetujui! Stok berkurang.")
                                st.rerun()
                            else:
                                st.error(f"❌ Stok tidak cukup! Tersedia {stok_tersedia}.")
                    with col2:
                        if st.button(f"❌ Tolak Order", key=f"reject_{row['id']}"):
                            run_query("UPDATE pesanan SET status='Ditolak', tanggal_konfirmasi=? WHERE id=?", 
                                      (datetime.now().strftime("%d/%m/%Y %H:%M"), row['id']))
                            st.warning("Order ditolak.")
                            st.rerun()
        
        st.divider()
        st.subheader("📜 Riwayat Konfirmasi Order")
        df_history = get_df("""SELECT id, klien, produk, jumlah, status, tanggal_konfirmasi 
                               FROM pesanan 
                               WHERE jenis_pesanan='order_stok' 
                               AND status != 'Menunggu Konfirmasi'
                               ORDER BY tanggal_konfirmasi DESC""")
        if not df_history.empty:
            st.dataframe(df_history, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: ANALISIS & PRODUKSI
    with t4:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📊 Dashboard Produksi")
        
        # Chart stok produk
        df_chart = get_df("SELECT nama, stok, stok_minimum FROM produk")
        if not df_chart.empty:
            fig = px.bar(df_chart, x='nama', y='stok', title="Stok per Produk", 
                         color='stok', color_continuous_scale='Viridis',
                         labels={'stok': 'Jumlah Stok', 'nama': 'Produk'})
            fig.add_hline(y=df_chart['stok_minimum'].mean(), line_dash="dash", line_color="red", 
                          annotation_text="Rata-rata Stok Minimum")
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Rekomendasi produksi
        st.subheader("🏭 Rekomendasi Produksi")
        df_kebutuhan = get_df("""
            SELECT produk, SUM(jumlah) as total_dibutuhkan 
            FROM pesanan 
            WHERE jenis_pesanan='makloon' AND status='Proses Produksi'
            GROUP BY produk
        """)
        
        if not df_kebutuhan.empty:
            st.write("**Total pesanan makloon yang perlu diproduksi:**")
            st.dataframe(df_kebutuhan, use_container_width=True, hide_index=True)
            
            for _, row in df_kebutuhan.iterrows():
                produk = row['produk']
                kebutuhan = row['total_dibutuhkan']
                stok_sekarang = get_df("SELECT stok FROM produk WHERE nama=?", (produk,)).iloc[0]['stok']
                stok_min = get_df("SELECT stok_minimum FROM produk WHERE nama=?", (produk,)).iloc[0]['stok_minimum']
                
                if stok_sekarang < stok_min:
                    perlu_produksi = (stok_min - stok_sekarang) + kebutuhan
                    st.warning(f"""
                    **{produk}**  
                    - Stok saat ini: {stok_sekarang}  
                    - Stok minimum: {stok_min}  
                    - Pesanan makloon: {kebutuhan}  
                    - 🔥 **Rekomendasi produksi: {perlu_produksi} unit**
                    """)
                else:
                    st.info(f"""
                    **{produk}**  
                    - Stok saat ini: {stok_sekarang}  
                    - Stok minimum: {stok_min}  
                    - Pesanan makloon: {kebutuhan}  
                    - ✅ Stok mencukupi
                    """)
        else:
            st.info("Tidak ada pesanan makloon yang perlu diproduksi saat ini.")
        
        st.divider()
        
        # Stok yang sudah dikirim ke distributor
        st.subheader("📦 Stok yang Sudah Dikirim ke Distributor")
        df_dist_stok = get_df("""
            SELECT distributor, produk, SUM(jumlah) as total, tanggal_ambil 
            FROM stok_distributor 
            GROUP BY distributor, produk
            ORDER BY tanggal_ambil DESC
        """)
        if not df_dist_stok.empty:
            st.dataframe(df_dist_stok, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada stok yang dikirim ke distributor.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 5: TAMBAH PRODUK
    with t5:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("➕ Registrasi Produk Baru")
        
        # Tampilkan gambar produk jika ada
        col_img1, col_img2 = st.columns([1,3])
        with col_img1:
            tampilkan_gambar_produk("Sari Kurma")
        with col_img2:
            st.caption("Contoh gambar produk Sari Kurma")
        
        with st.form("new_product"):
            np = st.text_input("Nama Produk", placeholder="ex: Sari Kurma Ekstra")
            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                sp = st.number_input("Stok Awal", min_value=0, step=1)
            with col_h2:
                sm = st.number_input("Stok Minimum", min_value=0, step=1, value=50)
            with col_h3:
                hp = st.number_input("Harga Jual (Rp)", min_value=0, step=1000)
            if st.form_submit_button("Tambah Produk", use_container_width=True):
                if np:
                    try:
                        run_query("INSERT INTO produk (nama, stok, stok_minimum, harga_jual) VALUES (?,?,?,?)", 
                                  (np, sp, sm, hp))
                        st.success(f"✅ Produk '{np}' berhasil ditambahkan!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Nama produk sudah ada.")
                else:
                    st.warning("Nama produk harus diisi.")
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- ROLE DISTRIBUTOR --------------------
elif role == "distributor":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🏪 Portal Distributor")
    
    # Tampilkan gambar produk
    col_img1, col_img2 = st.columns([1,3])
    with col_img1:
        try:
            if Path("images/sari_kurma.png").exists():
                st.image("images/sari_kurma.png", width=100)
            else:
                st.image("https://img.icons8.com/fluency/96/date-filled.png", width=80)
        except:
            pass
    
    tab1, tab2, tab3 = st.tabs(["📦 Lihat Stok Pabrik", "🛒 Order Stok", "📋 Riwayat Order Saya"])
    
    with tab1:
        df_stok = get_df("SELECT nama, stok, harga_jual FROM produk")
        if not df_stok.empty:
            st.dataframe(df_stok.style.format({'harga_jual': 'Rp {:,.0f}'}), use_container_width=True, hide_index=True)
    
    with tab2:
        produk_list = get_df("SELECT nama, stok FROM produk")
        if not produk_list.empty:
            with st.form("order_stok_form"):
                pilih = st.selectbox("Pilih Produk", produk_list['nama'].tolist())
                stok_tersedia = produk_list[produk_list['nama']==pilih]['stok'].values[0]
                st.metric("Stok tersedia", stok_tersedia)
                jumlah = st.number_input("Jumlah Order", min_value=1, max_value=1000, step=1)
                if st.form_submit_button("Kirim Order", use_container_width=True):
                    if jumlah <= stok_tersedia:
                        tgl = datetime.now().strftime("%d/%m/%Y %H:%M")
                        run_query("""INSERT INTO pesanan (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                     VALUES (?,?,?,?,?,?,?)""",
                                  (username, pilih, jumlah, "Menunggu Konfirmasi", tgl, "order_stok", username))
                        st.success("✅ Order berhasil dikirim! Menunggu konfirmasi pabrik.")
                        st.rerun()
                    else:
                        st.error(f"❌ Stok tidak cukup. Tersedia {stok_tersedia}.")
        else:
            st.warning("Belum ada produk.")
    
    with tab3:
        df_riwayat = get_df("""SELECT id, produk, jumlah, status, tanggal_masuk, tanggal_konfirmasi
                               FROM pesanan WHERE created_by=? ORDER BY tanggal_masuk DESC""", (username,))
        if df_riwayat.empty:
            st.info("Belum ada pesanan.")
        else:
            st.dataframe(df_riwayat, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- ROLE KLIEN --------------------
elif role == "klien":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🤝 Monitoring & Order untuk Klien")
    
    # Tampilkan gambar produk
    try:
        if Path("images/sari_kurma.png").exists():
            st.image("images/sari_kurma.png", width=120)
    except:
        pass
    
    tab1, tab2, tab3 = st.tabs(["📋 Status Pesanan Makloon", "🛒 Order Stok", "📜 Riwayat Lengkap"])
    
    with tab1:
        df_mak = get_df("""SELECT produk, jumlah, status, tanggal_masuk FROM pesanan 
                           WHERE klien=? AND jenis_pesanan='makloon' 
                           ORDER BY tanggal_masuk DESC""", (username,))
        if df_mak.empty:
            st.info("Tidak ada pesanan makloon.")
        else:
            st.dataframe(df_mak, use_container_width=True, hide_index=True)
    
    with tab2:
        produk_list = get_df("SELECT nama, stok, harga_jual FROM produk")
        if not produk_list.empty:
            with st.form("order_stok_klien"):
                pilih = st.selectbox("Produk", produk_list['nama'].tolist())
                stok_tersedia = produk_list[produk_list['nama']==pilih]['stok'].values[0]
                harga = produk_list[produk_list['nama']==pilih]['harga_jual'].values[0]
                st.metric("Stok tersedia", stok_tersedia)
                st.caption(f"Harga: Rp {harga:,.0f}")
                jumlah = st.number_input("Jumlah", 1, 1000)
                if st.form_submit_button("Order Sekarang", use_container_width=True):
                    if jumlah <= stok_tersedia:
                        tgl = datetime.now().strftime("%d/%m/%Y %H:%M")
                        run_query("""INSERT INTO pesanan (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                     VALUES (?,?,?,?,?,?,?)""",
                                  (username, pilih, jumlah, "Menunggu Konfirmasi", tgl, "order_stok", username))
                        st.success("✅ Order stok terkirim!")
                        st.rerun()
                    else:
                        st.error(f"❌ Stok tidak cukup.")
        else:
            st.warning("Belum ada produk.")
    
    with tab3:
        df_all = get_df("""SELECT id, produk, jumlah, status, tanggal_masuk, jenis_pesanan 
                           FROM pesanan 
                           WHERE created_by=? OR (klien=? AND jenis_pesanan='makloon')
                           ORDER BY tanggal_masuk DESC""", (username, username))
        if df_all.empty:
            st.info("Tidak ada riwayat.")
        else:
            st.dataframe(df_all, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<hr><p style="text-align: center; color: #888;">© 2025 CV Amal Mulia - Sistem Manajemen Produksi & Distribusi</p>', unsafe_allow_html=True)
