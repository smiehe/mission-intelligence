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
        # ttl=0 ist extrem wichtig, damit er nicht alte (gelöschte) Daten aus dem Cache anzeigt
        return conn.read(worksheet=ws_name, ttl=0)
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

# 4. Session State
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state:
    st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state:
    st.session_state.mission_start_time = time.time()
if 'selected_boss' not in st.session_state:
    st.session_state.selected_boss = "The Awakened One"

# 5. CSS (High Contrast)
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #FFFFFF; font-size: 1.2rem; }
    .splash-box { text-align: center; margin-top: 5%; padding: 50px; border: 4px solid #00FF41; background-color: #050505; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 3px solid #00FF41; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; font-size: 1.1rem !important; opacity: 1 !important; }
    .timer-display { font-family: 'Courier New', monospace; color: #00FF41; font-size: 3rem; text-align: center; padding: 10px; border: 2px solid #00FF41; }
    .mission-header { width: 100%; background: #00FF41; color: #000000; padding: 10px 0; text-align: center; font-weight: bold; margin-top: -65px; margin-bottom: 20px; }
    .stButton>button { background-color: #00FF41 !important; color: #000000 !important; font-weight: bold !important; height: 3.5rem; }
    .agent-card { border: 2px solid #00FF41; padding: 15px; background: #111; border-radius: 10px; margin-bottom: 10px; }
    label { color: #00FF41 !important; font-size: 1.3rem !important; }
    input, textarea, select { background-color: #000 !important; color: #FFF !important; border: 2px solid #00FF41 !important; }
</style>
""", unsafe_allow_html=True)

if st.session_state.access_granted and st_autorefresh:
    st_autorefresh(interval=3000, key="global_tick")

# 7. Start / Login
if not st.session_state.access_granted:
    st.markdown('<div class="splash-box"><h1 style="color:#00FF41; font-size:4rem;">MISSION:<br>INTELLIGENCE</h1><p style="color:#FFF;">PCS DIVISION | Q1 2026</p></div>', unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1,2,1])
    with col_mid:
        st.write("")
        st.session_state.selected_boss = st.radio("Wähle deinen Avatar:", list(BOSS_LIST.keys()), horizontal=True)
        st.markdown(f"<div style='text-align:center; font-size:7rem;'>{BOSS_LIST[st.session_state.selected_boss]}</div>", unsafe_allow_html=True)
        if st.button("ENTER HQ"):
            st.session_state.access_granted = True
            st.rerun()

# 8. HQ Bereich
else:
    st.markdown('<div class="mission-header">NETWORK: ACTIVE // BOSS MODE ACTIVE</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⏳ MISSION CLOCK")
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        rem_sec = max(0, (active_info['duration'] * 60) - (time.time() - st.session_state.mission_start_time))
        m, s = divmod(int(rem_sec), 60)
        st.markdown(f'<div class="timer-display">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        st.markdown("---")
        for k, d in MISSION_DATA.items():
            if st.button(f"{k} | {d['name']}", key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()

    t1, t2, t3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with t1:
        st.header("Operation: Agent Profile")
        with st.form("p_form"):
            a_name = st.selectbox("Identität:", AGENT_LIST)
            c_name = st.text_input("Codename:")
            a_skill = st.text_input("Spezialfähigkeit:")
            if st.form_submit_button("PROFIL SPEICHERN"):
                new_entry = pd.DataFrame([{"Agent": a_name, "Codename": c_name, "Skill": a_skill, "Avatar": BOSS_LIST[st.session_state.selected_boss]}])
                conn.update(worksheet="Profiles", data=pd.concat([safe_read("Profiles"), new_entry], ignore_index=True))
                st.success("Gespeichert!")
                time.sleep(1)
                st.rerun()

        st.subheader("Aktive Agenten")
        df_p = safe_read("Profiles").dropna(subset=["Agent"])
        if not df_p.empty:
            c_grid = st.columns(2)
            for idx, r in df_p.iterrows():
                with c_grid[idx % 2]:
                    st.markdown(f'<div class="agent-card"><div style="font-size:3rem; float:right;">{r["Avatar"]}</div><b>{r["Agent"]}</b><br>CODE: {r["Codename"]}<br>SKILL: {r["Skill"]}</div>', unsafe_allow_html=True)
                    # VERBESSERTE LÖSCH-LOGIK
                    if st.button(f"🗑️ LÖSCHEN: {r['Agent']}", key=f"del_{idx}_{r['Agent']}"):
                        # 1. Aktuelle Daten laden
                        current_df = safe_read("Profiles")
                        # 2. Genau diesen Agenten rausfiltern (nicht über Index, sondern Name + Codename)
                        updated_df = current_df[current_df["Agent"] != r["Agent"]]
                        # 3. Das Sheet komplett überschreiben
                        conn.update(worksheet="Profiles", data=updated_df)
                        st.warning(f"Profil {r['Agent']} gelöscht. Synchronisiere...")
                        time.sleep(1)
                        st.rerun()

    with t2:
        st.header("Die Sabotage-Akte")
        with st.form("s_form"):
            s_thema = st.text_input("Sabotage-Thema:")
            if st.form_submit_button("SENDEN"):
                new_s = pd.DataFrame([{"Thema": s_thema}])
                conn.update(worksheet="Sabotage", data=pd.concat([safe_read("Sabotage"), new_s], ignore_index=True))
                st.rerun()

    with t3:
        st.header("💰 Operation: Golden Coin")
        df_s = safe_read("Sabotage").dropna(subset=["Thema"])
        if not df_s.empty:
            v_agent = st.selectbox("Wer investiert?", AGENT_LIST, key="v_sel")
            for item in df_s["Thema"].unique():
                st.slider(f"INVEST: {item}", 0, 100, 0, key=f"sl_{v_agent}_{item}")
