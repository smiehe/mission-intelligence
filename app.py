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
        # ttl="0" erzwingt das Laden frischer Daten ohne Cache
        return conn.read(worksheet=worksheet_name, ttl="0")
    except Exception:
        if worksheet_name == "Profiles":
            return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
        if worksheet_name == "Sabotage":
            return pd.DataFrame(columns=["Thema", "Details"])
        if worksheet_name == "Votes":
            return pd.DataFrame(columns=["Voter"])
        return pd.DataFrame()

# --- INITIALISIERUNG ---
AGENT_LIST = ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"]

MISSION_DATA = {
    "09:00": {"name": "Operation: Agent Profile", "duration": 30},
    "09:30": {"name": "The Intelligence Briefing (Nico)", "duration": 90},
    "11:15": {"name": "The Deep-Dive Mission", "duration": 90},
    "12:45": {"name": "Field Rations (Lunch)", "duration": 60},
    "13:45": {"name": "Final Briefing (Wrap-up)", "duration": 30},
    "15:30": {"name": "Field Operation (Museum)", "duration": 120},
    "17:30": {"name": "Safe House Drinks & Dinner", "duration": 180}
}

if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state:
    st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state:
    st.session_state.mission_start_time = time.time()

# --- DESIGN & CSS ---
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
        padding: 10px; border: 2px solid #00FF41;
        background: rgba(0, 255, 65, 0.1); margin-bottom: 5px;
    }
    .agent-card {
        border: 1px solid #00FF41; padding: 12px; border-radius: 5px; 
        margin-bottom: 10px; background: rgba(0, 255, 65, 0.05);
    }
    .stButton>button { 
        background-color: #000000 !important; color: #00FF41 !important; 
        border: 1px solid #00FF41 !important; width: 100%; text-align: left !important;
    }
    .stButton>button:hover { border: 1px solid #FFFFFF !important; color: #FFFFFF !important; }
    .stTabs [data-baseweb="tab"] { color: #00FF41; border: 1px solid #00FF41; }
    input, textarea, select { background-color: #111 !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; }
    </style>
    """, unsafe_allow_html=True)

# Automatischer Refresh für den Timer
if st.session_state.access_granted:
    st_autorefresh(interval=1000, key="timer_refresh")

# --- LOGIK: STARTBILDSCHIRM ---
if not st.session_state.access_granted:
    st.markdown('<div class="splash-container"><h1>MISSION:<br>INTELLIGENCE</h1><p>> PCS DIVISION | Q1 2026</p></div>', unsafe_allow_html=True)
    _, col2, _ = st.columns([1,1,1])
    with col2:
        if st.button("ENTER HQ / MISSION STARTEN"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # --- SIDEBAR: TIMER & AGENDA ---
    st.sidebar.markdown("### ⏳ MISSION CLOCK")
    m_info = MISSION_DATA[st.session_state.active_mission_key]
    elapsed = time.time() - st.session_state.mission_start_time
    remaining = max(0, (m_info['duration'] * 60) - elapsed)
    mins, secs = divmod(int(remaining), 60)
    timer_col = "#00FF41" if remaining > 300 else "#FF0000"
    st.sidebar.markdown(f'<div class="timer-box" style="color:{timer_col}; border-color:{timer_col};">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.header("📍 EINSATZPLAN")
    for t_key, data in MISSION_DATA.items():
        label = f"{t_key} | {data['name']}"
        if t_key == st.session_state.active_mission_key: label = f"▶ {label}"
        if st.sidebar.button(label, key=f"btn_{t_key}"):
            st.session_state.active_mission_key = t_key
            st.session_state.mission_start_time = time.time()
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info("Team: Sören, Laura, Tamara, Janina, Christin, Leo, Claudine")

    # --- HAUPTBEREICH: TABS ---
    st.title(f"🕵️‍♂️ HQ: {m_info['name']}")
    tab1, tab2, tab3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with tab1:
        st.header("Operation: Agent Profile")
        with st.form("p_form"):
            name = st.selectbox("PCS Agent:", AGENT_LIST)
            codename = st.text_input("KI-Codename:")
            skill = st.text_input("KI-Skill:")
            if st.form_submit_button("PROFIL SPEICHERN"):
                if codename and skill:
                    new_p = pd.DataFrame([{"Agent": name, "Codename": codename, "Skill": skill}])
                    old_p = safe_read("Profiles")
                    updated_p = pd.concat([old_p, new_p], ignore_index=True)
                    conn.update(worksheet="Profiles", data=updated_p)
                    st.success("Profil im Zentralspeicher.")
                    time.sleep(1)
                    st.rerun()

        st.subheader("Aktive Agenten im Netzwerk")
        p_df = safe_read("Profiles").dropna(subset=["Agent"])
        if not p_df.empty:
            cols = st.columns(2)
            for i, row in p_df.iterrows():
                with cols[i % 2]:
                    st.markdown(f'<div class="agent-card"><b>{row["Agent"]}</b><br>Code: {row["Codename"]}<br>Skill: {row["Skill"]}</div>', unsafe_allow_html=True)

    with tab2:
        st.header("Die Sabotage-Akte")
        with st.form("s_form"):
            t_name = st.text_input("Thema:")
            details = st.text_area("Details:")
            if st.form_submit_button("AKTE AN NICO SENDEN"):
                if t_name:
                    new_s = pd.DataFrame([{"Thema": t_name, "Details": details}])
                    old_s = safe_read("Sabotage")
                    updated_s = pd.concat([old_s, new_s], ignore_index=True)
                    conn.update(worksheet="Sabotage", data=updated_s)
                    st.success(f"'{t_name}' registriert.")
                    time.sleep(1)
                    st.rerun()

    with tab3:
        st.header("💰 Operation: Golden Coin")
        s_df = safe_read("Sabotage").dropna(subset=["Thema"])
        if s_df.empty:
            st.warning("Warte auf Sabotage-Akten...")
        else:
            voter = st.selectbox("Agent für Voting:", AGENT_LIST, key="v_sel")
            themen = s_df["Thema"].unique()
            total = 0
            votes = {}
            for item in themen:
                # Wir nutzen einen eindeutigen Key pro Voter und Thema
                votes[item] = st.slider(f"Investment: {item}", 0, 100, 0, key=f"sl_{voter}_{item}")
                total += votes[item]
            
            st.markdown(f"### Gesamt {voter}: `{total} / 100` Coins")
            if total == 100:
                if st.button(f"VOTING FÜR {voter} FINALISIEREN"):
                    v_row = {"Voter": voter}
                    v_row.update(votes)
                    v_df = pd.DataFrame([v_row])
                    old_v = safe_read("Votes")
                    updated_v = pd.concat([old_v, v_df], ignore_index=True)
                    conn.update(worksheet="Votes", data=updated_v)
                    st.balloons()
            elif total > 100:
                st.error(f"Budget überschritten! (-{total-100})")
