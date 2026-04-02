import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Autorefresh für den Live-Timer
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# 1. Basis-Konfiguration
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# 2. Zentralspeicher (Google Sheets)
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

# 3. Konstanten & Team
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

# 4. System-Status (Session State Initialisierung)
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state:
    st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state:
    st.session_state.mission_start_time = time.time()
if 'selected_boss' not in st.session_state:
    st.session_state.selected_boss = "The Awakened One"

# 5. High-Contrast Design (Alles Weiss/Grün auf Schwarz)
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #FFFFFF; font-size: 1.2rem; }
    
    .splash-box {
        text-align: center; margin-top: 5%; padding: 50px;
        border: 4px solid #00FF41; background-color: #050505;
        box-shadow: 0 0 40px #00FF41;
    }
    
    [data-testid="stSidebar"] { background-color: #050505; border-right: 3px solid #00FF41; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] b, [data-testid="stSidebar"] span, [data-testid="stSidebar"] li {
        color: #FFFFFF !important; font-size: 1.2rem !important; opacity: 1 !important;
    }

    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        color: #00FF41; font-size: 3.2rem; text-align: center;
        padding: 15px; border: 3px solid #00FF41; background: #000;
        font-weight: bold; text-shadow: 0 0 10px #00FF41;
    }

    .mission-header {
        width: 100%; background: #00FF41; color: #000000; padding: 15px 0;
        text-align: center; font-weight: bold; letter-spacing: 5px;
        margin-top: -70px; margin-bottom: 30px; font-size: 1.3rem;
    }

    .stButton>button { 
        background-color: #00FF41 !important; color: #000000 !important; 
        font-weight: bold !important; font-size: 1.2rem !important; height: 3.8rem;
        border: none !important;
    }
    .stButton>button:hover { background-color: #FFFFFF !important; color: #000000 !important; }

    .agent-card { 
        border: 2px solid #00FF41; padding: 20px; background: #111; 
        border-radius: 12px; margin-bottom: 15px; 
    }
    .agent-card b { color: #00FF41; font-size: 1.6rem; }
    
    label { color: #00FF41 !important; font-size: 1.4rem !important; font-weight: bold !important; }
    input, textarea, select { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border: 2px solid #00FF41 !important; font-size: 1.2rem !important;
    }

    .stTabs [data-baseweb="tab"] { color: #00FF41 !important; border: 1px solid #00FF41 !important; font-size: 1.2rem !important; }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !important; color: #00
