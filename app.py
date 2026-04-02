import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time

# Seiteneinstellungen
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- KONFIGURATION DER MISSIONEN (Uhrzeit, Name, Dauer in Minuten) ---
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
    /* Agenda Styling */
    .stButton>button {
        background-color: #000000 !important; color: #00FF41 !important;
        border: 1px solid #00FF41 !important; width: 100%; text-align: left !important;
        font-family: 'Courier New', Courier, monospace; margin-bottom: -5px;
    }
    .stButton>button:hover { border: 1px solid #FFFFFF !important; color: #FFFFFF !important; }
    
    .stTabs [data-baseweb="tab"] { color: #00FF41; border:
