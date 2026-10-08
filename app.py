import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. CONFIGURATION PAGE & CONNECTION
# ==========================================
st.set_page_config(page_title="Sales Pipeline & CRM", layout="wide")

# Inisialisasi Koneksi Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """Mengambil data paling update dari Google Sheet 'CRM_DBase'"""
    try:
        df = conn.read(ttl=0)
        # Menghapus baris yang seluruh kolomnya kosong
        df = df.dropna(how="all")
        
        # Memastikan seluruh kolom wajib tersedia
        expected_cols = ["id", "nama", "kontak", "sumber", "kualifikasi", "status", "tanggal"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception as e:
        # Fallback jika sheet belum bisa dibaca
        return pd.DataFrame(columns=["id", "nama", "kontak", "sumber", "kualifikasi", "status", "tanggal"])

def save_data(df):
    """Menyimpan/menimpa seluruh DataFrame kembali ke Google Sheet 'CRM_DBase'"""
    conn.update(data=df)

# Read Data awal
df_leads = load_data()

STAGES = [
    "Lead Masuk", 
    "Lead Qualification", 
    "Follow-Up Otomatis", 
    "Pipeline Penjualan", 
    "Closing Deal", 
    "After-Sales Service"
]

# Credentials Admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Navigation Sidebar Utama
access_type = st.sidebar.radio("Akses Aplikasi", ["Form Pelanggan (Publik)", "Login Admin"])


# ==========================================
# 2. HALAMAN PUBLIK (CALON PELANGGAN)
# ==========================================
if access_type == "Form Pelanggan (Publik)":
    st.title("📋 Form Konsultasi & Layanan")
    st.write("Silakan isi data diri Anda di bawah ini untuk terhubung dengan tim kami.")
    
    with st.form("public_lead_form", clear_on_submit=True):
        nama = st.text_input("Nama Lengkap")
        whatsapp = st.text_input("Nomor WhatsApp (Aktif)")
        kebutuhan = st.text_area("Apa yang bisa kami bantu?")
        
        submitted = st.form_submit_button("Kirim Data")
        
        if submitted:
            if nama and whatsapp:
                current_df = load_data()
                
                # Hitung ID baru
                new_id = len(current_df) + 1
                
                new_row = pd.DataFrame([{
                    "id": new_id,
                    "nama": nama,
                    "kontak": whatsapp,
                    "sumber": "Website Form (Publik)",
                    "kualifikasi": "Warm",
                    "status": "Lead Masuk",
                    "tanggal": str(datetime.date.today())
                }])
                
                # Gabungkan dan simpan ke Google Sheet
                updated_df = pd.concat([current_df, new_row], ignore_index=True)
                save_data(updated_df)
                
                st.success("Terima kasih! Data Anda telah terkirim. Tim kami akan segera menghubungi Anda via WhatsApp.")
            else:
                st.error("Mohon isi Nama Lengkap dan Nomor WhatsApp Anda.")


# ==========================================
# 3. HALAMAN LOGIN / DASHBOARD ADMIN
# ==========================================
elif access_type == "Login Admin":
    if not st.session_state.logged_in:
        st.title("🔐 Login Control Panel Admin")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Masuk")
            
            if login_button:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.success("Login berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
    else:
        st.sidebar.markdown("---")
        st.sidebar.write("👤 Status: **Logged In as Admin**")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        menu = st.sidebar.radio("Navigation Admin", ["Dashboard", "Kanban Pipeline", "Tambah Lead Manual", "Kirim Follow-Up"])

        # Ambil data terbaru untuk Admin
        df_leads = load_data()

        # ------------------------------------------
        # A. DASHBOARD ADMIN
        # ------------------------------------------
        if menu == "Dashboard":
            st.title("📊 CRM & Sales Pipeline Overview")
            
            if st.button("🔄 Refresh Data Google Sheets"):
                st.rerun()

            total_leads = len(df_leads)
            closing = len(df_leads[df_leads["status"].isin(["Closing Deal", "After-Sales Service"])]) if total_leads > 0 else 0
            conversion_rate = (closing / total_leads * 100) if total_leads > 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Leads", total_leads)
            col2.metric("Deal Closing", closing)
            col3.metric("Conversion Rate", f"{conversion_rate:.1f}%")

            st.subheader("Data Arsip Google Sheets (`CRM_DBase`)")
            st.dataframe(df_leads, use_container_width=True)

        # ------------------------------------------
        # B. KANBAN PIPELINE
        # ------------------------------------------
        elif menu == "Kanban Pipeline":
            st.title("🗂️ Sales Pipeline Board")
            cols = st.columns(len(STAGES))

            for idx, stage in enumerate(STAGES):
                with cols[idx]:
                    st.markdown(f"### {stage}")
                    stage_leads = df_leads[df_leads["status"] == stage]
                    
                    for _, lead in stage_leads.iterrows():
                        with st.expander(f"👤 {lead['nama']}", expanded=True):
                            st.caption(f"📱 {lead['kontak']}")
                            st.caption(f"🏷️ Kategori: **{lead['kualifikasi']}**")
                            st.caption(f"📌 Sumber: {lead['sumber']}")
                            
                            current_index = STAGES.index(lead["status"]) if lead["status"] in STAGES else 0
                            new_status = st.selectbox(
                                "Pindah Status:", 
                                STAGES, 
                                index=current_index, 
                                key=f"status_{lead['id']}"
                            )
                            
                            if new_status != lead["status"]:
                                df_leads.loc[df_leads["id"] == lead["id"], "status"] = new_status
                                save_data(df_leads)
                                st.success("Status di-update ke Google Sheets!")
                                st.rerun()

        # ------------------------------------------
        # C. TAMBA