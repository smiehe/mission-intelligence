import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Versuch, Autorefresh zu laden
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# Seiteneinstellungen
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- VERBINDUNG ZUM ZENTRALSPEICHER ---
conn = st.connection("gsheets", type=GSheetsConnection)

def safe_read(worksheet_name):
    try:
        return conn.read(worksheet=worksheet_name, ttl="0")
    except Exception:
        if worksheet_name == "Profiles":
            return pd.DataFrame(columns=["Agent", "Codename", "Skill", "Avatar"])
        if worksheet_name == "Sabotage":
            return pd.DataFrame(columns=["Thema", "Details"])
        return pd.DataFrame()

# --- KONFIGURATION ---
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

# --- SESSION STATE ---
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state:
    st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state:
    st.session_state.mission_start_time = time.time()
if 'selected_boss' not in st.session_state:
    st.session_state.selected_boss = "The Awakened One"

# --- DESIGN & CSS (KEIN GRAU, MAX KONTRAST) ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #FFFFFF; font-size: 1.2rem; }
    
    /* Splash Screen */
    .splash-box {
        text-align: center; margin-top: 5%; padding: 50px;
        border: 4px solid #00FF41; background-color: #050505;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #050505; border-right: 2px solid #00FF41; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] b, [data-testid="stSidebar"] span {
        color: #FFFFFF !important; font-size: 1.1rem !important; opacity: 1 !important;
    }

    /* Timer */
    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        color: #00FF41; font-size: 2.8rem; text-align: center;
        padding: 10px; border: 3px solid #00FF41; background: #000;
    }

    /* Header */
    .mission-header {
        width: 100%; background: #00FF41; color: #000000; padding: 10px 0;
        text-align: center; font-weight: bold; letter-spacing: 3px;
        margin-top: -65px; margin-bottom: 20px; font-size: 1.1rem;
    }

    /* Buttons */
    .stButton>button { 
        background-color: #00FF41 !important; color: #000000 !important; 
        font-weight: bold !important; font-size: 1.2rem !important; height: 3.5rem;
    }
    .stButton>button:hover { background-color: #FFFFFF !important; }

    /* Karten */
    .agent-card { border: 2px solid #00FF41; padding: 15px; background: #111; border-radius: 10px; margin-bottom: 10px; }
    .agent-card b { color: #00FF41; font-size: 1.4rem; }
    
    /* Inputs */
    label { color: #00FF41 !important; font-size: 1.3rem !important; font-weight: bold !important; }
    input, textarea, select { background-color: #000000 !important; color: #FFFFFF !important; border: 2px solid #00FF41 !important; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] { color: #00FF41 !important; border: 1px solid #00FF41 !important; font-size: 1.2rem !important; }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !
