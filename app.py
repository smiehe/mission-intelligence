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

# Speicher für die Sabotage-Akten (wird für das Voting genutzt)
if 'sabotage_list' not in st.session_state:
    st.session_state.sabotage_list = []

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
                st.success(f"Agent {name} registriert.")

    with tab2:
        st.header("Die Sabotage-Akte")
        st.write("Welche Prozesse sabotieren unsere Coordination?")
        with st.form("sabotage_form", clear_on_submit=True):
            p_name = st.text_input("Name des Sabotage-Akts (z.B. Salesforce-Sync):")
            desc = st.text_area("Details der Ineffizienz:")
            submitted = st.form_submit_button("AKTE AN NICO SENDEN")
            if submitted and p_name:
                if p_name not in st.session_state.sabotage_list:
                    st.session_state.sabotage_list.append(p_name)
                st.success(f"'{p_name}' wurde in die Datenbank aufgenommen.")

    with tab3:
        st.header("💰 Operation: Golden Coin")
        if not st.session_state.sabotage_list:
            st.warning("⚠️ Keine Sabotage-Akten vorhanden. Bitte erst in Tab 2 Probleme identifizieren!")
        else:
            st.info("Verteilen Sie exakt 100 Coins auf die identifizierten Sabotage-Akten.")
            voter = st.selectbox("PCS Agent für Voting:", AGENT_LIST, key="v_t3")
            
            total_coins = 0
            votes = {}
            
            # Dynamische Slider basierend auf den Einträgen aus Tab 2
            for s_item in st.session_state.sabotage_list:
                votes[s_item] = st.slider(f"Investment für: {s_item}", 0, 100, 0, key=f"v_{s_item}")
                total_coins += votes[s_item]
            
            st.markdown(f"### Gesamt-Investment: `{total_coins} / 100` Coins")
            
            if total_coins > 100:
                st.error(f"⚠️ Budget überschritten! Bitte {total_coins - 100} Coins abziehen.")
            elif total_coins < 100:
                st.warning(f"Es müssen noch {100 - total_coins} Coins vergeben werden.")
            else:
                st.success("✅ Perfekte Budgetierung. Mission bereit zum Abschluss.")
                if st.button("INVESTITION FINALISIEREN"):
                    st.balloons()
                    st.success("Investment-Daten wurden sicher ans HQ übertragen.")
