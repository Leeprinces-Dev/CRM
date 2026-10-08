import streamlit as st
import pandas as pd
import datetime

# Configuration Page
st.set_page_config(page_title="Sales Pipeline & CRM", layout="wide")

# Initialize Session State
if "leads" not in st.session_state:
    st.session_state.leads = pd.DataFrame([
        {
            "id": 1, 
            "nama": "Budi Santoso", 
            "kontak": "08123456789", 
            "sumber": "Meta Ads", 
            "kualifikasi": "Hot", 
            "status": "Lead Masuk",
            "tanggal": "2026-10-01"
        },
        {
            "id": 2, 
            "nama": "Siti Rahma", 
            "kontak": "08987654321", 
            "sumber": "Website Form", 
            "kualifikasi": "Warm", 
            "status": "Lead Qualification",
            "tanggal": "2026-10-03"
        }
    ])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

STAGES = [
    "Lead Masuk", 
    "Lead Qualification", 
    "Follow-Up Otomatis", 
    "Pipeline Penjualan", 
    "Closing Deal", 
    "After-Sales Service"
]

# CREDENTIALS ADMIN (Ganti sesuai kebutuhan)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"

# Sidebar Navigation Utama
access_type = st.sidebar.radio("Akses Aplikasi", ["Form Pelanggan (Publik)", "Login Admin"])

# ==========================================
# 1. HALAMAN PUBLIK (CALON PELANGGAN)
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
                new_id = len(st.session_state.leads) + 1
                new_row = {
                    "id": new_id,
                    "nama": nama,
                    "kontak": whatsapp,
                    "sumber": "Website Form (Publik)",
                    "kualifikasi": "Warm",
                    "status": "Lead Masuk",
                    "tanggal": str(datetime.date.today())
                }
                st.session_state.leads = pd.concat([st.session_state.leads, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Terima kasih! Data Anda telah terkirim. Tim kami akan segera menghubungi Anda via WhatsApp.")
            else:
                st.error("Mohon isi Nama Lengkap dan Nomor WhatsApp Anda.")

# ==========================================
# 2. HALAMAN LOGIN / DASHBOARD ADMIN
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
        st.sidebar.write("👤 Status: **LoggedIn as Admin**")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        menu = st.sidebar.radio("Navigation Admin", ["Dashboard", "Kanban Pipeline", "Tambah Lead Manual", "Kirim Follow-Up"])

        # DASHBOARD
        if menu == "Dashboard":
            st.title("📊 CRM & Sales Pipeline Overview")
            
            df = st.session_state.leads
            total_leads = len(df)
            closing = len(df[df["status"].isin(["Closing Deal", "After-Sales Service"])])
            conversion_rate = (closing / total_leads * 100) if total_leads > 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Leads", total_leads)
            col2.metric("Deal Closing", closing)
            col3.metric("Conversion Rate", f"{conversion_rate:.1f}%")

            st.subheader("Data Lead Terbaru")
            st.dataframe(df, use_container_width=True)

        # KANBAN PIPELINE
        elif menu == "Kanban Pipeline":
            st.title("🗂️ Sales Pipeline Board")
            cols = st.columns(len(STAGES))
            df = st.session_state.leads

            for idx, stage in enumerate(STAGES):
                with cols[idx]:
                    st.markdown(f"### {stage}")
                    stage_leads = df[df["status"] == stage]
                    
                    for _, lead in stage_leads.iterrows():
                        with st.expander(f"👤 {lead['nama']}", expanded=True):
                            st.caption(f"📱 {lead['kontak']}")
                            st.caption(f"🏷️ Kategori: **{lead['kualifikasi']}**")
                            st.caption(f"📌 Sumber: {lead['sumber']}")
                            
                            new_status = st.selectbox(
                                "Pindah Status:", 
                                STAGES, 
                                index=STAGES.index(lead["status"]), 
                                key=f"status_{lead['id']}"
                            )
                            
                            if new_status != lead["status"]:
                                st.session_state.leads.loc[
                                    st.session_state.leads["id"] == lead["id"], "status"
                                ] = new_status
                                st.rerun()

        # TAMBAH LEAD MANUAL
        elif menu == "Tambah Lead Manual":
            st.title("➕ Input Lead Baru (Manual)")
            
            with st.form("add_lead_form"):
                nama = st.text_input("Nama Lengkap / Perusahaan")
                kontak = st.text_input("Nomor WhatsApp / Telepon")
                sumber = st.selectbox("Sumber Lead", ["Meta Ads", "Google Ads", "Website Form", "Instagram DM", "Referral"])
                kualifikasi = st.selectbox("Hasil Kualifikasi Awal", ["Hot", "Warm", "Cold"])
                
                submitted = st.form_submit_button("Simpan Lead")
                
                if submitted:
                    new_id = len(st.session_state.leads) + 1
                    new_row = {
                        "id": new_id,
                        "nama": nama,
                        "kontak": kontak,
                        "sumber": sumber,
                        "kualifikasi": kualifikasi,
                        "status": "Lead Masuk",
                        "tanggal": str(datetime.date.today())
                    }
                    st.session_state.leads = pd.concat([st.session_state.leads, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"Lead '{nama}' berhasil ditambahkan!")

        # FOLLOW-UP AUTOMATION
        elif menu == "Kirim Follow-Up":
            st.title("🤖 Simulator Follow-Up Otomatis")
            
            lead_names = st.session_state.leads["nama"].tolist()
            if lead_names:
                selected_lead = st.selectbox("Pilih Lead untuk Follow-Up:", lead_names)
                lead_info = st.session_state.leads[st.session_state.leads["nama"] == selected_lead].iloc[0]
                
                st.write(f"**Kontak:** {lead_info['kontak']}")
                st.write(f"**Status Saat Ini:** {lead_info['status']}")
                
                template_pesan = f"Halo Kak {lead_info['nama']},\n\nTerima kasih telah berkonsultasi dengan kami.\nApakah ada hal lain yang bisa kami bantu?"
                pesan = st.text_area("Pesan WhatsApp / Telegram:", template_pesan, height=150)
                
                if st.button("Kirim Pesan Otomatis (Webhook Test)"):
                    st.success(f"Pesan berhasil dikirimkan ke {lead_info['kontak']}!")
            else:
                st.info("Belum ada data lead.")