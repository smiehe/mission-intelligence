import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time

# Seiteneinstellungen
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- INITIALISIERUNG SESSION STATE ---
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- DESIGN & KONTRAST ---
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
        font-family: 'Courier New', Courier, monospace;
    }
    .timer-box {
        font-family: 'Courier New', Courier, monospace;
        color: #00FF41;
        font-size: 2.5rem;
        text-align: center;
        padding: 15px;
        border: 2px solid #00FF41;
        background: rgba(0, 255, 65, 0.1);
        margin-bottom: 20px;
        text-shadow: 0 0 10px #00FF41;
    }
    .stButton>button {
        background-color: #00FF41 !important;
        color: #000000 !important;
        font-weight: bold !important;
        width: 100%;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"] { color: #00FF41; border: 1px solid #00FF41; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTO-REFRESH (Jede Sekunde aktualisieren, wenn HQ offen ist) ---
if st.session_state.access_granted:
    st_autorefresh(interval=1000, key="datarefresh")

# --- LOGIK: STARTBILDSCHIRM ---
if not st.session_state.access_granted:
    st.markdown("""
        <div class="splash-container">
            <h1 style="font-size: 4rem; letter-spacing: 10px;">MISSION:<br>INTELLIGENCE</h1>
            <p>> DIVISION: PROJECT COORDINATION<br>> STATUS: ENCRYPTED</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1,1,1])
    with col2:
        if st.button("ENTER HQ / MISSION STARTEN"):
            st.session_state.access_granted = True
            st.session_state.start_time = time.time() # Hier wird die Zeit genommen!
            st.rerun()

else:
    # --- HQ BEREICH ---
    st.markdown("<p style='text-align:right; opacity:0.6;'>[ PCS AGENT LOGGED IN ]</p>", unsafe_allow_html=True)
    
    # --- SIDEBAR MIT COUNTDOWN ---
    st.sidebar.markdown("### ⏳ MISSION CLOCK")
    
    # Timer Logik: 30 Minuten ab Startzeit
    WARMUP_DURATION = 30 * 60 # 30 Minuten in Sekunden
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, WARMUP_DURATION - elapsed)
    
    mins, secs = divmod(int(remaining), 60)
    timer_color = "#00FF41" if remaining > 300 else "#FF0000" # Rot ab 5 Minuten Rest
    
    st.sidebar.markdown(f'<div class="timer-box" style="color:{timer_color}; border-color:{timer_color};">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
    st.sidebar.caption("Verbleibende Zeit für Operation: Agent Profile")
    
    if remaining == 0:
        st.sidebar.error("MISSION TIME EXPIRED!")

    st.sidebar.markdown("---")
    st.sidebar.header("📍 Einsatzplan")
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

    # --- TABS ---
    st.title("🕵️‍♂️ MISSION: INTELLIGENCE HQ")
    tab1, tab2, tab3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with tab1:
        st.header("Operation: Agent Profile")
        with st.form("checkin"):
            name = st.selectbox("PCS Agent wählen:", ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"])
            codename = st.text_input("KI-Generierter Codename:")
            skill = st.text_input("KI-Spezialfähigkeit:")
            if st.form_submit_button("PROFIL AKTIVIEREN"):
                st.success(f"PCS Agent '{name}' aktiv.")

    with tab2:
        st.header("Die Sabotage-Akte")
        with st.form("sabotage"):
            p_name = st.text_input("Sabotage-Prozess:")
            desc = st.text_area("Details:")
            if st.form_submit_button("AN NICO SENDEN"):
                st.warning("Akte übertragen.")

    with tab3:
        st.header("💰 Operation: Golden Coin")
        st.info("Budget-Verteilung (100 Coins Methode)")
        voter = st.selectbox("Identität für Voting:", ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"], key="voter_tab3")
        # Hier folgt die Coin-Logik (Slider), sobald die Datenbank steht
