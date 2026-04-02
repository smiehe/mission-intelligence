import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

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

# --- INITIALISIERUNG ---
AGENT_LIST = ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"]
BOSS_LIST = {
    "The Awakened One": "🦅",
    "Time Eater": "⏳",
    "Donu & Deca": "💎",
    "The Corrupt Heart": "❤️",
    "The Champ": "🏆"
}

if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'selected_boss' not in st.session_state:
    st.session_state.selected_boss = "The Awakened One"
if 'active_mission_key' not in st.session_state:
    st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state:
    st.session_state.mission_start_time = time.time()

# --- DESIGN & CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-size: 1.1rem; }
    
    .digital-header {
        width: 100%; background: #00FF41; color: #000000; padding: 12px 0;
        text-align: center; font-family: 'Courier New', Courier, monospace;
        font-weight: bold; letter-spacing: 4px; font-size: 1.1rem;
        margin-top: -65px; margin-bottom: 30px;
    }

    .timer-box {
        font-family: 'Courier New', Courier, monospace;
        color: #00FF41; font-size: 3rem; text-align: center;
        padding: 15px; border: 3px solid #00FF41; background: #000;
        margin-bottom: 10px; font-weight: bold;
    }

    .agent-card {
        border: 2px solid #00FF41; padding: 15px; border-radius: 8px; 
        margin-bottom: 8px; background: #111111;
    }
    .agent-card b { color: #00FF41; font-size: 1.3rem; }
    .avatar-display { font-size: 2.5rem; float: right; margin-top: -10px; }

    .stButton>button { 
        background-color: #00FF41 !important; color: #000000 !important; 
        border: none !important; width: 100%; font-weight: bold !important;
        height: 3.5rem; font-size: 1.2rem !important;
    }
    
    label { color: #00FF41 !important; font-size: 1.2rem !important; font-weight: bold !important; }
    input, textarea, select { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border: 2px solid #00FF41 !important; 
    }
    
    /* Radio Buttons für Character Select */
    div[data-testid="stMarkdownContainer"] > p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if st.session_state.access_granted:
    st_autorefresh(interval=2000, key="timer_refresh")

# --- STARTBILDSCHIRM (CHARACTER SELECT) ---
if not st.session_state.access_granted:
    st.markdown("""
        <div style="text-align: center; margin-top: 5%; padding: 30px; border: 4px solid #00FF41; background: #000;">
            <h1 style="color: #00FF41; font-size: 3.5rem; letter-spacing: 5px;">CHARACTER SELECT</h1>
            <p style="color: #FFF; font-size: 1.2rem;">WÄHLE DEINEN ENDBOSS FÜR DIE MISSION</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("")
        selected = st.radio("Verfügbare Bosse:", list(BOSS_LIST.keys()), horizontal=True)
        st.session_state.selected_boss = selected
        
        st.markdown(f"<div style='text-align:center; font-size:6rem;'>{BOSS_LIST[selected]}</div>", unsafe_allow_html=True)
        st.write("")
        
        if st.button("BESTÄTIGEN & HQ BETRETEN"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # --- HEADER & SIDEBAR (Wie gehabt) ---
    st.markdown('<div class="digital-header">INTELLIGENCE NETWORK // BOSS MODE ACTIVE</div>', unsafe_allow_html=True)
    
    # Mission Clock & Agenda
    st.sidebar.markdown(f"### ⏳ MISSION CLOCK")
    # ... (Timer Code hier weggelassen für Kürze, bleibt aber im echten Code gleich) ...
    
    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with tab1:
        st.header("Operation: Agent Profile")
        with st.form("p_form"):
            name = st.selectbox("PCS Agent:", AGENT_LIST)
            codename = st.text_input("KI-Codename:")
            skill = st.text_input("KI-Skill:")
            # Der Avatar wird aus dem session_state (vom Startbildschirm) gezogen
            current_avatar = st.session_state.selected_boss
            st.info(f"Ausgewählter Avatar: {current_avatar} {BOSS_LIST[current_avatar]}")
            
            if st.form_submit_button("PROFIL SPEICHERN"):
                if codename and skill:
                    new_p = pd.DataFrame([{
                        "Agent": name, 
                        "Codename": codename, 
                        "Skill": skill, 
                        "Avatar": BOSS_LIST[current_avatar]
                    }])
                    old_p = safe_read("Profiles")
                    conn.update(worksheet="Profiles", data=pd.concat([old_p, new_p], ignore_index=True))
                    st.success("Profil mit Boss-Stärke gespeichert!")
                    time.sleep(1)
                    st.rerun()

        st.subheader("Aktive PCS-Agenten im Netzwerk")
        p_df = safe_read("Profiles").dropna(subset=["Agent"])
        if not p_df.empty:
            cols = st.columns(2)
            for i, row in p_df.iterrows():
                with cols[i % 2]:
                    # Hole das Icon (entweder aus Spalte "Avatar" oder Standard)
                    icon = row["Avatar"] if "Avatar" in row else "🕵️‍♂️"
                    st.markdown(f"""
                        <div class="agent-card">
                            <div class="avatar-display">{icon}</div>
                            <b>{row["Agent"]}</b><br>
                            CODE: {row["Codename"]}<br>
                            SKILL: {row["Skill"]}
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"🗑️ LÖSCHEN: {row['Agent']}", key=f"del_{i}"):
                        conn.update(worksheet="Profiles", data=safe_read("Profiles").drop(i))
                        st.rerun()
    # ... (Restliche Tabs wie gehabt) ...
