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

# --- VERBINDUNG ZUM ZENTRALSPEICHER ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_fresh_data(ws_name):
    """Erzwingt das Laden absolut frischer Daten ohne Zwischenspeicher."""
    st.cache_data.clear() 
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        # Falls das Sheet existiert aber leer ist, Spalten sicherstellen
        if df.empty:
            if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
            if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema"])
        return df.dropna(how="all")
    except Exception:
        if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
        if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema"])
        return pd.DataFrame()

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
    [data-testid="stSidebar"] * { color: #FFFFFF !important; font-size: 1.2rem !important; opacity: 1 !important; }
    .timer-display { font-family: 'Courier New', monospace; color: #00FF41; font-size: 3.5rem; text-align: center; padding: 15px; border: 3px solid #00FF41; font-weight: bold; }
    .mission-header { width: 100%; background: #00FF41; color: #000; padding: 15px 0; text-align: center; font-weight: bold; margin-top: -70px; margin-bottom: 30px; font-size: 1.3rem; }
    .stButton>button { background-color: #00FF41 !important; color: #000 !important; font-weight: bold !important; height: 4rem; }
    .agent-card { border: 2px solid #00FF41; padding: 20px; background: #111; border-radius: 12px; margin-bottom: 15px; }
    label { color: #00FF41 !important; font-size: 1.4rem !important; font-weight: bold !important; }
    input, textarea, select { background-color: #000 !important; color: #FFF !important; border: 2px solid #00FF41 !important; font-size: 1.2rem !important; }
    .stTabs [data-baseweb="tab"] { color: #00FF41 !important; border: 1px solid #00FF41 !important; }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !important; color: #000 !important; }
</style>
""", unsafe_allow_html=True)

# --- STARTBILDSCHIRM ---
if not st.session_state.access_granted:
    st.markdown('<div class="splash-box"><h1 style="color:#00FF41; font-size:5rem;">MISSION:<br>INTELLIGENCE</h1><p style="color:#FFF; font-size:1.8rem;">PCS DIVISION | QUARTERDAY Q1 2026</p></div>', unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1,1,1])
    with col_mid:
        if st.button("ENTER HQ / MISSION STARTEN"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # Auto-Refresh (Timer läuft im Hintergrund)
    if st_autorefresh:
        st_autorefresh(interval=2000, key="timer_tick")

    # --- HQ BEREICH ---
    st.markdown('<div class="mission-header">NETWORK ACCESS GRANTED // PCS HQ BERLIN // STATUS: ACTIVE</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⏳ MISSION CLOCK")
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        elapsed = time.time() - st.session_state.mission_start_time
        rem_sec = max(0, (active_info['duration'] * 60) - elapsed)
        m, s = divmod(int(rem_sec), 60)
        st.markdown(f'<div class="timer-display">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        st.markdown("---")
        for k, d in MISSION_DATA.items():
            lbl = f"{k} | {d['name']}"
            if k == st.session_state.active_mission_key: lbl = f"▶ {lbl}"
            if st.sidebar.button(lbl, key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()
        st.markdown("---")
        if st.button("🔄 REFRESH DATA"): st.rerun()

    t1, t2, t3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with t1:
        st.header("Operation: Agent Profile")
        with st.form("p_form", clear_on_submit=True):
            a_name = st.selectbox("Wer bist du?", AGENT_LIST)
            c_name = st.text_input("Dein KI-Codename:")
            a_skill = st.text_input("Deine KI-Spezialfähigkeit:")
            if st.form_submit_button("PROFIL GLOBAL SPEICHERN"):
                with st.spinner("Synchronisiere..."):
                    current_df = get_fresh_data("Profiles")
                    new_entry = pd.DataFrame([{"Agent": a_name, "Codename": c_name, "Skill": a_skill}])
                    updated_df = pd.concat([current_df, new_entry], ignore_index=True).drop_duplicates(subset=["Agent"], keep="last")
                    conn.update(worksheet="Profiles", data=updated_df)
                    st.success("Profil gesichert.")
                    time.sleep(1)
                    st.rerun()

        st.subheader("Aktive PCS-Agenten")
        p_df = get_fresh_data("Profiles")
        if not p_df.empty:
            c_grid = st.columns(2)
            for idx, r in p_df.iterrows():
                with c_grid[idx % 2]:
                    st.markdown(f'<div class="agent-card"><b>{r["Agent"]}</b><br>CODE: {r["Codename"]}<br>SKILL: {r["Skill"]}</div>', unsafe_allow_html=True)
                    if st.button(f"🗑️ LÖSCHEN: {r['Agent']}", key=f"del_{idx}"):
                        df_to_clean = get_fresh_data("Profiles")
                        df_cleaned = df_to_clean[df_to_clean["Agent"] != r["Agent"]]
                        conn.update(worksheet="Profiles", data=df_cleaned)
                        st.rerun()

    with t2:
        st.header("Die Sabotage-Akte")
        with st.form("s_form", clear_on_submit=True):
            s_thema = st.text_input("Welcher Prozess sabotiert uns?")
            if st.form_submit_button("AN NICO ÜBERMITTELN"):
                if s_thema:
                    with st.spinner("Übertrage..."):
                        current_s = get_fresh_data("Sabotage")
                        new_s = pd.DataFrame([{"Thema": s_thema}])
                        updated_s = pd.concat([current_s, new_s], ignore_index=True).drop_duplicates()
                        conn.update(worksheet="Sabotage", data=updated_s)
                        st.success(f"'{s_thema}' archiviert.")
                        time.sleep(1)
                        st.rerun()

        # LISTE DER AKTUELLEN SABOTAGEAKTE (Damit ihr seht, was da ist!)
        st.subheader("Bisher identifizierte Sabotage-Themen")
        current_sabotage_list = get_fresh_data("Sabotage")
        if not current_sabotage_list.empty:
            for item in current_sabotage_list["Thema"].unique():
                st.markdown(f"• **{item}**")

    with t3:
        st.header("💰 Operation: Golden Coin")
        df_s_vote = get_fresh_data("Sabotage")
        if df_s_vote.empty:
            st.info("Warten auf Sabotage-Themen aus Tab 2...")
        else:
            v_agent = st.selectbox("Identität für Investment:", AGENT_LIST, key="v_sel")
            t_spent = 0
            v_dict = {}
            # Hier laden wir dynamisch alle Themen, die in Tab 2 eingetragen wurden
            for item in df_s_vote["Thema"].unique():
                if pd.notna(item):
                    v_dict[item] = st.slider(f"INVEST: {item}", 0, 100, 0, key=f"sl_{v_agent}_{item}")
                    t_spent += v_dict[item]
            
            st.markdown(f"## Status {v_agent}: {t_spent} / 100 Coins")
            if t_spent == 100:
                if st.button(f"INVESTITION FÜR {v_agent} FINALISIEREN"):
                    st.balloons()
                    st.success("Investment übertragen!")
