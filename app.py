import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Basis-Konfiguration
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- VERBINDUNG ZUM ZENTRALSPEICHER ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_fresh_data(ws_name):
    """Erzwingt das Laden frischer Daten vom Google Server."""
    st.cache_data.clear() 
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        if df is None or df.empty:
            if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
            if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
            if ws_name == "Votes": return pd.DataFrame(columns=["Voter", "Total"])
        return df.loc[:, ~df.columns.str.contains('^Unnamed')].dropna(how="all")
    except Exception:
        if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
        if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
        if ws_name == "Votes": return pd.DataFrame(columns=["Voter", "Total"])
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
    .splash-box { text-align: center; margin-top: 10%; padding: 50px; border: 4px solid #00FF41; background-color: #050505; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 3px solid #00FF41; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; font-size: 1.2rem !important; }
    .timer-display { font-family: 'Courier New', monospace; color: #00FF41; font-size: 3.5rem; text-align: center; border: 3px solid #00FF41; padding: 15px; font-weight: bold; }
    .mission-header { width: 100%; background: #00FF41; color: #000; padding: 15px 0; text-align: center; font-weight: bold; margin-top: -70px; margin-bottom: 30px; font-size: 1.3rem; }
    .stButton>button { background-color: #00FF41 !important; color: #000 !important; font-weight: bold !important; height: 3.8rem; border: none !important; }
    .agent-card { border: 2px solid #00FF41; padding: 20px; background: #111; border-radius: 12px; margin-bottom: 15px; }
    label { color: #00FF41 !important; font-size: 1.3rem !important; font-weight: bold !important; }
    input, textarea, select { background-color: #000 !important; color: #FFF !important; border: 2px solid #00FF41 !important; }
    .stTabs [data-baseweb="tab"] { color: #00FF41 !important; border: 1px solid #00FF41 !important; padding: 10px 20px !important; }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !important; color: #000 !important; }
</style>
""", unsafe_allow_html=True)

# --- APP LOGIK ---
if not st.session_state.access_granted:
    st.markdown('<div class="splash-box"><h1 style="color:#00FF41; font-size:4rem;">MISSION: INTELLIGENCE</h1><p style="color:#FFF;">PCS DIVISION | QUARTERDAY 2026</p></div>', unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1,1,1])
    with col_mid:
        if st.button("ENTER HQ"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    st.markdown('<div class="mission-header">NETWORK ACCESS GRANTED // STATUS: ACTIVE</div>', unsafe_allow_html=True)

    # SIDEBAR: TIMER & AGENDA
    with st.sidebar:
        st.markdown("### ⏳ MISSION CLOCK")
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        rem_sec = max(0, (active_info['duration'] * 60) - (time.time() - st.session_state.mission_start_time))
        m, s = divmod(int(rem_sec), 60)
        st.markdown(f'<div class="timer-display">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        st.write("")
        for k, d in MISSION_DATA.items():
            if st.sidebar.button(f"{k} | {d['name']}", key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()
        st.markdown("---")
        if st.button("🔄 REFRESH SYSTEM"): st.rerun()

    t1, t2, t3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    # TAB 1: PROFILE
    with t1:
        st.header("Operation: Agent Profile")
        with st.form("p_form"):
            a_name = st.selectbox("Agent Identität:", AGENT_LIST)
            c_name = st.text_input("Codename:")
            a_skill = st.text_input("KI-Spezialfähigkeit:")
            if st.form_submit_button("PROFIL SPEICHERN"):
                df_p = get_fresh_data("Profiles")
                new_p = pd.DataFrame([{"Agent": a_name, "Codename": c_name, "Skill": a_skill}])
                updated_p = pd.concat([df_p[df_p["Agent"] != a_name], new_p], ignore_index=True)
                conn.update(worksheet="Profiles", data=updated_p)
                st.success("Profil im Zentralspeicher verriegelt.")
                time.sleep(1)
                st.rerun()

        st.subheader("Aktive Agenten")
        p_df_display = get_fresh_data("Profiles")
        if not p_df_display.empty:
            for idx, r in p_df_display.iterrows():
                st.markdown(f'<div class="agent-card"><b>{r["Agent"]}</b> | CODE: {r["Codename"]} | SKILL: {r["Skill"]}</div>', unsafe_allow_html=True)

    # TAB 2: SABOTAGE
    with t2:
        st.header("Die Sabotage-Akte")
        with st.form("s_form"):
            s_thema = st.text_input("Welcher Prozess sabotiert uns?")
            s_details = st.text_area("Details:")
            if st.form_submit_button("AKTE AN NICO SENDEN"):
                if s_thema:
                    df_s = get_fresh_data("Sabotage")
                    new_s = pd.DataFrame([{"Thema": s_thema, "Details": s_details}])
                    updated_s = pd.concat([df_s, new_s], ignore_index=True).drop_duplicates(subset=["Thema"])
                    conn.update(worksheet="Sabotage", data=updated_s)
                    st.success("Thema archiviert.")
                    time.sleep(1)
                    st.rerun()

        st.subheader("Archivierte Themen")
        s_df_display = get_fresh_data("Sabotage")
        for idx, r in s_df_display.iterrows():
            with st.expander(f"🔎 {r['Thema']}"):
                st.write(r["Details"])

    # TAB 3: COIN-INVESTMENT
    with t3:
        st.header("💰 Operation: Golden Coin")
        st.write("Verteile genau 100 Coins auf die Sabotage-Themen.")
        
        df_sabotage_list = get_fresh_data("Sabotage")
        if df_sabotage_list.empty:
            st.warning("Keine Sabotage-Akten zum Investment verfügbar.")
        else:
            voter = st.selectbox("Wähle deinen Namen:", AGENT_LIST, key="v_sel_coin")
            themen = df_sabotage_list["Thema"].unique()
            
            investments = {}
            total_spent = 0
            
            # Slider für jedes Thema
            for item in themen:
                val = st.slider(f"Investment für: {item}", 0, 100, 0, key=f"coin_{voter}_{item}")
                investments[item] = val
                total_spent += val
            
            st.markdown(f"### Gesamt-Coins für {voter}: `{total_spent} / 100`")
            
            if total_spent > 100:
                st.error(f"Budget überschritten! Bitte entferne {total_spent - 100} Coins.")
            elif total_spent < 100:
                st.info(f"Du hast noch {100 - total_spent} Coins übrig.")
            else:
                # Exakt 100 Coins
                if st.button("INVESTITION IN GOOGLE SHEETS SPEICHERN"):
                    with st.spinner("Übertrage Daten..."):
                        # Daten für das Sheet vorbereiten
                        vote_row = {"Voter": voter, "Total": total_spent}
                        vote_row.update(investments)
                        new_vote_df = pd.DataFrame([vote_row])
                        
                        # Alte Votes laden
                        df_votes = get_fresh_data("Votes")
                        
                        # Den alten Vote dieses Agents entfernen (falls vorhanden) und neuen anhängen
                        if not df_votes.empty and "Voter" in df_votes.columns:
                            df_votes = df_votes[df_votes["Voter"] != voter]
                        
                        updated_votes = pd.concat([df_votes, new_vote_df], ignore_index=True)
                        
                        # Speichern
                        conn.update(worksheet="Votes", data=updated_votes)
                        st.balloons()
                        st.success(f"Danke Agent {voter}. Dein Investment wurde sicher im Zentralspeicher hinterlegt.")
