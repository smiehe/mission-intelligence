import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time

# Seiteneinstellungen
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- KONFIGURATION DER MISSIONEN (Dauer in Minuten) ---
MISSION_DATA = {
    "Operation: Agent Profile": 30,
    "The Intelligence Briefing (Nico)": 90,
    "The Deep-Dive Mission": 90,
    "Field Rations (Lunch)": 60,
    "Final Briefing (Wrap-up)": 30,
    "Field Operation (Museum)": 120,
    "Safe House Drinks & Dinner": 180
}

# --- INITIALISIERUNG SESSION STATE ---
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'active_mission' not in st.session_state:
    st.session_state.active_mission = "Operation: Agent Profile"
if 'mission_start_time' not in st.session_state:
    st.session_state.mission_start_time = time.time()

# --- DESIGN & KONTRAST (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; }
    .splash-container {
        text-align: center; margin-top: 10%; padding: 50px;
        border: 3px solid #00FF41; box-shadow: 0 0 50px #00FF41;
        background-color: #050505; font-family: 'Courier New', Courier, monospace;
    }
    .timer-box {
        font-family: 'Courier New', Courier, monospace;
        color: #00FF41; font-size: 2.5rem; text-align: center;
        padding: 15px; border: 2px solid #00FF41;
        background: rgba(0, 255, 65, 0.1); margin-bottom: 10px;
        text-shadow: 0 0 10px #00FF41;
    }
    /* Agenda Buttons Styling */
    .stButton>button {
        background-color: #000000 !important; color: #00FF41 !important;
        border: 1px solid #00FF41 !important; width: 100%; text-align: left !important;
        font-family: 'Courier New', Courier, monospace; margin-bottom: -10px;
    }
    .stButton>button:hover { border: 1px solid #FFFFFF !important; color: #FFFFFF !important; }
    
    /* Aktive Mission hervorheben */
    .active-mission-btn button { background-color: #00FF41 !important; color: #000000 !important; }
    
    .stTabs [data-baseweb="tab"] { color: #00FF41; border: 1px solid #00FF41; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTO-REFRESH (Jede Sekunde für den Timer) ---
if st.session_state.access_granted:
    st_autorefresh(interval=1000, key="timer_refresh")

# --- LOGIK: STARTBILDSCHIRM ---
if not st.session_state.access_granted:
    st.markdown("""
        <div class="splash-container">
            <h1 style="font-size: 4rem; letter-spacing: 10px;">MISSION:<br>INTELLIGENCE</h1>
            <p>> PCS DIVISION | Q1 2026<br>> STATUS: ENCRYPTED</p>
        </div>
    """, unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1,1,1])
    with col2:
        if st.button("ENTER HQ / MISSION STARTEN"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # --- HQ BEREICH ---
    st.sidebar.markdown("### ⏳ MISSION CLOCK")
    
    # Timer Logik für die AKTIVE MISSION
    duration_min = MISSION_DATA[st.session_state.active_mission]
    elapsed = time.time() - st.session_state.mission_start_time
    remaining = max(0, (duration_min * 60) - elapsed)
    
    mins, secs = divmod(int(remaining), 60)
    timer_color = "#00FF41" if remaining > 300 else "#FF0000"
    
    st.sidebar.markdown(f'<div class="timer-box" style="color:{timer_color}; border-color:{timer_color};">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center;'>Ziel: {st.session_state.active_mission}</p>", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.header("📍 WÄHLE MISSION")

    # Interaktive Agenda
    for mission in MISSION_DATA.keys():
        # Falls diese Mission gerade aktiv ist, bekommt der Button ein anderes Styling (via Label-Trick oder einfach Text)
        label = f"▶ {mission}" if mission == st.session_state.active_mission else mission
        if st.sidebar.button(label, key=f"btn_{mission}"):
            st.session_state.active_mission = mission
            st.session_state.mission_start_time = time.time()
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info("PCS-Team: Sören, Laura, Tamara, Janina, Christin, Leo, Claudine")

    # --- HAUPTBEREICH TABS ---
    st.title(f"🕵️‍♂️ HQ: {st.session_state.active_mission}")
    
    tab1, tab2, tab3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with tab1:
        st.header("Operation: Agent Profile")
        with st.form("checkin"):
            name = st.selectbox("PCS Agent:", ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"])
            codename = st.text_input("KI-Generierter Codename:")
            skill = st.text_input("KI-Spezialfähigkeit:")
            if st.form_submit_button("PROFIL AKTIVIEREN"):
                st.success(f"Agent {name} ist bereit.")

    with tab2:
        st.header("Die Sabotage-Akte")
        with st.form("sabotage"):
            p_name = st.text_input("Sabotage-Prozess:")
            desc = st.text_area("Details:")
            if st.form_submit_button("AKTE AN NICO SENDEN"):
                st.warning("Daten übertragen.")

    with tab3:
        st.header("💰 Operation: Golden Coin")
        voter = st.selectbox("PCS Agent für Voting:", ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"])
        st.write("Hier folgen die 100-Coins-Slider...")
