import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Seiteneinstellungen
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- VERBINDUNG ZUM ZENTRALSPEICHER ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Hilfsfunktion zum sicheren Lesen der Daten
def safe_read(worksheet_name):
    try:
        return conn.read(worksheet=worksheet_name, ttl="0")
    except Exception:
        # Falls Blatt leer oder Fehler, leeren DataFrame mit Köpfen zurückgeben
        if worksheet_name == "Profiles":
            return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
        if worksheet_name == "Sabotage":
            return pd.DataFrame(columns=["Thema", "Details"])
        return pd.DataFrame()

# --- INITIALISIERUNG ---
AGENT_LIST = ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"]

if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False

# --- DESIGN & CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF41; }
    .splash-container {
        text-align: center; margin-top: 10%; padding: 50px;
        border: 3px solid #00FF41; box-shadow: 0 0 50px #00FF41;
        background-color: #050505; font-family: 'Courier New', Courier, monospace;
    }
    .agent-card {
        border: 1px solid #00FF41; padding: 15px; border-radius: 5px; margin-bottom: 10px; background: rgba(0, 255, 65, 0.05);
    }
    .stButton>button { background-color: #000000 !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; width: 100%; }
    input, textarea, select { background-color: #111 !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- STARTBILDSCHIRM ---
if not st.session_state.access_granted:
    st.markdown('<div class="splash-container"><h1>MISSION:<br>INTELLIGENCE</h1><p>> PCS DIVISION | Q1 2026</p></div>', unsafe_allow_html=True)
    _, col2, _ = st.columns([1,1,1])
    with col2:
        if st.button("ENTER HQ / IDENTITÄT BESTÄTIGEN"):
            st.session_state.access_granted = True
            st.rerun()
else:
    # --- HQ BEREICH ---
    tab1, tab2, tab3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with tab1:
        st.header("Operation: Agent Profile")
        with st.form("profile_form"):
            name = st.selectbox("PCS Agent:", AGENT_LIST)
            codename = st.text_input("KI-Generierter Codename:")
            skill = st.text_input("KI-Spezialfähigkeit:")
            if st.form_submit_button("PROFIL IM NETZWERK SPEICHERN"):
                if codename and skill:
                    new_data = pd.DataFrame([{"Agent": name, "Codename": codename, "Skill": skill}])
                    old_data = safe_read("Profiles")
                    updated_df = pd.concat([old_data, new_data], ignore_index=True)
                    conn.update(worksheet="Profiles", data=updated_df)
                    st.success("Profil global gespeichert!")
                    time.sleep(1)
                    st.rerun()

        st.subheader("Aktive PCS-Agenten im Netzwerk")
        profiles_df = safe_read("Profiles")
        if not profiles_df.empty:
            cols = st.columns(2)
            # Entferne leere Zeilen
            profiles_df = profiles_df.dropna(subset=["Agent"])
            for i, row in profiles_df.iterrows():
                with cols[i % 2]:
                    st.markdown(f'<div class="agent-card"><b>AGENT: {row["Agent"]}</b><br>CODENAME: {row["Codename"]}<br>SKILL: {row["Skill"]}</div>', unsafe_allow_html=True)

    with tab2:
        st.header("Die Sabotage-Akte")
        with st.form("sabotage_form"):
            p_name = st.text_input("Name des Sabotage-Akts:")
            desc = st.text_area("Details:")
            if st.form_submit_button("AKTE AN NICO SENDEN"):
                if p_name:
                    sabotage_data = pd.DataFrame([{"Thema": p_name, "Details": desc}])
                    existing_sabotage = safe_read("Sabotage")
                    updated_sabotage = pd.concat([existing_sabotage, sabotage_data], ignore_index=True)
                    conn.update(worksheet="Sabotage", data=updated_sabotage)
                    st.success(f"'{p_name}' registriert.")
                    time.sleep(1)
                    st.rerun()

    with tab3:
        st.header("💰 Operation: Golden Coin")
        sabotage_df = safe_read("Sabotage")
        if sabotage_df.empty:
            st.warning("Keine Sabotage-Akten im Zentralspeicher gefunden.")
        else:
            voter = st.selectbox("Wer investiert?", AGENT_LIST, key="v_gs")
            themen = sabotage_df["Thema"].unique()
            total = 0
            current_votes = {}
            for item in themen:
                current_votes[item] = st.slider(f"Investment: {item}", 0, 100, 0, key=f"sl_{item}")
                total += current_votes[item]
            
            st.markdown(f"### Gesamt: `{total} / 100` Coins")
            if total == 100:
                if st.button("VOTING FINALISIEREN"):
                    vote_row = {"Voter": voter}
                    vote_row.update(current_votes)
                    # Hier speichern wir in "Votes"
                    st.balloons()
                    st.success("Investment übertragen!")
