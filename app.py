import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Autorefresh laden (wichtig für den Timer)
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# 1. Basis-Konfiguration
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# 2. Verbindung zu Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def safe_read(ws_name):
    try:
        return conn.read(worksheet=ws_name, ttl="0")
    except Exception:
        if ws_name == "Profiles":
            return pd.DataFrame(columns=["Agent", "Codename", "Skill", "Avatar"])
        if ws_name == "Sabotage":
            return pd.DataFrame(columns=["Thema", "Details"])
        return pd.DataFrame()

# 3. Konstanten
AGENT_LIST = ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"]
BOSS_LIST = {
    "The Awakened One": "🦅",
    "Time Eater": "⏳",
    "Donu & Deca": "💎",
    "The Corrupt Heart": "❤️",
    "The Champ": "🏆"
}
MISSION_DATA = {
    "09:00": {"name": "Operation: Agent Profile", "duration": 30},
    "09:30": {"name": "The Intelligence Briefing (Nico)", "duration": 90},
    "11:15": {"name": "The Deep-Dive Mission", "duration": 90},
    "12:45": {"name": "Field Rations (Lunch)", "duration": 60},
    "13:45": {"name": "Final Briefing (Wrap-up)", "duration": 30},
    "15:30": {"name": "Field Operation (Museum)", "duration": 120},
    "17:30": {"name": "Safe House Drinks & Dinner", "duration": 180}
}

# 4. Session State Initialisierung
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state:
    st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state:
    st.session_state.mission_start_time = time.time()
if 'selected_boss' not in st.session_state:
    st.session_state.selected_boss = "The Awakened One"

# 5. Styling (KEIN GRAU, GROSSE SCHRIFT)
st.markdown("""
<style>
    /* Hintergrund & Schrift */
    .stApp { background-color: #000000; color: #FFFFFF; font-size: 1.2rem; }
    
    /* Splash Box */
    .splash-box {
        text-align: center; margin-top: 5%; padding: 40px;
        border: 4px solid #00FF41; background-color: #050505;
    }
    
    /* Sidebar Fix */
    [data-testid="stSidebar"] { background-color: #050505; border-right: 2px solid #00FF41; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] b, [data-testid="stSidebar"] span {
        color: #FFFFFF !important; font-size: 1.15rem !important; opacity: 1 !important;
    }

    /* Timer */
    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        color: #00FF41; font-size: 3rem; text-align: center;
        padding: 10px; border: 3px solid #00FF41; background: #000;
        font-weight: bold;
    }

    /* Header */
    .mission-header {
        width: 100%; background: #00FF41; color: #000000; padding: 12px 0;
        text-align: center; font-weight: bold; letter-spacing: 4px;
        margin-top: -65px; margin-bottom: 25px; font-size: 1.2rem;
    }

    /* Buttons */
    .stButton>button { 
        background-color: #00FF41 !important; color: #000000 !important; 
        font-weight: bold !important; font-size: 1.2rem !important; height: 3.5rem;
    }
    .stButton>button:hover { background-color: #FFFFFF !important; }

    /* Karten */
    .agent-card { border: 2px solid #00FF41; padding: 15px; background: #111; border-radius: 10px; margin-bottom: 10px; }
    .agent-card b { color: #00FF41; font-size: 1.5rem; }
    
    /* Inputs & Labels */
    label { color: #00FF41 !important; font-size: 1.3rem !important; font-weight: bold !important; }
    input, textarea, select { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border: 2px solid #00FF41 !important; font-size: 1.1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# 6. Timer-Tick
if st.session_state.access_granted and st_autorefresh:
    st_autorefresh(interval=2000, key="global_tick")

# 7. Startbildschirm (Splash)
if not st.session_state.access_granted:
    st.markdown('<div class="splash-box"><h1 style="color:#00FF41; font-size:4rem;">MISSION:<br>INTELLIGENCE</h1><p style="color:#FFF; font-size:1.5rem;">PCS DIVISION | Q1 2026</p></div>', unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1,2,1])
    with col_mid:
        st.write("")
        st.markdown("<p style='text-align:center; color:#00FF41; font-weight:bold; font-size:1.4rem;'>WÄHLE DEINEN BOSS-AVATAR:</p>", unsafe_allow_html=True)
        boss_name = st.radio("Bosse:", list(BOSS_LIST.keys()), horizontal=True, label_visibility="collapsed")
        st.session_state.selected_boss = boss_name
        st.markdown(f"<div style='text-align:center; font-size:8rem;'>{BOSS_LIST[boss_name]}</div>", unsafe_allow_html=True)
        
        if st.button("ENTER HQ / IDENTITÄT BESTÄTIGEN"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()

# 8. HQ-Bereich (Main App)
else:
    # Top Banner
    st.markdown('<div class="mission-header">NETWORK ACCESS GRANTED // BOSS MODE: ACTIVE // PCS HQ</div>', unsafe_allow_html=True)

    # SIDEBAR
    with st.sidebar:
        st.markdown("### ⏳ MISSION CLOCK")
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        rem_sec = max(0, (active_info['duration'] * 60) - (time.time() - st.session_state.mission_start_time))
        m, s = divmod(int(rem_sec), 60)
        t_color = "#00FF41" if rem_sec > 300 else "#FF4B4B"
        st.markdown(f'<div class="timer-display" style="color:{t_color}; border-color:{t_color};">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("📍 EINSATZPLAN")
        for k, d in MISSION_DATA.items():
            lbl = f"{k} | {d['name']}"
            if k == st.session_state.active_mission_key: lbl = f"▶ {lbl}"
            if st.button(lbl, key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()
        
        st.markdown("---")
        st.write("**TEAM IM EINSATZ:**")
        st.write("
