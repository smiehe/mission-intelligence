import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# 1. Basis-Konfiguration
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- VERBINDUNG ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_fresh_data(ws_name):
    """Lädt Daten und erzwingt eine saubere Struktur."""
    st.cache_data.clear() 
    try:
        # Wir lesen das Blatt
        df = conn.read(worksheet=ws_name, ttl=0)
        
        # Falls das Blatt komplett leer ist oder Fehler wirft, leeres Gerüst bauen
        if df is None or df.empty:
            if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
            if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
        
        # WICHTIG: Sicherstellen, dass keine "Unnamed" Spalten drin sind
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df.dropna(how="all")
    except Exception:
        if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
        if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
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

# --- DESIGN ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .splash-box { text-align: center; margin-top: 10%; padding: 50px; border: 4px solid #00FF41; background-color: #050505; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 3px solid #00FF41; }
    .timer-display { font-family: 'Courier New', monospace; color: #00FF41; font-size: 3rem; text-align: center; border: 2px solid #00FF41; padding: 10px; }
    .mission-header { width: 100%; background: #00FF41; color: #000; padding: 10px; text-align: center; font-weight: bold; margin-top: -65px; }
    .stButton>button { background-color: #00FF41 !important; color: #000 !important; font-weight: bold !important; width: 100%; }
    .agent-card { border: 1px solid #00FF41; padding: 15px; margin-bottom: 10px; background: #111; }
</style>
""", unsafe_allow_html=True)

# --- APP LOGIK ---
if not st.session_state.access_granted:
    st.markdown('<div class="splash-box"><h1 style="color:#00FF41;">MISSION: INTELLIGENCE</h1><p>PCS DIVISION | Q1 2026</p></div>', unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1,1,1])
    with col_mid:
        if st.button("ENTER HQ"):
            st.session_state.access_granted = True
            st.rerun()
else:
    st.markdown('<div class="mission-header">HQ STATUS: ACTIVE</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### ⏳ MISSION CLOCK")
        m_info = MISSION_DATA[st.session_state.active_mission_key]
        rem = max(0, (m_info['duration'] * 60) - (time.time() - st.session_state.mission_start_time))
        mins, secs = divmod(int(rem), 60)
        st.markdown(f'<div class="timer-display">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        st.write("")
        for k, d in MISSION_DATA.items():
            if st.button(f"{k} | {d['name']}", key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()
        if st.button("🔄 REFRESH SYSTEM"): st.rerun()

    t1, t2, t3 = st.tabs(["👤 PROFILE", "📂 SABOTAGE", "💰 COINS"])

    with t1:
        st.header("Agenten-Profile")
        with st.form("p_form"):
            a_name = st.selectbox("Name:", AGENT_LIST)
            c_name = st.text_input("Codename:")
            a_skill = st.text_input("Skill:")
            if st.form_submit_button("SPEICHERN"):
                # 1. Frische Daten laden
                df = get_fresh_data("Profiles")
                # 2. Neuen Eintrag anhängen
                new_row = pd.DataFrame([{"Agent": a_name, "Codename": c_name, "Skill": a_skill}])
                # 3. WICHTIG: Wenn der Agent schon existiert, wird er ersetzt, sonst angehängt
                df = df[df["Agent"] != a_name] 
                updated_df = pd.concat([df, new_row], ignore_index=True)
                # 4. Hochladen
                conn.update(worksheet="Profiles", data=updated_df)
                st.success("Profil übertragen!")
                time.sleep(1)
                st.rerun()

        st.subheader("Aktive Agenten")
        p_df = get_fresh_data("Profiles")
        for _, r in p_df.iterrows():
            st.markdown(f'<div class="agent-card"><b>{r["Agent"]}</b> | Code: {r["Codename"]} | Skill: {r["Skill"]}</div>', unsafe_allow_html=True)

    with t2:
        st.header("Sabotage-Akte")
        with st.form("s_form"):
            s_thema = st.text_input("Thema:")
            s_details = st.text_area("Details:")
            if st.form_submit_button("AKTE SPEICHERN"):
                # 1. Frische Daten laden
                df = get_fresh_data("Sabotage")
                # 2. Neuen Eintrag anhängen
                new_row = pd.DataFrame([{"Thema": s_thema, "Details": s_details}])
                # 3. Anhängen ohne Altes zu löschen
                updated_df = pd.concat([df, new_row], ignore_index=True).drop_duplicates()
                # 4. Hochladen
                conn.update(worksheet="Sabotage", data=updated_df)
                st.success("Sabotage registriert!")
                time.sleep(1)
                st.rerun()

        st.subheader("Archivierte Akten")
        s_df = get_fresh_data("Sabotage")
        for _, r in s_df.iterrows():
            with st.expander(f"🔎 {r['Thema']}"):
                st.write(r["Details"])

    with t3:
        st.header("Coin-Investment")
        s_df_coins = get_fresh_data("Sabotage")
        if s_df_coins.empty:
            st.info("Warten auf Sabotage-Themen...")
        else:
            voter = st.selectbox("Wer votet?", AGENT_LIST, key="v_sel")
            total = 0
            for item in s_df_coins["Thema"].unique():
                val = st.slider(f"Invest in {item}:", 0, 100, 0, key=f"sl_{voter}_{item}")
                total += val
            st.write(f"Gesamt: {total}/100")
            if total == 100:
                if st.button("VOTE ABSCHLIESSEN"):
                    st.balloons()
