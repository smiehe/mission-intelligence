import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Autorefresh für den flüssigen Takt
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# 1. Basis-Konfiguration
st.set_page_config(page_title="USS Intelligence HQ", page_icon="🚀", layout="wide")

# --- DATA ENGINE (GSHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def get_cached_data(ws_name):
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        return df.dropna(how="all")
    except:
        if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill"])
        if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
        return pd.DataFrame()

def force_reload():
    st.cache_data.clear()
    st.rerun()

# --- MISSIONS-DATEN ---
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

# --- STYLING (STAR TREK / LCARS STYLE) ---
st.markdown("""
<style>
    /* Grund-Design: Tiefraum-Schwarz */
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Courier New', monospace; }
    
    /* Splash Screen Upgrade */
    .splash-box {
        text-align: center; margin-top: 5%; padding: 60px;
        border: 2px solid #00FF41; 
        background: linear-gradient(180deg, rgba(0,255,65,0.1) 0%, rgba(0,0,0,1) 100%);
        box-shadow: 0 0 50px rgba(0,255,65,0.3);
        border-radius: 0 50px 0 50px;
    }
    .splash-title { color: #00FF41; font-size: 5rem; font-weight: bold; text-shadow: 0 0 20px #00FF41; letter-spacing: 15px; }
    
    /* Sidebar: LCARS Panel Look */
    [data-testid="stSidebar"] { 
        background-color: #050505; 
        border-right: 5px solid #00FF41; 
        padding-top: 20px;
    }
    [data-testid="stSidebar"] * { 
        color: #FFFFFF !important; 
        font-size: 1.25rem !important; 
        font-weight: bold !important; 
    }

    /* Timer: Warp Core Display */
    .timer-display {
        font-family: 'Courier New', monospace;
        color: #00FF41; font-size: 4rem; text-align: center;
        border: 4px solid #00FF41; border-radius: 15px;
        padding: 20px; background: rgba(0, 255, 65, 0.05);
        text-shadow: 0 0 15px #00FF41;
        margin-bottom: 20px;
    }

    /* Header: Ship Status Bar */
    .mission-header {
        width: 100%; background: linear-gradient(90deg, #00FF41 0%, #000 70%);
        color: #000; padding: 15px; font-weight: bold; 
        font-size: 1.5rem; letter-spacing: 5px; margin-top: -75px; 
        margin-bottom: 40px; border-radius: 0 0 30px 0;
    }

    /* Buttons: Console Toggles */
    .stButton>button {
        background-color: #111 !important; color: #00FF41 !important;
        border: 2px solid #00FF41 !important; border-radius: 5px !important;
        height: 3.5rem; font-weight: bold !important; font-size: 1.1rem !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00FF41 !important; color: #000 !important;
        box-shadow: 0 0 20px #00FF41;
    }

    /* Cards: Tactical Display */
    .agent-card {
        border-left: 10px solid #00FF41; 
        border-top: 1px solid #00FF41;
        border-right: 1px solid #00FF41;
        border-bottom: 1px solid #00FF41;
        padding: 20px; background: rgba(0, 255, 65, 0.03); 
        border-radius: 0 15px 15px 0; margin-bottom: 15px;
    }
    .agent-card b { color: #00FF41; font-size: 1.8rem; text-transform: uppercase; }

    /* Forms & Inputs */
    label { color: #00FF41 !important; font-size: 1.5rem !important; font-weight: bold !important; margin-bottom: 10px; }
    input, textarea, select { 
        background-color: #000 !important; color: #FFF !important; 
        border: 2px solid #00FF41 !important; font-size: 1.3rem !important;
    }

    /* Tabs: LCARS Style */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        color: #00FF41 !important; border: 2px solid #00FF41 !important;
        border-radius: 10px 10px 0 0 !important; padding: 15px 30px !important;
        background: #111 !important; font-size: 1.2rem !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FF41 !important; color: #000 !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; background: #000; }
    ::-webkit-scrollbar-thumb { background: #00FF41; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- STARTBILDSCHIRM ---
if not st.session_state.access_granted:
    st.markdown("""
        <div class="splash-box">
            <p style="letter-spacing: 5px; color: #FFF;">AUTHORIZATION REQUIRED</p>
            <h1 class="splash-title">MISSION<br>INTELLIGENCE</h1>
            <p style="font-size: 1.5rem; color: #00FF41;">STARDATE 02.04.2026 | QUARTERDAY Q1</p>
        </div>
    """, unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1,1,1])
    with col_mid:
        st.write("")
        if st.button("INITIATE HQ ACCESS"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # AUTO-REFRESH (Timer-Tick jede Sekunde)
    if st_autorefresh:
        st_autorefresh(interval=1000, key="timer_tick")

    st.markdown('<div class="mission-header">>> USS INTELLIGENCE // MAIN COMPUTER // STATUS: SECURE</div>', unsafe_allow_html=True)

    # --- SIDEBAR: TACTICAL CONTROL ---
    with st.sidebar:
        st.markdown("<h3 style='color:#00FF41;'>CHRONOMETER</h3>", unsafe_allow_html=True)
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        elapsed = time.time() - st.session_state.mission_start_time
        rem_sec = max(0, (active_info['duration'] * 60) - elapsed)
        m, s = divmod(int(rem_sec), 60)
        
        # Rotes Glühen wenn die Zeit knapp wird
        t_color = "#00FF41" if rem_sec > 300 else "#FF0000"
        st.markdown(f'<div class="timer-display" style="color:{t_color}; border-color:{t_color}; text-shadow: 0 0 15px {t_color};">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("<h3 style='color:#00FF41;'>MISSION LOG</h3>", unsafe_allow_html=True)
        for k, d in MISSION_DATA.items():
            btn_label = f"[{k}] {d['name']}"
            if k == st.session_state.active_mission_key: btn_label = f"▶ {btn_label}"
            if st.sidebar.button(btn_label, key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()
        
        st.markdown("---")
        if st.button("SYNC DATA"): force_reload()

    # --- MAIN TERMINAL ---
    st.title(f"📍 {active_info['name']}")
    t1, t2, t3 = st.tabs(["👤 PERSONNEL", "📂 SABOTAGE", "💰 CREDITS"])

    with t1:
        st.header("Personnel Database")
        with st.form("p_form", clear_on_submit=True):
            a_name = st.selectbox("Identify Agent:", AGENT_LIST)
            c_name = st.text_input("Assigned Codename:")
            a_skill = st.text_input("Specialization:")
            if st.form_submit_button("COMMIT TO DATABASE"):
                with st.spinner("Encrypting..."):
                    df_p = get_cached_data("Profiles")
                    new_p = pd.DataFrame([{"Agent": a_name, "Codename": c_name, "Skill": a_skill}])
                    updated_p = pd.concat([df_p[df_p["Agent"] != a_name], new_p], ignore_index=True)
                    conn.update(worksheet="Profiles", data=updated_p)
                    force_reload()

        st.subheader("Active Personnel on Deck")
        p_list = get_cached_data("Profiles")
        for idx, r in p_list.iterrows():
            col_a, col_b = st.columns([0.85, 0.15])
            with col_a:
                st.markdown(f"""
                <div class="agent-card">
                    <b>{r["Agent"]}</b><br>
                    <span style="color:#FFF; font-size:1.1rem;">CODE: {r["Codename"]} | SPEC: {r["Skill"]}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.write("")
                if st.button("🗑️", key=f"del_p_{idx}"):
                    df_cleaned = p_list[p_list["Agent"] != r["Agent"]]
                    conn.update(worksheet="Profiles", data=df_cleaned)
                    force_reload()

    with t2:
        st.header("Security Breach Log")
        with st.form("s_form", clear_on_submit=True):
            s_thema = st.text_input("Identify Sabotage Sector:")
            s_details = st.text_area("Detailed Breach Report:")
            if st.form_submit_button("SUBMIT REPORT"):
                df_s = get_cached_data("Sabotage")
                new_s = pd.DataFrame([{"Thema": s_thema, "Details": s_details}])
                updated_s = pd.concat([df_s, new_s], ignore_index=True).drop_duplicates(subset=["Thema"])
                conn.update(worksheet="Sabotage", data=updated_s)
                force_reload()
        
        s_list = get_cached_data("Sabotage")
        for idx, r in s_list.iterrows():
            with st.expander(f"🔴 ALERT: {r['Thema']}"):
                st.write(f"**Description:** {r['Details']}")

    with t3:
        st.header("Credit Investment Console")
        df_coins = get_cached_data("Sabotage")
        if df_coins.empty:
            st.info("Awaiting Security Breach Reports...")
        else:
            voter = st.selectbox("Assigning Officer:", AGENT_LIST, key="v_sel")
            spent = 0
            for item in df_coins["Thema"].unique():
                spent += st.slider(f"ALLOCATE CREDITS: {item}", 0, 100, 0, key=f"c_{voter}_{item}")
            
            # Statusanzeige mit Farbe
            c_status = "#00FF41" if spent == 100 else "#FFF"
            st.markdown(f"### Total Allocation: <span style='color:{c_status};'>{spent} / 100 Credits</span>", unsafe_allow_html=True)
            
            if spent == 100:
                if st.button("FINALIZE TRANSACTION"):
                    st.balloons()
