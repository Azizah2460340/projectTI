import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==================== 1. KONFIGURASI HALAMAN ====================
st.set_page_config(page_title="MDMS - CV Amal Mulia", layout="wide", page_icon="🏭")

# ==================== 2. FUNGSI DATABASE ====================
def get_connection():
    """Membuat koneksi ke database SQLite."""
    return sqlite3.connect('makloon.db', check_same_thread=False)

def init_db():
    """Membuat tabel dan data default jika belum ada."""
    with get_connection() as conn:
        c = conn.cursor()
        
        # Tabel Produk
        c.execute('''CREATE TABLE IF NOT EXISTS produk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT UNIQUE,
                    stok INTEGER,
                    harga_jual INTEGER)''')
        
        # Tabel Pesanan (diperluas untuk makloon & order stock)
        c.execute('''CREATE TABLE IF NOT EXISTS pesanan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    klien TEXT,                -- nama klien atau distributor yang order
                    produk TEXT,
                    jumlah INTEGER,
                    status TEXT,               -- Menunggu Konfirmasi, Disetujui, Ditolak, Proses Produksi, Selesai
                    tanggal_masuk TEXT,
                    jenis_pesanan TEXT,        -- 'makloon' atau 'order_stock'
                    created_by TEXT,           -- username yang membuat order
                    tanggal_konfirmasi TEXT
                    )''')
        
        # Tabel Users
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    role TEXT)''')
        
        # Data default users
        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()[0] == 0:
            users_data = [
                ('pabrik', 'pabrik123', 'pabrik'),
                ('distributor', 'dist123', 'distributor'),
                ('klien', 'klien123', 'klien')
            ]
            c.executemany("INSERT INTO users VALUES (?,?,?)", users_data)
        
        # Data default produk
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

# Inisialisasi database
init_db()

# ==================== 3. SISTEM LOGIN ====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login MDMS - CV Amal Mulia")
    col_l1, col_l2, col_l3 = st.columns([1,2,1])
    with col_l2:
        with st.form("login_form"):
            u = st.text_input("Username").strip()
            p = st.text_input("Password", type="password").strip()
            if st.form_submit_button("Masuk"):
                res = get_df("SELECT role FROM users WHERE username=? AND password=?", (u, p))
                if not res.empty:
                    st.session_state.authenticated = True
                    st.session_state.username = u
                    st.session_state.role = res.iloc[0]['role']
                    st.rerun()
                else:
                    st.error("Username atau password salah!")
    st.stop()

# ==================== 4. SIDEBAR ====================
st.sidebar.title(f"👤 {st.session_state.username}")
st.sidebar.info(f"Role: {st.session_state.role.upper()}")
if st.sidebar.button("🚪 Keluar"):
    st.session_state.authenticated = False
    st.rerun()

# ==================== 5. DASHBOARD BERDASARKAN ROLE ====================
role = st.session_state.role
username = st.session_state.username

# -------------------- ROLE PABRIK --------------------
if role == "pabrik":
    st.title("🏭 Dashboard Admin Pabrik")
    t1, t2, t3, t4 = st.tabs(["📊 Stok Barang", "📦 Pesanan Makloon", "🛒 Order Stok Masuk", "➕ Tambah Produk"])
    
    # TAB 1: STOK BARANG
    with t1:
        st.subheader("Inventory Real-time")
        df_stok = get_df("SELECT id, nama, stok, harga_jual FROM produk")
        if not df_stok.empty:
            st.dataframe(df_stok, use_container_width=True, hide_index=True)
            
            # Fitur edit stok langsung (opsional)
            with st.expander("✏️ Edit Stok Produk"):
                pilih_produk = st.selectbox("Pilih produk", df_stok['nama'].tolist())
                stok_baru = st.number_input("Stok baru", min_value=0, step=1)
                if st.button("Update Stok"):
                    run_query("UPDATE produk SET stok = ? WHERE nama = ?", (stok_baru, pilih_produk))
                    st.success("Stok berhasil diupdate!")
                    st.rerun()
        else:
            st.info("Belum ada data produk.")
    
    # TAB 2: PESANAN MAKLOON (input dan daftar)
    with t2:
        st.subheader("Input Pesanan Makloon Baru (dari klien)")
        with st.form("add_makloon", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                klien_name = st.text_input("Nama Klien")
                produk_name = st.text_input("Nama Produk")
            with col_b:
                qty = st.number_input("Jumlah", min_value=1, step=1)
                tgl_now = datetime.now().strftime("%d/%m/%Y %H:%M")
            if st.form_submit_button("Simpan Pesanan Makloon"):
                if klien_name and produk_name:
                    try:
                        run_query("""INSERT INTO pesanan 
                                     (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                     VALUES (?,?,?,?,?,?,?)""",
                                  (klien_name, produk_name, qty, "Proses Produksi", tgl_now, "makloon", st.session_state.username))
                        st.success(f"Pesanan makloon untuk {klien_name} tercatat!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal simpan: {e}")
                else:
                    st.warning("Lengkapi nama klien dan produk!")
        
        st.divider()
        st.subheader("Daftar Semua Pesanan (Makloon & Order Stock)")
        df_semua_pesanan = get_df("SELECT id, klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by, tanggal_konfirmasi FROM pesanan ORDER BY id DESC")
        st.dataframe(df_semua_pesanan, use_container_width=True, hide_index=True)
    
    # TAB 3: ORDER STOK MASUK (perlu konfirmasi)
    with t3:
        st.subheader("Order Stok Menunggu Konfirmasi")
        df_order_masuk = get_df("""SELECT * FROM pesanan 
                                   WHERE jenis_pesanan='order_stock' 
                                   AND status='Menunggu Konfirmasi'
                                   ORDER BY tanggal_masuk ASC""")
        if df_order_masuk.empty:
            st.info("Tidak ada order stok yang menunggu konfirmasi.")
        else:
            for idx, row in df_order_masuk.iterrows():
                with st.expander(f"📦 Order dari {row['klien']} - {row['produk']} x {row['jumlah']} (Tgl: {row['tanggal_masuk']})"):
                    st.write(f"**ID Order:** {row['id']}")
                    st.write(f"**Jumlah dipesan:** {row['jumlah']}")
                    # Cek stok tersedia
                    stok_tersedia = get_df("SELECT stok FROM produk WHERE nama=?", (row['produk'],)).iloc[0]['stok']
                    st.write(f"**Stok saat ini:** {stok_tersedia}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Setujui & Kurangi Stok", key=f"approve_{row['id']}"):
                            if row['jumlah'] <= stok_tersedia:
                                # Kurangi stok
                                run_query("UPDATE produk SET stok = stok - ? WHERE nama=?", (row['jumlah'], row['produk']))
                                # Update status pesanan
                                run_query("""UPDATE pesanan 
                                             SET status='Disetujui & Siap Kirim', 
                                                 tanggal_konfirmasi=? 
                                             WHERE id=?""", 
                                          (datetime.now().strftime("%d/%m/%Y %H:%M"), row['id']))
                                st.success(f"Order {row['id']} disetujui. Stok berkurang.")
                                st.rerun()
                            else:
                                st.error(f"Stok tidak cukup! Tersedia hanya {stok_tersedia}.")
                    with col2:
                        if st.button(f"❌ Tolak Order", key=f"reject_{row['id']}"):
                            run_query("UPDATE pesanan SET status='Ditolak', tanggal_konfirmasi=? WHERE id=?", 
                                      (datetime.now().strftime("%d/%m/%Y %H:%M"), row['id']))
                            st.warning(f"Order {row['id']} ditolak.")
                            st.rerun()
        
        st.divider()
        st.subheader("Riwayat Konfirmasi Order Stok")
        df_riwayat_order = get_df("""SELECT id, klien, produk, jumlah, status, tanggal_masuk, tanggal_konfirmasi 
                                     FROM pesanan 
                                     WHERE jenis_pesanan='order_stock' 
                                     AND status != 'Menunggu Konfirmasi'
                                     ORDER BY tanggal_konfirmasi DESC""")
        if not df_riwayat_order.empty:
            st.dataframe(df_riwayat_order, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada order yang dikonfirmasi atau ditolak.")
    
    # TAB 4: TAMBAH PRODUK
    with t4:
        st.subheader("Registrasi Produk Baru")
        with st.form("new_product", clear_on_submit=True):
            np = st.text_input("Nama Produk Baru").strip()
            sp = st.number_input("Stok Awal", min_value=0, step=1)
            hp = st.number_input("Harga Jual", min_value=0, step=1000)
            if st.form_submit_button("Tambah ke Database"):
                if np:
                    try:
                        run_query("INSERT INTO produk (nama, stok, harga_jual) VALUES (?,?,?)", (np, sp, hp))
                        st.success(f"Produk '{np}' berhasil didaftarkan!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Gagal! Nama produk sudah ada.")
                    except Exception as e:
                        st.error(f"Kesalahan: {e}")
                else:
                    st.warning("Nama produk tidak boleh kosong!")

# -------------------- ROLE DISTRIBUTOR --------------------
elif role == "distributor":
    st.title("🏪 Portal Distributor")
    tab1, tab2, tab3 = st.tabs(["📦 Lihat Stok", "🛒 Order Stok", "📋 Riwayat Order Saya"])
    
    # TAB 1: Lihat Stok
    with tab1:
        st.subheader("Stok Produk Tersedia")
        df_stok_dist = get_df("SELECT nama, stok, harga_jual FROM produk")
        if not df_stok_dist.empty:
            st.dataframe(df_stok_dist, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada data produk.")
    
    # TAB 2: Order Stok
    with tab2:
        st.subheader("Buat Order Stok Baru")
        produk_list = get_df("SELECT nama, stok FROM produk")
        if produk_list.empty:
            st.warning("Belum ada produk yang tersedia.")
        else:
            with st.form("form_order_stock", clear_on_submit=True):
                pilih_produk = st.selectbox("Pilih Produk", produk_list['nama'].tolist())
                # Ambil stok produk terpilih
                stok_tersedia = produk_list[produk_list['nama'] == pilih_produk]['stok'].values[0]
                st.caption(f"Stok tersedia: {stok_tersedia}")
                jumlah_order = st.number_input("Jumlah", min_value=1, max_value=1000, step=1)
                
                if st.form_submit_button("Kirim Order"):
                    if jumlah_order <= stok_tersedia:
                        # Simpan ke tabel pesanan dengan status 'Menunggu Konfirmasi'
                        tgl_order = datetime.now().strftime("%d/%m/%Y %H:%M")
                        try:
                            run_query("""INSERT INTO pesanan 
                                         (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                         VALUES (?,?,?,?,?,?,?)""",
                                      (username, pilih_produk, jumlah_order, "Menunggu Konfirmasi", 
                                       tgl_order, "order_stock", username))
                            st.success("Order stok berhasil dikirim! Menunggu konfirmasi pabrik.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal mengirim order: {e}")
                    else:
                        st.error(f"Stok tidak mencukupi! Maksimal order {stok_tersedia}.")
    
    # TAB 3: Riwayat Order Saya
    with tab3:
        st.subheader("Riwayat Pesanan Saya (Order Stok & Makloon)")
        df_riwayat_saya = get_df("""SELECT id, produk, jumlah, status, tanggal_masuk, jenis_pesanan, tanggal_konfirmasi
                                    FROM pesanan 
                                    WHERE created_by = ? 
                                    ORDER BY tanggal_masuk DESC""", (username,))
        if df_riwayat_saya.empty:
            st.info("Anda belum pernah membuat pesanan.")
        else:
            st.dataframe(df_riwayat_saya, use_container_width=True, hide_index=True)

# -------------------- ROLE KLIEN --------------------
elif role == "klien":
    st.title("🤝 Monitoring & Order Stock untuk Klien")
    tab1, tab2, tab3 = st.tabs(["📋 Status Pesanan Makloon", "🛒 Order Stok (Sisa Stok)", "📜 Riwayat Order Saya"])
    
    # TAB 1: Pesanan makloon yang dicatat oleh pabrik (berdasarkan nama klien = username)
    with tab1:
        st.subheader("Status Pesanan Makloon")
        df_makloon = get_df("""SELECT produk, jumlah, status, tanggal_masuk, tanggal_konfirmasi 
                               FROM pesanan 
                               WHERE klien = ? AND jenis_pesanan = 'makloon'
                               ORDER BY tanggal_masuk DESC""", (username,))
        if df_makloon.empty:
            st.info(f"Halo {username}, belum ada pesanan makloon atas nama Anda.")
        else:
            st.dataframe(df_makloon, use_container_width=True, hide_index=True)
    
    # TAB 2: Klien juga bisa order stok (seperti distributor)
    with tab2:
        st.subheader("Beli Stok Langsung (Order Stock)")
        produk_list = get_df("SELECT nama, stok, harga_jual FROM produk")
        if produk_list.empty:
            st.warning("Belum ada produk yang dijual.")
        else:
            with st.form("form_order_stok_klien", clear_on_submit=True):
                pilih_produk = st.selectbox("Pilih Produk", produk_list['nama'].tolist())
                stok_tersedia = produk_list[produk_list['nama'] == pilih_produk]['stok'].values[0]
                st.caption(f"Stok tersedia: {stok_tersedia}")
                jumlah_order = st.number_input("Jumlah order", min_value=1, max_value=1000, step=1)
                
                if st.form_submit_button("Order Stok"):
                    if jumlah_order <= stok_tersedia:
                        tgl_order = datetime.now().strftime("%d/%m/%Y %H:%M")
                        run_query("""INSERT INTO pesanan 
                                     (klien, produk, jumlah, status, tanggal_masuk, jenis_pesanan, created_by)
                                     VALUES (?,?,?,?,?,?,?)""",
                                  (username, pilih_produk, jumlah_order, "Menunggu Konfirmasi", 
                                   tgl_order, "order_stock", username))
                        st.success("Order stok berhasil dikirim. Pabrik akan mengonfirmasi.")
                        st.rerun()
                    else:
                        st.error(f"Stok tidak cukup. Tersedia {stok_tersedia}.")
    
    # TAB 3: Riwayat semua pesanan klien (baik makloon maupun order stock)
    with tab3:
        st.subheader("Riwayat Semua Pesanan")
        df_riwayat = get_df("""SELECT id, produk, jumlah, status, tanggal_masuk, jenis_pesanan, tanggal_konfirmasi
                               FROM pesanan 
                               WHERE created_by = ? OR (klien = ? AND jenis_pesanan='makloon')
                               ORDER BY tanggal_masuk DESC""", (username, username))
        if df_riwayat.empty:
            st.info("Tidak ada riwayat pesanan.")
        else:
            st.dataframe(df_riwayat, use_container_width=True, hide_index=True)

# ==================== END ====================
