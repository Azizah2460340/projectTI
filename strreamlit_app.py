import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import base64
from PIL import Image

# ==================== 0. KONFIGURASI HALAMAN ====================
logo_cv = Image.open("LogoCV.jpeg")
st.set_page_config(page_title = "MDMS - CV Amal Mulia", layout="wide", page_icon="LogoCV")

# -------------------- FUNGSI UNTUK BACKGROUND GIF (BERGERAK) --------------------
import streamlit as st
import base64

def set_background_mp4(mp4_url_or_path):
    """
    Set background menggunakan MP4 (URL atau file lokal).
    Ditambah overlay putih transparan agar teks tetap kontras.
    """
    is_url = mp4_url_or_path.startswith(('http://', 'https://'))
    
    if is_url:
        video_source = mp4_url_or_path
    else:
        try:
            with open(mp4_url_or_path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode()
            video_source = f"data:video/mp4;base64,{b64}"
        except:
            return

    video_html = f"""
        <style>
        /* Mengatur video agar memenuhi layar dan berada di belakang */
        #myVideo {{
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%; 
            min-height: 100%;
            z-index: -1;
            object-fit: cover;
        }}

        /* Overlay putih agar konten aplikasi mudah dibaca */
        .stApp {{
            background: rgba(255, 255, 255, 0.7); /* Atur kegelapan di sini (0.7 = 70%) */
        }}
        </style>
        
        <video autoplay muted loop id="myVideo">
          <source src="{video_source}" type="video/mp4">
          Your browser does not support HTML5 video.
        </video>
    """
    st.markdown(video_html, unsafe_allow_html=True)

# -------------------- KONFIGURASI URL VIDEO --------------------
# Pastikan nama variabel SAMA saat dibuat dan saat dipanggil
BACKGROUND_MP4_URL = "https://www.youtube.com/watch?v=SLbSsv_2u4A" 

# Jika pakai link OneDrive, pastikan itu adalah link "Direct Download"
# Link biasa dari OneDrive seringkali terblokir (Forbidden) oleh browser
set_background_mp4(BACKGROUND_MP4_URL)

# ==================== 1. CSS TAMBAHAN UNTUK CARD PUTIH ====================
st.markdown("""
<style>
    /* Semua konten utama dibungkus card putih transparan */
    .main-card {
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 25px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        backdrop-filter: blur(2px);
    }
    /* Sidebar juga dibuat sedikit transparan agar background terlihat */
    .css-1d391kg, .css-12oz5g0 {
        background-color: rgba(30, 60, 44, 0.9) !important;
        backdrop-filter: blur(5px);
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
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255,255,255,0.9);
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
    /* Dataframe */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        background: white;
    }
    /* Header utama */
    .main-header {
        background: linear-gradient(120deg, #1e3c2c, #2e8b57);
        padding: 1rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 2. FUNGSI DATABASE ====================
def get_connection():
    return sqlite3.connect('makloon_v2.db', check_same_thread=False)

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
        c.execute('''CREATE TABLE IF NOT EXISTS stok_distributor (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    distributor TEXT,
                    produk TEXT,
                    jumlah INTEGER,
                    tanggal_ambil TEXT)''')
        
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

# ==================== 3. SISTEM LOGIN ====================

# ==================== 3. SISTEM LOGIN & REGISTRASI ====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏭 MDMS - CV Amal Mulia")
    
    # Tambahkan opsi pilih menu di login page
    menu_login = st.radio("Pilih Menu", ["Masuk", "Daftar Akun"], horizontal=True)
    
    col_l1, col_l2, col_l3 = st.columns([1,2,1])
    
    with col_l2:
        if menu_login == "Masuk":
            with st.form("login_form"):
                st.subheader("🔑 Login")
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
                        st.error("❌ Username atau password salah!")
        
        else:
            with st.form("register_form"):
                st.subheader("📝 Daftar Akun Baru")
                new_u = st.text_input("Buat Username")
                new_p = st.text_input("Buat Password", type="password")
                # Anda bisa membatasi role apa saja yang boleh daftar mandiri
                new_role = st.selectbox("Daftar sebagai", ["distributor", "klien"])
                
                st.info("Pendaftaran role 'pabrik' hanya bisa dilakukan oleh Admin.")
                
                if st.form_submit_button("Daftar Sekarang", use_container_width=True):
                    if new_u and new_p:
                        # Cek apakah username sudah ada
                        cek_user = get_df("SELECT * FROM users WHERE username=?", (new_u,))
                        if cek_user.empty:
                            try:
                                run_query("INSERT INTO users (username, password, role) VALUES (?,?,?)", 
                                         (new_u, new_p, new_role))
                                st.success("✅ Akun berhasil dibuat! Silakan pilih menu 'Masuk'.")
                            except Exception as e:
                                st.error(f"Gagal mendaftar: {e}")
                        else:
                            st.warning("⚠️ Username sudah digunakan, pilih nama lain.")
                    else:
                        st.error("❌ Semua kolom harus diisi!")

    st.stop()
# ==================== 4. SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🏭 MDMS")
    st.markdown(f"**👤 {st.session_state.username}**")
    st.markdown(f"**Role:** `{st.session_state.role.upper()}`")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Header utama (juga dibungkus card putih transparan)
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown(f"## 👋 Selamat datang, {st.session_state.username}")
st.markdown(f"{datetime.now().strftime('%A, %d %B %Y')}")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== 5. DASHBOARD ====================
role = st.session_state.role
username = st.session_state.username

if role == "pabrik":
    # Metric dalam card putih
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    total_stok = get_df("SELECT SUM(stok) as total FROM produk").iloc[0]['total'] or 0
    total_pesanan_makloon = get_df("SELECT SUM(jumlah) FROM pesanan WHERE jenis_pesanan='makloon' AND status='Proses Produksi'").iloc[0,0] or 0
    total_order_waiting = get_df("SELECT SUM(jumlah) FROM pesanan WHERE jenis_pesanan='order_stok' AND status='Menunggu Konfirmasi'").iloc[0,0] or 0
    with col_m1:
        st.metric("📦 Total Stok", total_stok)
    with col_m2:
        st.metric("🏭 Pesanan Makloon", total_pesanan_makloon)
    with col_m3:
        st.metric("⏳ Order Menunggu", total_order_waiting)
    with col_m4:
        st.metric("📊 Total Produk", get_df("SELECT COUNT(*) FROM produk").iloc[0,0])
    st.markdown('</div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["📊 Manajemen Stok", "🏭 Pesanan Makloon", "🛒 Order Stok Masuk", "📈 Analisis & Produksi"])
    
    with t1:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📋 Inventory Real-time")
        df_stok = get_df("SELECT id, nama, stok, stok_minimum, harga_jual FROM produk")
        if not df_stok.empty:
            # Warning jika stok di bawah minimum
            produk_rendah = df_stok[df_stok['stok'] < df_stok['stok_minimum']]
            if not produk_rendah.empty:
                st.warning(f"⚠️ Stok perlu segera diproduksi: {', '.join(produk_rendah['nama'].tolist())}")
            st.dataframe(df_stok, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("✏️ Update Stok Produk")
            col_up1, col_up2 = st.columns([1,1])
            with col_up1:
                pilih_produk = st.selectbox("Pilih produk", df_stok['nama'].tolist())
                stok_saat_ini = int(df_stok[df_stok['nama'] == pilih_produk]['stok'].values[0])
                st.metric("Stok saat ini", stok_saat_ini)
            with col_up2:
                stok_baru = st.number_input("Stok baru (setelah produksi)", min_value=0, step=1, value=stok_saat_ini)
                if st.button("💾 Update Stok", type="primary"):
                    run_query("UPDATE produk SET stok = ? WHERE nama = ?", (stok_baru, pilih_produk))
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
    
    with t4:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("📊 Dashboard Produksi")
        df_chart = get_df("SELECT nama, stok FROM produk")
        if not df_chart.empty:
            fig = px.bar(df_chart, x='nama', y='stok', title="Stok per Produk", color='stok', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
        st.divider()
        st.subheader("🏭 Rekomendasi Produksi")
        df_kebutuhan = get_df("""
            SELECT produk, SUM(jumlah) as total_dibutuhkan 
            FROM pesanan 
            WHERE jenis_pesanan='makloon' AND status='Proses Produksi'
            GROUP BY produk
        """)
        if not df_kebutuhan.empty:
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
                    st.info(f"{produk}: Stok aman.")
        else:
            st.info("Tidak ada pesanan makloon yang perlu diproduksi saat ini.")
        st.markdown('</div>', unsafe_allow_html=True)

elif role == "distributor":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🏪 Portal Distributor")
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

elif role == "klien":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🤝 Monitoring & Order Klien")
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
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: rgba(255,255,255,0.7); border-radius: 20px;">
    © 2025 CV Amal Mulia - Manufacturing & Distribution System
</div>
""", unsafe_allow_html=True
           )
