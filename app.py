import streamlit as st
import time

# Autorefresh laden
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# Seiteneinstellungen
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- INITIALISIERUNG ---
AGENT_LIST = ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"]

# Speicher für Agenten-Profile
if 'agent_profiles' not in st.session_state:
    st.session_state.agent_profiles = {}

# Speicher für die Sabotage-Akten
if 'sabotage_list' not in st.session_state:
    st.session_state.sabotage_list = []

# Gedächtnis für die Coins (Pro Agent ein Dictionary)
if 'all_votes' not in st.session_state:
    st.session_state.all_votes = {agent: {} for agent in AGENT_LIST}

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
        color: #00FF41; font-size: 3rem; text-align: center;
        padding: 15px; border: 2px solid #00FF41;
        background: rgba(0, 255, 65, 0.1); margin-bottom: 5px;
    }
    /* Agenten-Karte Styling */
    .agent-card {
        border: 1px solid #00FF41;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        background: rgba(0, 255, 65, 0.05);
    }
    .stButton>button {
        background-color: #000000 !important; color: #00FF41 !important;
        border: 1px solid #00FF41 !important; width: 100%; text-align: left !important;
    }
    .stButton>button:hover { border: 1px solid #FFFFFF !important; color: #FFFFFF !important; }
    input, textarea, select { 
        background-color: #111 !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

if st.session_state.access_granted and st_autorefresh:
    st_autorefresh(interval=1000, key="timer_refresh")

# --- LOGIK: STARTBILDSCHIRM ---
if not st.session_state.access_granted:
    st.markdown("""
        <div class="splash-container">
            <h1 style="font-size: 4rem; letter-spacing: 10px;">MISSION:<br>INTELLIGENCE</h1>
            <p>> PCS DIVISION | QUARTERDAY Q1 2026<br>> STATUS: ENCRYPTED</p>
        </div>
    """, unsafe_allow_html=True)
    _, col2, _ = st.columns([1,1,1])
    with col2:
        if st.button("ENTER HQ / MISSION STARTEN"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # --- SIDEBAR ---
    st.sidebar.markdown("### ⏳ MISSION CLOCK")
    mission_info = {
        "09:00": {"name": "Operation: Agent Profile", "duration": 30},
        "09:30": {"name": "The Intelligence Briefing (Nico)", "duration": 90},
        "11:15": {"name": "The Deep-Dive Mission", "duration": 90},
        "12:45": {"name": "Field Rations (Lunch)", "duration": 60},
        "13:45": {"name": "Final Briefing (Wrap-up)", "duration": 30},
        "15:30": {"name": "Field Operation (Museum)", "duration": 120},
        "17:30": {"name": "Safe House Drinks & Dinner", "duration": 180}
    }
    
    current_mission = mission_info[st.session_state.active_mission_key]
    elapsed = time.time() - st.session_state.mission_start_time
    remaining = max(0, (current_mission['duration'] * 60) - elapsed)
    
    mins, secs = divmod(int(remaining), 60)
    timer_col = "#00FF41" if remaining > 300 else "#FF0000"
    st.sidebar.markdown(f'<div class="timer-box" style="color:{timer_col}; border-color:{timer_col};">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
    
    st.sidebar.header("📍 EINSATZPLAN")
    for time_key, data in mission_info.items():
        label = f"{time_key} | {data['name']}"
        if time_key == st.session_state.active_mission_key: label = f"▶ {label}"
        if st.sidebar.button(label, key=f"btn_{time_key}"):
            st.session_state.active_mission_key = time_key
            st.session_state.mission_start_time = time.time()
            st.rerun()

    # --- HAUPTBEREICH ---
    st.title(f"🕵️‍♂️ HQ: {current_mission['name']}")
    tab1, tab2, tab3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with tab1:
        st.header("Operation: Agent Profile")
        with st.form("checkin_form"):
            name = st.selectbox("PCS Agent:", AGENT_LIST)
            codename = st.text_input("KI-Generierter Codename:")
            skill = st.text_input("KI-Spezialfähigkeit:")
            if st.form_submit_button("PROFIL AKTIVIEREN"):
                if codename and skill:
                    # Speichere das Profil im Session State
                    st.session_state.agent_profiles[name] = {
                        "codename": codename,
                        "skill": skill
                    }
                    st.success(f"Agent {name} registriert.")
                else:
                    st.error("Bitte Codename und Spezialfähigkeit eingeben!")

        # --- GALERIE DER AKTIVEN AGENTEN ---
        st.markdown("---")
        st.subheader("🕵️‍♂️ Aktive PCS-Agenten im Feld")
        if not st.session_state.agent_profiles:
            st.info("Warte auf Identifizierung der Agenten...")
        else:
            # Zeige die Profile in einem Grid an
            cols = st.columns(2)
            for i, (agent, data) in enumerate(st.session_state.agent_profiles.items()):
                with cols[i % 2]:
                    st.markdown(f"""
                        <div class="agent-card">
                            <b style="color:#00FF41;">AGENT: {agent}</b><br>
                            <span style="opacity:0.7;">CODENAME:</span> {data['codename']}<br>
                            <span style="opacity:0.7;">SKILL:</span> {data['skill']}
                        </div>
                    """, unsafe_allow_html=True)

    with tab2:
        st.header("Die Sabotage-Akte")
        with st.form("sabotage_form", clear_on_submit=True):
            p_name = st.text_input("Name des Sabotage-Akts:")
            desc = st.text_area("Details der Ineffizienz:")
            submitted = st.form_submit_button("AKTE AN NICO SENDEN")
            if submitted and p_name:
                if p_name not in st.session_state.sabotage_list:
                    st.session_state.sabotage_list.append(p_name)
                    for agent in AGENT_LIST:
                        st.session_state.all_votes[agent][p_name] = 0
                st.success(f"'{p_name}' wurde für das Voting freigeschaltet.")

    with tab3:
        st.header("💰 Operation: Golden Coin")
        if not st.session_state.sabotage_list:
            st.warning("⚠️ Keine Sabotage-Akten vorhanden.")
        else:
            voter = st.selectbox("Wer investiert gerade?", AGENT_LIST, key="voter_select")
            st.info(f"Agent {voter}, verteilen Sie Ihre 100 Coins.")
            
            total_spent = 0
            for s_item in st.session_state.sabotage_list:
                current_val = st.session_state.all_votes[voter].get(s_item, 0)
                new_val = st.slider(f"Investment: {s_item}", 0, 100, current_val, key=f"slider_{voter}_{s_item}")
                st.session_state.all_votes[voter][s_item] = new_val
                total_spent += new_val
            
            st.markdown(f"### Status {voter}: `{total_spent} / 100` Coins")
            if total_spent == 100:
                if st.button(f"INVESTITION FÜR {voter} FINALISIEREN"):
                    st.balloons()
            elif total_spent > 100:
                st.error(f"Budget überschritten! (-{total_spent - 100})")
