import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Autorefresh für den flüssigen Takt (Timer)
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# 1. Basis-Konfiguration
st.set_page_config(page_title="PCS Intelligence HQ", page_icon="🚀", layout="wide")

# --- DATA ENGINE (GSHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5) # Kurzer Cache für flüssige Bedienung
def get_cached_data(ws_name):
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        return df.dropna(how="all")
    except:
        if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
        if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
        if ws_name == "Votes": return pd.DataFrame(columns=["Voter", "Total"])
        return pd.DataFrame()

def force_reload():
    """Löscht den Cache und erzwingt Daten-Synchronisation."""
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

# --- SYSTEM STATUS ---
if 'access_granted' not in st.session_state: st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state: st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state: st.session_state.mission_start_time = time.time()

# --- STYLING (LCARS / TACTICAL DESIGN - KEINE VERLÄUFE) ---
st.markdown("""
<style>
    /* Grund-Design */
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Courier New', monospace; }
    
    /* Splash Box */
    .splash-box {
        text-align: center; margin-top: 5%; padding: 60px;
        border: 4px solid #00FF41; 
        background-color: #050505;
        box-shadow: 0 0 50px rgba(0,255,65,0.2);
        border-radius: 0 50px 0 50px;
    }

    /* Sidebar Panel */
    [data-testid="stSidebar"] { 
        background-color: #050505; 
        border-right: 5px solid #00FF41; 
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; font-size: 1.25rem !important; }

    /* Timer Display */
    .timer-display {
        font-family: 'Courier New', monospace;
        color: #00FF41; font-size: 4rem; text-align: center;
        border: 4px solid #00FF41; border-radius: 15px;
        padding: 20px; background: #000;
        text-shadow: 0 0 15px #00FF41;
        margin-bottom: 20px;
    }

    /* Header */
    .mission-header {
        width: 100%; background-color: #00FF41; 
        color: #000; padding: 15px; font-weight: bold; 
        font-size: 1.5rem; letter-spacing: 5px; margin-top: -75px; 
        margin-bottom: 40px; border-radius: 0 0 30px 0;
    }

    /* Buttons */
    .stButton>button {
        background-color: #111 !important; color: #FFFFFF !important;
        border: 3px solid #00FF41 !important; 
        height: 4rem; font-weight: bold !important; font-size: 1.2rem !important;
    }
    .stButton>button:hover {
        background-color: #00FF41 !important; color: #000 !important;
    }

    /* Info Karten */
    .info-card {
        border: 1px solid #00FF41;
        border-left: 10px solid #00FF41;
        padding: 15px; background: #111; 
        border-radius: 0 15px 15px 0; margin-bottom: 10px;
    }

    /* Texte & Labels */
    label, p, span, div { color: #FFFFFF !important; font-size: 1.3rem !important; }
    label { color: #00FF41 !important; font-weight: bold !important; font-size: 1.4rem !important; }
    
    /* Eingabefelder */
    input, textarea { 
        background-color: #000 !important; color: #FFF !important; 
        border: 2px solid #00FF41 !important; font-size: 1.3rem !important;
    }

    /* FIX: SCHWARZER TEXT AUF GRÜNEM GRUND (Identify Agent Selectbox) */
    div[data-baseweb="select"] > div {
        background-color: #00FF41 !important;
        border: 2px solid #00FF41 !important;
    }
    div[data-baseweb="select"] span {
        color: #000000 !important;
        font-weight: bold !important;
    }
    div[data-baseweb="select"] svg {
        fill: #000000 !important;
    }
    li[data-baseweb="option"] {
        color: #000000 !important;
    }

    /* Tab Design */
    .stTabs [data-baseweb="tab"] {
        color: #00FF41 !important; border: 2px solid #00FF41 !important;
        background: #111 !important; font-size: 1.3rem !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FF41 !important; color: #000 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- APP LOGIK ---
if not st.session_state.access_granted:
    st.markdown('<div class="splash-box"><h1 style="color:#00FF41; font-size:5rem;">MISSION<br>INTELLIGENCE</h1><p>AUTHORIZATION REQUIRED</p></div>', unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1,1,1])
    with col_mid:
        if st.button("INITIATE ACCESS"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # AUTO-REFRESH (Timer-Tick jede Sekunde)
    if st_autorefresh:
        st_autorefresh(interval=1000, key="timer_tick")

    st.markdown('<div class="mission-header">>> PCS INTELLIGENCE // MAIN COMPUTER // SECURE ACCESS</div>', unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<h3 style='color:#00FF41;'>CHRONOMETER</h3>", unsafe_allow_html=True)
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        elapsed = time.time() - st.session_state.mission_start_time
        rem_sec = max(0, (active_info['duration'] * 60) - elapsed)
        m, s = divmod(int(rem_sec), 60)
        t_color = "#00FF41" if rem_sec > 300 else "#FF0000"
        st.markdown(f'<div class="timer-display" style="color:{t_color}; border-color:{t_color};">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("MISSION LOG")
        for k, d in MISSION_DATA.items():
            lbl = f"[{k}] {d['name']}"
            if k == st.session_state.active_mission_key: lbl = f"▶ {lbl}"
            if st.sidebar.button(lbl, key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()
        
        st.markdown("---")
        if st.button("SYNC SYSTEM"): force_reload()

    # --- MAIN TERMINAL TABS ---
    t1, t2, t3 = st.tabs(["👤 PERSONNEL", "📂 SABOTAGE", "💰 CREDITS"])

    # TAB 1: PERSONNEL
    with t1:
        top_col1, top_col2 = st.columns([0.7, 0.3])
        with top_col1:
            st.header("Personnel Database")
        with top_col2:
            st.write(" ")
            save_p = st.button("COMMIT TO DATABASE", use_container_width=True)

        input_col1, input_col2 = st.columns(2)
        with input_col1:
            a_name = st.selectbox("Identify Agent:", AGENT_LIST)
            c_name = st.text_input("Codename:")
        with input_col2:
            a_skill = st.text_input("Specialization:")

        if save_p:
            if c_name:
                df_p = get_cached_data("Profiles")
                new_p = pd.DataFrame([{"Agent": a_name, "Codename": c_name, "Skill": a_skill}])
                updated_p = pd.concat([df_p[df_p["Agent"] != a_name], new_p], ignore_index=True)
                conn.update(worksheet="Profiles", data=updated_p)
                st.success("DATA COMMITTED")
                force_reload()

        st.markdown("---")
        p_list = get_cached_data("Profiles")
        for idx, r in p_list.iterrows():
            c1, c2 = st.columns([0.9, 0.1])
            with c1:
                st.markdown(f'<div class="info-card"><b>{r["Agent"]}</b> | CODE: {r["Codename"]} | SPEC: {r["Skill"]}</div>', unsafe_allow_html=True)
            with c2:
                if st.button("🗑️", key=f"del_p_{idx}"):
                    conn.update(worksheet="Profiles", data=p_list[p_list["Agent"] != r["Agent"]])
                    force_reload()

    # TAB 2: SABOTAGE
    with t2:
        top_col1_s, top_col2_s = st.columns([0.7, 0.3])
        with top_col1_s:
            st.header("Security Breach Log")
        with top_col2_s:
            st.write(" ")
            save_s = st.button("SUBMIT REPORT", use_container_width=True)

        s_thema = st.text_input("Sabotage Sector (Thema):")
        s_details = st.text_area("Detailed Breach Report (Details):", height=150)

        if save_s:
            if s_thema:
                df_s = get_cached_data("Sabotage")
                new_s = pd.DataFrame([{"Thema": s_thema, "Details": s_details}])
                updated_s = pd.concat([df_s, new_s], ignore_index=True).drop_duplicates(subset=["Thema"])
                conn.update(worksheet="Sabotage", data=updated_s)
                st.success("BREACH REGISTERED")
                force_reload()

        st.markdown("---")
        s_list = get_cached_data("Sabotage")
        for idx, r in s_list.iterrows():
            c1, c2 = st.columns([0.9, 0.1])
            with c1:
                with st.expander(f"🔴 ALERT: {r['Thema']}"):
                    st.write(f"DETAILS: {r['Details']}")
            with c2:
                if st.button("🗑️", key=f"del_s_{idx}"):
                    conn.update(worksheet="Sabotage", data=s_list[s_list["Thema"] != r["Thema"]])
                    force_reload()

    # TAB 3: CREDITS (INVESTMENT)
    with t3:
        st.header("Credit Investment Console")
        df_coins = get_cached_data("Sabotage")
        
        if df_coins.empty:
            st.info("Awaiting reports...")
        else:
            voter = st.selectbox("Assigning Officer:", AGENT_LIST, key="v_sel")
            spent = 0
            investments = {}
            
            for item in df_coins["Thema"].unique():
                val = st.slider(f"ALLOCATE: {item}", 0, 100, 0, key=f"c_{voter}_{item}")
                investments[item] = val
                spent += val
            
            c_status = "#00FF41" if spent == 100 else "#FF4B4B"
            st.markdown(f"### Total Allocation: <span style='color:{c_status};'>{spent} / 100</span>", unsafe_allow_html=True)
            
            if spent == 100:
                if st.button("FINALIZE TRANSACTION"):
                    with st.spinner("Transmitting data..."):
                        # Daten für Google Sheets vorbereiten
                        vote_row = {"Voter": voter, "Total": 100}
                        vote_row.update(investments)
                        new_vote_df = pd.DataFrame([vote_row])
                        
                        # Bestehende Votes laden und aktualisieren
                        df_votes = get_cached_data("Votes")
                        if not df_votes.empty:
                            df_votes = df_votes[df_votes["Voter"] != voter]
                        
                        updated_votes = pd.concat([df_votes, new_vote_df], ignore_index=True)
                        conn.update(worksheet="Votes", data=updated_votes)
                        
                        st.balloons()
                        st.success("TRANSACTION SECURED")
            elif spent > 100:
                st.error(f"Budget Exceeded! Remove {spent - 100} credits.")
            else:
                st.warning(f"Allocate {100 - spent} more credits to finalize.")
