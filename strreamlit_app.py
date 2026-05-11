import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="OrderStock - CV Amal Mulia",
    layout="wide",
    page_icon="🌴"
)

# ==================== CSS ====================
st.markdown("""
<style>

:root{
    --green-dark:#0f3d2e;
    --green-main:#1f7a59;
    --green-soft:#2f9e75;
    --green-bg:#eef8f1;
}

.stApp{
    background: linear-gradient(135deg,#eef8f1,#f7fcf8);
}

/* SIDEBAR */
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#0f3d2e,#1b5e45);
}

section[data-testid="stSidebar"] *{
    color:white !important;
}
/* Custom card untuk form */
    .custom-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;

}
/* CARD */
.white-card{
    background:white;
    border-radius:22px;
    padding:1.5rem;
    margin-bottom:1rem;
    box-shadow:0 4px 10px rgba(0,0,0,0.05);
    border-left:6px solid var(--green-main);
}

/* BUTTON */
.stButton button{
    background: linear-gradient(135deg,#1f7a59,#2f9e75);
    color:white;
    border:none;
    border-radius:25px;
    font-weight:bold;
}

/* TABS */
.stTabs [data-baseweb="tab"]{
    background:#e7f5ec;
    border-radius:20px;
    padding:10px 20px;
}

.stTabs [aria-selected="true"]{
    background:#1f7a59;
    color:white;
}

/* METRIC */
.metric-box{
    background:white;
    border-radius:20px;
    padding:1rem;
    text-align:center;
    box-shadow:0 3px 8px rgba(0,0,0,0.05);
}

.metric-value{
    font-size:2rem;
    font-weight:bold;
    color:#0f3d2e;
}

.footer{
    text-align:center;
    margin-top:2rem;
    color:#456;
}

</style>
""", unsafe_allow_html=True)

# ==================== DATABASE ====================
def get_connection():
    return sqlite3.connect(
        "makloon.db",
        check_same_thread=False
    )

def init_db():

    with get_connection() as conn:

        c = conn.cursor()

        # ===== PRODUK =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS produk(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT UNIQUE,
            stok INTEGER,
            stok_minimum INTEGER,
            harga_jual INTEGER
        )
        """)

        # ===== PESANAN =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS pesanan(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            klien TEXT,
            produk TEXT,
            jumlah INTEGER,
            status TEXT,
            tanggal_masuk TEXT,
            jenis_pesanan TEXT,
            created_by TEXT
        )
        """)

        # ===== STOK DISTRIBUTOR =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS stok_distributor(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            distributor TEXT,
            produk TEXT,
            stok INTEGER
        )
        """)

        # ===== USERS =====
        c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
        """)

        # ===== DEFAULT USER =====
        c.execute("SELECT COUNT(*) FROM users")

        if c.fetchone()[0] == 0:

            users = [
                ("pabrik","pabrik123","pabrik"),
                ("distributor1","dist123","distributor"),
                ("distributor2","dist123","distributor"),
                ("distributor3","dist123","distributor"),
                ("klien1","klien123","klien")
            ]

            c.executemany(
                "INSERT INTO users VALUES (?,?,?)",
                users
            )

        # ===== DEFAULT PRODUK =====
        c.execute("SELECT COUNT(*) FROM produk")

        if c.fetchone()[0] == 0:

            produk = [
                ("Sari Kurma Premium",500,50,35000),
                ("Sari Kurma Herbal Obat Batuk",300,50,40000),
                ("Sari Kurma Lambung",250,50,45000),
                ("Sari Kurma Al-Jazira",600,50,30000)
            ]

            c.executemany("""
            INSERT INTO produk
            (nama,stok,stok_minimum,harga_jual)
            VALUES (?,?,?,?)
            """, produk)

        # ===== AUTO BUAT STOK DISTRIBUTOR =====
        distributors = pd.read_sql_query("""
        SELECT username
        FROM users
        WHERE role='distributor'
        """, conn)

        products = pd.read_sql_query("""
        SELECT nama
        FROM produk
        """, conn)

        for _, d in distributors.iterrows():

            for _, p in products.iterrows():

                cek = pd.read_sql_query("""
                SELECT *
                FROM stok_distributor
                WHERE distributor=? AND produk=?
                """, conn, params=(d["username"], p["nama"]))

                if cek.empty:

                    c.execute("""
                    INSERT INTO stok_distributor
                    (distributor,produk,stok)
                    VALUES (?,?,?)
                    """, (
                        d["username"],
                        p["nama"],
                        0
                    ))

        conn.commit()

def run_query(query, params=()):

    with get_connection() as conn:

        c = conn.cursor()
        c.execute(query, params)
        conn.commit()

def get_df(query, params=()):

    with get_connection() as conn:

        return pd.read_sql_query(
            query,
            conn,
            params=params
        )

init_db()

# ==================== LOGIN ====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ==================== BELUM LOGIN ====================
if not st.session_state.authenticated:

    st.markdown("""
    <div class="white-card">
        <h1>🌴 OrderStock - CV Amal Mulia</h1>
        <p>Manajemen Pesanan & Distribusi Stok</p>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "",
        ["Masuk","Daftar"],
        horizontal=True
    )

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        # ===== LOGIN =====
        if menu == "Masuk":

            with st.form("login"):

                st.subheader("🔐 Login")

                u = st.text_input("Username")

                p = st.text_input(
                    "Password",
                    type="password"
                )

                submit = st.form_submit_button("Masuk")

                if submit:

                    res = get_df(
                        "SELECT role FROM users WHERE username=? AND password=?",
                        (u,p)
                    )

                    if not res.empty:

                        st.session_state.authenticated = True
                        st.session_state.username = u
                        st.session_state.role = res.iloc[0]["role"]

                        st.rerun()

                    else:
                        st.error("Username/password salah")

        # ===== REGISTER =====
        else:

            with st.form("register"):

                st.subheader("📝 Daftar")

                new_u = st.text_input("Username")

                new_p = st.text_input(
                    "Password",
                    type="password"
                )

                role = st.selectbox(
                    "Daftar sebagai",
                    ["distributor","klien"]
                )

                submit = st.form_submit_button("Daftar")

                if submit:

                    cek = get_df(
                        "SELECT * FROM users WHERE username=?",
                        (new_u,)
                    )

                    if cek.empty:

                        run_query(
                            "INSERT INTO users VALUES (?,?,?)",
                            (new_u,new_p,role)
                        )

                        if role == "distributor":

                            produk_list = get_df("""
                            SELECT nama
                            FROM produk
                            """)

                            for _, row in produk_list.iterrows():

                                run_query("""
                                INSERT INTO stok_distributor
                                (distributor,produk,stok)
                                VALUES (?,?,?)
                                """,(
                                    new_u,
                                    row["nama"],
                                    0
                                ))

                        st.success("Akun berhasil dibuat")

                    else:
                        st.error("Username sudah ada")

    st.stop()

# ==================== SESSION ====================
role = st.session_state.role
username = st.session_state.username

# ==================== SIDEBAR ====================
with st.sidebar:

    st.markdown(f"## 👤 {username}")
    st.markdown("---")

    if st.button("🚪 Logout"):

        st.session_state.authenticated = False
        st.rerun()

# ==================== HEADER ====================
st.markdown(f"""
<div class="white-card">
    <h2>🏢 Selamat Datang, {username}</h2>
    <p>{datetime.now().strftime('%A, %d %B %Y')}</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# ==================== ROLE PABRIK ========================
# =========================================================
if role == "pabrik":

    total_stok = get_df("""
    SELECT SUM(stok) as total
    FROM produk
    """).iloc[0]["total"] or 0

    total_order = get_df("""
    SELECT COUNT(*) as total
    FROM pesanan
    WHERE status='Menunggu Konfirmasi'
    """).iloc[0]["total"] or 0

    selesai = get_df("""
    SELECT COUNT(*) as total
    FROM pesanan
    WHERE status='Selesai'
    """).iloc[0]["total"] or 0

    col1,col2,col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{total_stok}</div>
            <div>Total Stok Pabrik</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{total_order}</div>
            <div>Pesanan Pending</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{selesai}</div>
            <div>Pesanan Selesai</div>
        </div>
        """, unsafe_allow_html=True)

    # ===== WARNING STOK MENIPIS =====
    stok_tipis = get_df("""
    SELECT *
    FROM stok_distributor
    WHERE stok <= 50
    """)

    if not stok_tipis.empty:

        st.warning("⚠️ Ada stok distributor menipis")

        for _, row in stok_tipis.iterrows():

            st.info(
                f"Distributor {row['distributor']} | "
                f"{row['produk']} tersisa {row['stok']} pcs"
            )

    tab1,tab2,tab3,tab4,tab5 = st.tabs([
        "📦 Stok Pabrik",
        "➕ Tambah Produk",
        "🛒 Order Masuk",
        "✅ Konfirmasi",
        "📊 Semua Stok Distributor"
    ])

    # ==================== TAB 1 ====================
    with tab1:

        df_produk = get_df("""
        SELECT nama,stok,stok_minimum,harga_jual
        FROM produk
        """)

        df_produk["harga_jual"] = df_produk["harga_jual"].apply(
            lambda x: f"Rp {x:,.0f}".replace(",", ".")
        )

        st.dataframe(
            df_produk,
            use_container_width=True,
            hide_index=True
        )

    # ==================== TAB 2 ====================
    with tab2:

        with st.form("produk_baru"):

            nama = st.text_input("Nama Produk")

            stok = st.number_input(
                "Stok Awal",
                min_value=0
            )

            stok_min = st.number_input(
                "Stok Minimum",
                min_value=0,
                value=50
            )

            harga = st.number_input(
                "Harga",
                min_value=0
            )

            submit = st.form_submit_button(
                "Tambah Produk"
            )

            if submit:

                try:

                    run_query("""
                    INSERT INTO produk
                    (nama,stok,stok_minimum,harga_jual)
                    VALUES (?,?,?,?)
                    """,(
                        nama,
                        stok,
                        stok_min,
                        harga
                    ))

                    distributor_list = get_df("""
                    SELECT username
                    FROM users
                    WHERE role='distributor'
                    """)

                    for _, row in distributor_list.iterrows():

                        run_query("""
                        INSERT INTO stok_distributor
                        (distributor,produk,stok)
                        VALUES (?,?,?)
                        """,(
                            row["username"],
                            nama,
                            0
                        ))

                    st.success("Produk berhasil ditambahkan")
                    st.rerun()

                except:
                    st.error("Produk sudah ada")

    # ==================== TAB 3 ====================
    with tab3:

        df_order = get_df("""
        SELECT *
        FROM pesanan
        WHERE status='Menunggu Konfirmasi'
        """)

        if df_order.empty:

            st.info("Tidak ada pesanan")

        else:

            for _, row in df_order.iterrows():

                with st.expander(
                    f"{row['produk']} - {row['klien']}"
                ):

                    st.write(f"Jumlah : {row['jumlah']}")
                    st.write(f"Tanggal : {row['tanggal_masuk']}")

                    colA,colB = st.columns(2)

                    with colA:

                        if st.button(
                            "✅ Setujui",
                            key=f"ok_{row['id']}"
                        ):

                            run_query("""
                            UPDATE pesanan
                            SET status='Diproses'
                            WHERE id=?
                            """,(row['id'],))

                            run_query("""
                            UPDATE produk
                            SET stok = stok - ?
                            WHERE nama=?
                            """,(
                                row['jumlah'],
                                row['produk']
                            ))

                            if row["jenis_pesanan"] == "order_stok":

                                run_query("""
                                UPDATE stok_distributor
                                SET stok = stok + ?
                                WHERE distributor=? AND produk=?
                                """,(
                                    row['jumlah'],
                                    row['created_by'],
                                    row['produk']
                                ))

                            st.success("Pesanan diproses")
                            st.rerun()

                    with colB:

                        if st.button(
                            "❌ Tolak",
                            key=f"tolak_{row['id']}"
                        ):

                            run_query("""
                            UPDATE pesanan
                            SET status='Ditolak'
                            WHERE id=?
                            """,(row['id'],))

                            st.error("Pesanan ditolak")
                            st.rerun()

    # ==================== TAB 4 ====================
    with tab4:

        df_konf = get_df("""
        SELECT *
        FROM pesanan
        WHERE status='Diproses'
        """)

        if df_konf.empty:

            st.info("Tidak ada pesanan diproses")

        else:

            for _, row in df_konf.iterrows():

                with st.expander(
                    f"{row['produk']} - {row['klien']}"
                ):

                    if st.button(
                        "✅ Tandai Selesai",
                        key=f"done_{row['id']}"
                    ):

                        run_query("""
                        UPDATE pesanan
                        SET status='Selesai'
                        WHERE id=?
                        """,(row['id'],))

                        st.success("Pesanan selesai")
                        st.rerun()

    # ==================== TAB 5 ====================
    with tab5:

        df_all = get_df("""
        SELECT distributor,produk,stok
        FROM stok_distributor
        ORDER BY distributor ASC
        """)

        st.dataframe(
            df_all,
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# ==================== ROLE KLIEN =========================
# =========================================================
elif role == "klien":

    tab1,tab2 = st.tabs([
        "🏭 Pesan Makloon",
        "📋 Status Pesanan"
    ])

    with tab1:

        with st.form("makloon"):

            produk = st.text_input("Nama Produk")

            jumlah = st.number_input(
                "Jumlah Produksi",
                min_value=1
            )

            asal = st.text_input(
                "Asal PT / Brand"
            )

            catatan = st.text_area(
                "Catatan"
            )

            submit = st.form_submit_button(
                "Kirim Pesanan"
            )

            if submit:

                run_query("""
                INSERT INTO pesanan
                (klien,produk,jumlah,status,
                tanggal_masuk,jenis_pesanan,
                created_by)

                VALUES (?,?,?,?,?,?,?)
                """,(
                    asal,
                    produk,
                    jumlah,
                    "Menunggu Konfirmasi",
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "makloon",
                    username
                ))

                st.success("Pesanan berhasil dikirim")
                st.rerun()

    with tab2:

        df = get_df("""
        SELECT produk,jumlah,status,tanggal_masuk
        FROM pesanan
        WHERE created_by=?
        ORDER BY id DESC
        """,(username,))

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# ==================== ROLE DISTRIBUTOR ===================
# =========================================================
elif role == "distributor":

    tab1,tab2,tab3 = st.tabs([
        "📦 Lihat Produk",
        "🛒 Order Stok",
        "📊 Stok Saya"
    ])

    # ==================== TAB 1 ====================
    with tab1:

        df = get_df("""
        SELECT nama,stok,harga_jual
        FROM produk
        """)

        df["harga_jual"] = df["harga_jual"].apply(
            lambda x: f"Rp {x:,.0f}".replace(",", ".")
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    # ==================== TAB 2 ====================
    with tab2:

        produk = st.selectbox(
            "Pilih Produk",
            get_df(
                "SELECT nama FROM produk"
            )["nama"]
        )

        stok = get_df("""
        SELECT stok
        FROM produk
        WHERE nama=?
        """,(produk,)).iloc[0]["stok"]

        st.write(f"Stok tersedia di pabrik : {stok}")

        jumlah = st.number_input(
            "Jumlah",
            min_value=1,
            max_value=int(stok)
        )

        if st.button("Kirim Order"):

            run_query("""
            INSERT INTO pesanan
            (klien,produk,jumlah,status,
            tanggal_masuk,jenis_pesanan,
            created_by)

            VALUES (?,?,?,?,?,?,?)
            """,(
                username,
                produk,
                jumlah,
                "Menunggu Konfirmasi",
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                "order_stok",
                username
            ))

            st.success("Order berhasil dikirim")
            st.rerun()

    # ==================== TAB 3 ====================
    with tab3:

        df_stok = get_df("""
        SELECT produk,stok
        FROM stok_distributor
        WHERE distributor=?
        """,(username,))

        if df_stok.empty:

            st.info("Belum memiliki stok")

        else:

            st.dataframe(
                df_stok,
                use_container_width=True,
                hide_index=True
            )

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
🌴 © 2026 CV Amal Mulia — OrderStock
</div>
""", unsafe_allow_html=True)
