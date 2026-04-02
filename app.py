import streamlit as st
import time

# Versuch, das Autorefresh-Modul zu laden
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# Seiteneinstellungen
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- KONFIGURATION DER MISSIONEN ---
MISSION_DATA = {
    "09:00": {"name": "Operation: Agent Profile", "duration": 30},
    "09:30": {"name": "The Intelligence Briefing (Nico)", "duration": 90},
    "11:15": {"name": "The Deep-Dive Mission", "duration": 90},
    "12:45": {"name": "Field Rations (Lunch)", "duration": 60},
    "13:45": {"name": "Final Briefing (Wrap-up)", "duration": 30},
    "15:30": {"name": "Field Operation (Museum)", "duration": 120},
    "17:30": {"name": "Safe House Drinks & Dinner", "duration": 180}
}

# --- INITIALISIERUNG SESSION STATE ---
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state:
    st.session_state.active_mission_key = "09:00"
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
        color: #00FF41; font-size: 3rem; text-align: center;
        padding: 15px; border: 2px solid #00FF41;
        background: rgba(0, 255, 65, 0.1); margin-bottom: 5px;
        text-shadow: 0 0 15px #00FF41;
    }
    .stButton>button {
        background-color: #000000 !important; color: #00FF41 !important;
        border: 1px solid #00FF41 !important; width: 100%; text-align: left !important;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton>button:hover { border: 1px solid #FFFFFF !important; color: #FFFFFF !important; }
    .stTabs [data-baseweb="tab"] { color: #00FF41; border: 1px solid #00FF41; }
    input, textarea, select { 
        background-color: #111 !important; 
        color: #00FF41 !important; 
        border: 1px solid #00FF41 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- AUTO-REFRESH (Nur wenn eingeloggt) ---
if st.session_state.access_granted and st_autorefresh:
    st_autorefresh(interval=1000, key="timer_refresh")

# --- LOGIK: STARTBILDSCHIRM ---
if not st.session_state.access_granted:
    st.markdown("""
        <div class="splash-container">
            <h1 style="font-size: 4rem; letter-spacing: 10px;">MISSION:<br>INTELLIGENCE</h1>
            <p>> PCS DIVISION | QUARTERDAY Q1 2026<br>> STATUS: ENCRYPTED</p>
        </div>
    """, unsafe_allow_html=True)
    _, col2, _ = st.columns([1,1,1])
    with col2:
        if st.button("ENTER HQ / MISSION STARTEN"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # --- HQ SIDEBAR ---
    st.sidebar.markdown("### ⏳ MISSION CLOCK")
    
    # Timer Logik
    mission_info = MISSION_DATA[st.session_state.active_mission_key]
    duration_sec = mission_info['duration'] * 60
    elapsed = time.time() - st.session_state.mission_start_time
    remaining = max(0, duration_sec - elapsed)
    
    mins, secs = divmod(int(remaining), 60)
    timer_col = "#00FF41" if remaining > 300 else "#FF0000" # Rot unter 5 Min
    
    st.sidebar.markdown(f'<div class="timer-box" style="color:{timer_col}; border-color:{timer_col};">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center;'>AKTIV: {mission_info['name']}</p>", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.header("📍 EINSATZPLAN")

    for time_key, data in MISSION_DATA.items():
        label = f"{time_key} | {data['name']}"
        if time_key == st.session_state.active_mission_key:
            label = f"▶ {label}"
            
        if st.sidebar.button(label, key=f"btn_{time_key}"):
            st.session_state.active_mission_key = time_key
            st.session_state.mission_start_time = time.time()
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info("PCS-Team: Sören, Laura, Tamara, Janina, Christin, Leo, Claudine")

    # --- HAUPTBEREICH ---
    st.title(f"🕵️‍♂️ HQ: {mission_info['name']}")
    
    tab1, tab2, tab3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with tab1:
        st.header("Operation: Agent Profile")
        with st.form("checkin"):
            name = st.selectbox("PCS Agent:", ["Sören", "Laura
