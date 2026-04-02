import streamlit as st
import time
from datetime import datetime, timedelta

# Seiteneinstellungen
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- INITIALISIERUNG SESSION STATE ---
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()

# --- DESIGN & KONTRAST (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; }
    
    .splash-container {
        text-align: center;
        margin-top: 10%;
        padding: 50px;
        border: 3px solid #00FF41;
        box-shadow: 0 0 50px #00FF41;
        background-color: #050505;
    }
    
    /* Timer Styling */
    .timer-box {
        font-family: 'Courier New', Courier, monospace;
        color: #00FF41;
        font-size: 2rem;
        text-align: center;
        padding: 10px;
        border: 1px solid #00FF41;
        margin-bottom: 20px;
        background: rgba(0, 255, 65, 0.1);
    }

    .stButton>button {
        background-color: #00FF41 !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        border: none !important;
    }
    
    /* Tabs & Input Felder */
    .stTabs [data-baseweb="tab"] { color: #00FF41; border: 1px solid #00FF41; }
    .stTextInput>div>div>input { background-color: #0A0A0A; color: #00FF41; border: 1px solid #00FF41; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIK: STARTBILDSCHIRM ODER HQ ---
if not st.session_state.access_granted:
    st.markdown("""
        <div class="splash-container">
            <h1 style="font-size: 4rem; letter-spacing: 10px;">MISSION:<br>INTELLIGENCE</h1>
            <p style="font-family: 'Courier New'; font-size: 1.2rem;">> DIVISION: PROJECT COORDINATION<br>> STATUS: ENCRYPTED</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1,1,1])
    with col2:
        if st.button("ENTER HQ / IDENTITÄT BESTÄTIGEN"):
            st.session_state.access_granted = True
            st.rerun()

else:
    # --- HQ BEREICH ---
    st.markdown("<p style='text-align:right; opacity:0.6;'>[ PCS AGENT LOGGED IN ]</p>", unsafe_allow_html=True)
    
    # --- SIDEBAR MIT TIMER & AGENDA ---
    st.sidebar.markdown("### ⏳ MISSION CLOCK")
    
    # Timer Logik: Countdown bis zum Ende des Warmups (09:30 Uhr)
    # Wenn die Zeit vorbei ist, zählt er nicht weiter runter.
    now = datetime.now()
    # Wir setzen die Deadline für heute 09:30 Uhr
    deadline = now.replace(hour=9, minute=30, second=0, microsecond=0)
    
    if now < deadline:
        diff = deadline - now
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        st.sidebar.markdown(f'<div class="timer-box">{minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
        st.sidebar.caption("Verbleibende Zeit bis Ende Operation: Agent Profile")
    else:
        st.sidebar.markdown('<div class="timer-box">00:00</div>', unsafe_allow_html=True)
        st.sidebar.error("WARMUP BEENDET - BRIEFING STARTET")

    st.sidebar.markdown("---")
    st.sidebar.header("📍 Einsatzplan")
    # Agenda aktualisiert: Nico mit 'c', Claudine am Ende, Wrap-up eingefügt
    agenda = {
        "09:00": "Operation: Agent Profile (Warmup)",
        "09:30": "The Intelligence Briefing (Nico)",
        "11:15": "The Deep-Dive Mission (Workshop)",
        "12:45": "Field Rations (Lunch)",
        "13:45": "Final Briefing (Wrap-up)",
        "15:30": "Field Operation (Museum)",
        "17:30": "Safe House Drinks & Dinner"
    }
    for zeit, event in agenda.items():
        st.sidebar.write(f"**{zeit}** : {event}")

    # --- HAUPTINHALT ---
    st.title("🕵️‍♂️ MISSION: INTELLIGENCE HQ")
    
    tab1, tab2, tab3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with tab1:
        st.header("Operation: Agent Profile")
        with st.form("checkin"):
            name = st.selectbox("PCS Agent wählen:", ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"])
            codename = st.text_input("KI-Generierter Codename:")
            skill = st.text_input("KI-Spezialfähigkeit:")
            if st.form_submit_button("PROFIL AKTIVIEREN"):
                st.success(f"PCS Agent '{name}' (Codename: {codename}) aktiv im System.")

    with tab2:
        st.header("Die Sabotage-Akte")
        st.write("Identifizieren Sie die Prozesse, die unsere Coordination sabotieren.")
        with st.form("sabotage"):
            p_name = st.text_input("Sabotage-Prozess:")
            desc = st.text_area("Details der Ineffizienz:")
            if st.form_submit_button("AKTE AN NICO SENDEN"):
                st.warning("Akte wurde verschlüsselt übertragen.")

    with tab3:
        st.header("💰 Operation: Golden Coin")
        # 100 Coins Methode (Skelett)
        voter = st.selectbox("Identität für Voting:", ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"])
        st.info("Das Voting wird während der 'Deep-Dive Mission' freigeschaltet.")
