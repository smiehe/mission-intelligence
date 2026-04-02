import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Autorefresh für den flüssigen Timer
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# 1. Basis-Konfiguration
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- VERBINDUNG ZUM ZENTRALSPEICHER ---
conn = st.connection("gsheets", type=GSheetsConnection)

# OPTIMIERTE DATEN-ABFRAGE
@st.cache_data(ttl=10) # Merkt sich Daten für 10 Sekunden, um den Timer nicht zu bremsen
def get_cached_data(ws_name):
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        return df.dropna(how="all")
    except:
        if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
        if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
        return pd.DataFrame()

def force_reload():
    """Löscht den Cache komplett für einen harten Refresh."""
    st.cache_data.clear()
    st.rerun()

# --- KONFIGURATION ---
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

# --- SESSION STATE ---
if 'access_granted' not in st.session_state: st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state: st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state: st.session_state.mission_start_time = time.time()

# --- DESIGN & CSS ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #FFFFFF; font-size: 1.2rem; }
    .splash-box { text-align: center; margin-top: 10%; padding: 60px; border: 4px solid #00FF41; background-color: #050505; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 3px solid #00FF41; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; font-size: 1.2rem !important; }
    .timer-display { font-family: 'Courier New', monospace; color: #00FF41; font-size: 3.5rem; text-align: center; border: 3px solid #00FF41; padding: 15px; font-weight: bold; }
    .mission-header { width: 100%; background: #00FF41; color: #000; padding: 15px 0; text-align: center; font-weight: bold; margin-top: -70px; margin-bottom: 30px; font-size: 1.3rem; }
    .stButton>button { background-color: #00FF41 !important; color: #000 !important; font-weight: bold !important; height: 3.5rem; }
    .agent-card { border: 1px solid #00FF41; padding: 15px; background: #111; border-radius: 8px; margin-bottom: 5px; }
    .stTabs [data-baseweb="tab"] { color: #00FF41 !important; border: 1px solid #00FF41 !important; }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !important; color: #000 !important; }
</style>
""", unsafe_allow_html=True)

# --- APP LOGIK ---
if not st.session_state.access_granted:
    st.markdown('<div class="splash-box"><h1 style="color:#00FF41; font-size:4rem;">MISSION: INTELLIGENCE</h1><p>QUARTERDAY 2026</p></div>', unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1,2,1])
    with col_mid:
        if st.button("ENTER HQ"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # AUTO-REFRESH (Nur für die Uhr!)
    if st_autorefresh:
        st_autorefresh(interval=1000, key="timer_tick")

    st.markdown('<div class="mission-header">NETWORK ACCESS GRANTED // STATUS: ACTIVE</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⏳ MISSION CLOCK")
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        elapsed = time.time() - st.session_state.mission_start_time
        rem_sec = max(0, (active_info['duration'] * 60) - elapsed)
        m, s = divmod(int(rem_sec), 60)
        st.markdown(f'<div class="timer-display">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("📍 EINSATZPLAN")
        for k, d in MISSION_DATA.items():
            if st.sidebar.button(f"{k} | {d['name']}", key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()
        
        st.markdown("---")
        if st.button("🔄 REFRESH ALL DATA"):
            force_reload()

    t1, t2, t3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with t1:
        st.header("Agenten-Profile")
        with st.form("p_form"):
            a_name = st.selectbox("Wer bist du?", AGENT_LIST)
            c_name = st.text_input("Codename:")
            a_skill = st.text_input("Spezialfähigkeit:")
            if st.form_submit_button("PROFIL SPEICHERN"):
                # Hier erzwingen wir frische Daten vor dem Speichern
                df_p = get_cached_data("Profiles")
                new_p = pd.DataFrame([{"Agent": a_name, "Codename": c_name, "Skill": a_skill}])
                updated_p = pd.concat([df_p[df_p["Agent"] != a_name], new_p], ignore_index=True)
                conn.update(worksheet="Profiles", data=updated_p)
                st.success("Gespeichert!")
                force_reload()

        st.subheader("Aktive Agenten")
        p_list = get_cached_data("Profiles")
        for idx, r in p_list.iterrows():
            col_a, col_b = st.columns([0.85, 0.15])
            with col_a:
                st.markdown(f'<div class="agent-card"><b>{r["Agent"]}</b> | {r["Codename"]} | {r["Skill"]}</div>', unsafe_allow_html=True)
            with col_b:
                if st.button("🗑️", key=f"del_p_{idx}"):
                    df_cleaned = p_list[p_list["Agent"] != r["Agent"]]
                    conn.update(worksheet="Profiles", data=df_cleaned)
                    force_reload()

    with t2:
        st.header("Die Sabotage-Akte")
        with st.form("s_form"):
            s_thema = st.text_input("Thema:")
            s_details = st.text_area("Details:")
            if st.form_submit_button("AKTE SPEICHERN"):
                df_s = get_cached_data("Sabotage")
                new_s = pd.DataFrame([{"Thema": s_thema, "Details": s_details}])
                updated_s = pd.concat([df_s, new_s], ignore_index=True).drop_duplicates(subset=["Thema"])
                conn.update(worksheet="Sabotage", data=updated_s)
                st.success("Archiviert.")
                force_reload()
        
        s_list = get_cached_data("Sabotage")
        for idx, r in s_list.iterrows():
            with st.expander(f"🔎 {r['Thema']}"):
                st.write(r["Details"])

    with t3:
        st.header("💰 Operation: Golden Coin")
        df_coins = get_cached_data("Sabotage")
        if df_coins.empty:
            st.info("Warten auf Sabotage-Themen...")
        else:
            voter = st.selectbox("Wer investiert?", AGENT_LIST, key="v_sel")
            spent = 0
            for item in df_coins["Thema"].unique():
                spent += st.slider(f"INVEST: {item}", 0, 100, 0, key=f"c_{voter}_{item}")
            st.markdown(f"### Gesamt: `{spent} / 100` Coins")
            if spent == 100:
                if st.button("INVESTITION FINALISIEREN"):
                    st.balloons()
