import streamlit as st

# Grundkonfiguration (Tab-Name und Icon)
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- DER "NANO-BANANA" CODE-HEADER (CSS statt Bild) ---
st.markdown("""
    <style>
    /* Hintergrund & Matrix-Grün */
    .stApp { background-color: #0B0E14; color: #00FF41; }
    
    /* Animierter High-Tech Header */
    .hero-section {
        background: linear-gradient(180deg, #1A1C23 0%, #0B0E14 100%);
        padding: 3rem;
        border: 2px solid #00FF41;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.2);
        margin-bottom: 2rem;
        font-family: 'Courier New', Courier, monospace;
    }
    
    .glitch-title {
        font-size: 4rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 10px;
        margin: 0;
        text-shadow: 0 0 15px #00FF41;
    }
    
    .status-text {
        font-size: 1.2rem;
        color: #00FF41;
        opacity: 0.8;
        border-right: 2px solid #00FF41;
        white-space: nowrap;
        overflow: hidden;
        margin: 10px auto;
        width: fit-content;
        animation: typing 3.5s steps(40, end), blink .75s step-end infinite;
    }

    @keyframes typing { from { width: 0 } to { width: 100% } }
    @keyframes blink { from, to { border-color: transparent } 50% { border-color: #00FF41 } }

    /* Tabs und Buttons */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1A1C23;
        color: #00FF41;
        border-radius: 5px 5px 0 0;
        border: 1px solid #00FF41;
    }
    .stButton>button {
        background-color: #00FF41 !important;
        color: #0B0E14 !important;
        font-weight: bold !important;
        width: 100%;
        border: none !important;
    }
    </style>
    
    <div class="hero-section">
        <p style="margin:0; opacity:0.5;">[ SECURE CONNECTION ESTABLISHED ]</p>
        <h1 class="glitch-title">MISSION: INTELLIGENCE</h1>
        <div class="status-text">SYSTEM STATUS: ACTIVE | AGENT ACCESS GRANTED...</div>
        <p style="margin:0; font-size: 0.8rem;">QUARTERDAY Q1 2026 - PROJECT MANAGEMENT DIVISION</p>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Agenda) ---
st.sidebar.markdown("### 🔐 HQ-ZENTRALE")
st.sidebar.markdown(f"**Agenten im Feld:** \nClaudine, Sören, Laura, Tamara, Janina, Christin, Leo")
st.sidebar.markdown("---")
st.sidebar.header("📍 Einsatzplan")
agenda = {
    "09:00": "Operation: Agent Profile",
    "09:30": "The Intelligence Briefing (Niko)",
    "11:15": "The Deep-Dive Mission (Workshop)",
    "12:45": "Field Rations (Lunch)",
    "15:30": "Field Operation (Museum)",
    "17:30": "Safe House (Dinner)"
}
for zeit, event in agenda.items():
    st.sidebar.write(f"**{zeit}** : {event}")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["👤 AGENTEN-CHECK-IN", "📂 SABOTAGE-AKTE", "💡 KI-MISSIONEN"])

with tab1:
    st.header("Operation: Agent Profile")
    st.info("Nutze eine KI, um deinen Codenamen und eine Spezialfähigkeit basierend auf deinen PM-Stärken zu erstellen.")
    with st.form("checkin"):
        name = st.selectbox("Echter Name:", ["---", "Claudine", "Sören", "Laura", "Tamara", "Janina", "Christin", "Leo"])
        codename = st.text_input("KI-Generierter Codename:")
        skill = st.text_input("Deine KI-Spezialfähigkeit:")
        if st.form_submit_button("PROFIL AKTIVIEREN"):
            if name != "---" and codename:
                st.success(f"Agent '{codename}' ({name}) wurde im System registriert.")
                st.balloons()
            else:
                st.error("Identität konnte nicht verifiziert werden. Bitte alle Felder ausfüllen.")

with tab2:
    st.header("Die Sabotage-Akte")
    st.write("Welche Prozesse fühlen sich wie 'absichtliche Sabotage' an?")
    with st.form("sabotage"):
        prozess = st.text_input("Name des Sabotage-Prozesses:")
        beschreibung = st.text_area("Details der Ineffizienz:")
        schwere = st.slider("Schweregrad (1=Leicht, 10=Mission Critical)", 1, 10, 5)
        if st.form_submit_button("AKTE VERSCHLÜSSELT SENDEN"):
            st.warning("Akte wurde an 'The Intelligence' (Niko) übermittelt.")

with tab3:
    st.header("Mission Dashboard")
    st.write("Hier werden die 3 Pilotprojekte dokumentiert.")
    st.info("Bereich wird um 11:15 Uhr nach dem Briefing freigeschaltet.")
