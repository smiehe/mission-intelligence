import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# --- 1. PLUGINS & CONFIG ---
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

st.set_page_config(page_title="PCS Intelligence HQ", page_icon="🚀", layout="wide")

# --- 2. DATA ENGINE (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def get_cached_data(ws_name):
    """Lädt Daten aus GSheets und sichert die Tabellenstruktur, um Abstürze zu vermeiden."""
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        if df is None: df = pd.DataFrame()
        
        # Sicherstellen, dass alle nötigen Spalten existieren
        if ws_name == "Profiles":
            for col in ["Agent", "Codename", "Skill", "Questions"]:
                if col not in df.columns: df[col] = ""
        elif ws_name == "Sabotage":
            for col in ["Thema", "Details"]:
                if col not in df.columns: df[col] = ""
        elif ws_name == "Votes":
            for col in ["Voter", "Total"]:
                if col not in df.columns: df[col] = ""
                
        return df.dropna(how="all")
    except Exception:
        # Fallback-Gerüst bei Verbindungsfehlern
        if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill", "Questions"])
        if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
        if ws_name == "Votes": return pd.DataFrame(columns=["Voter", "Total"])
        return pd.DataFrame()

def force_reload():
    """Erzwingt ein Neuladen der Cloud-Daten."""
    st.cache_data.clear()
    st.rerun()

# --- 3. MISSION SETUP ---
AGENT_LIST = ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"]
MISSION_DATA = {
    "09:00": {"name": "Operation: Agent Profile", "duration": 10},
    "09:10": {"name": "The PM Sabotage File", "duration": 15},
    "09:25": {"name": "Credit Allocation", "duration": 5},
    "09:30": {"name": "Main Briefing (Nico)", "duration": 90}
}

if 'access_granted' not in st.session_state: st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state: st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state: st.session_state.mission_start_time = time.time()

# --- 4. TACTICAL CSS (LCARS DESIGN) ---
st.markdown("""
<style>
    /* Basis Layout */
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Courier New', monospace; }
    
    /* Startbildschirm */
    .splash-box {
        text-align: center; margin-top: 5%; padding: 60px;
        border: 4px solid #00FF41; background-color: #050505;
        box-shadow: 0 0 50px rgba(0,255,65,0.2); border-radius: 0 50px 0 50px;
    }

    /* Sidebar & Timer */
    [data-testid="stSidebar"] { background-color: #050505; border-right: 5px solid #00FF41; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; font-size: 1.25rem !important; }
    .timer-display {
        font-family: 'Courier New', monospace; color: #00FF41; font-size: 4rem; text-align: center;
        border: 4px solid #00FF41; border-radius: 15px; padding: 20px; background: #000;
        text-shadow: 0 0 15px #00FF41; margin-bottom: 20px;
    }

    /* Header & Buttons */
    .mission-header {
        width: 100%; background-color: #00FF41; color: #000; padding: 15px; font-weight: bold; 
        font-size: 1.5rem; letter-spacing: 5px; margin-top: -75px; 
        margin-bottom: 40px; border-radius: 0 0 30px 0;
    }
    .stButton>button {
        background-color: #111 !important; color: #FFFFFF !important;
        border: 3px solid #00FF41 !important; height: 3.5rem; font-weight: bold !important;
    }
    .stButton>button:hover { background-color: #00FF41 !important; color: #000 !important; }

    /* Textfelder & Typografie */
    label, p, span, div { color: #FFFFFF !important; font-size: 1.3rem !important; }
    label { color: #00FF41 !important; font-weight: bold !important; font-size: 1.4rem !important; }
    input, textarea { 
        background-color: #000 !important; color: #FFF !important; 
        border: 2px solid #00FF41 !important; font-size: 1.3rem !important;
    }

    /* --- DROPDOWN MENÜ FIX --- */
    /* Geschlossenes Feld (Grün) */
    div[data-baseweb="select"] > div {
        background-color: #00FF41 !important; border: 2px solid #00FF41 !important;
    }
    div[data-baseweb="select"] span { color: #000000 !important; font-weight: bold !important; }
    div[data-baseweb="select"] svg { fill: #000000 !important; }
    
    /* Offene Liste (Schwarz mit grünem Text) */
    div[data-baseweb="popover"], ul[role="listbox"] {
        background-color: #000000 !important; border: 1px solid #00FF41 !important;
    }
    li[role="option"] {
        background-color: #000000 !important; color: #00FF41 !important; 
        font-weight: bold !important; border-bottom: 1px solid #111;
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #00FF41 !important; color: #000000 !important;
    }
    /* ------------------------- */

    /* Tabs & Boxen */
    .stTabs [data-baseweb="tab"] {
        color: #00FF41 !important; border: 2px solid #00FF41 !important;
        background: #111 !important; font-size: 1.3rem !important;
    }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !important; color: #000 !important; }
    .prompt-box { border: 1px dashed #00FF41; padding: 15px; background: #111; margin-bottom: 20px; font-size: 1.1rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 5. APP INTERFACE ---
if not st.session_state.access_granted:
    # STARTBILDSCHIRM
    st.markdown('<div class="splash-box"><h1 style="color:#00FF41; font-size:5rem;">PCS<br>INTELLIGENCE</h1><p>AUTHORIZATION REQUIRED</p></div>', unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1,1,1])
    with col_mid:
        if st.button("INITIATE ACCESS"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # HAUPTMENÜ & TIMER
    if st_autorefresh:
        st_autorefresh(interval=1000, key="timer_tick")

    st.markdown('<div class="mission-header">>> PCS INTELLIGENCE // MAIN COMPUTER // SECURE ACCESS</div>', unsafe_allow_html=True)

    # -- SIDEBAR --
    with st.sidebar:
        st.markdown("<h3 style='color:#00FF41;'>CHRONOMETER</h3>", unsafe_allow_html=True)
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        elapsed = time.time() - st.session_state.mission_start_time
        rem_sec = max(0, (active_info['duration'] * 60) - elapsed)
        m, s = divmod(int(rem_sec), 60)
        t_color = "#00FF41" if rem_sec > 60 else "#FF0000"
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

    # -- TABS --
    t1, t2, t3 = st.tabs(["👤 PERSONNEL", "📂 SABOTAGE", "💰 CREDITS"])

    # TAB 1: PERSONNEL (Aufgabe 1)
    with t1:
        st.header("Task 1: Agenten-Identität")
        st.markdown('<div class="prompt-box"><b>GAIA Prompt:</b> "Ich nehme heute an einem Workshop zum Thema KI im PM teil. Erstelle mir eine Agenten-Identität für diesen Tag. Meine 2 PM-Stärken: [X], Meine 2 PM-Schwächen: [Y]. Generiere: Agentenname, Sichtweise und drei Leitfragen."</div>', unsafe_allow_html=True)
        
        top_c1, top_c2 = st.columns([0.7, 0.3])
        with top_c1: st.subheader("Identität registrieren:")
        with top_c2: save_p = st.button("COMMIT TO DATABASE", use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            a_name = st.selectbox("Identify Real Agent:", AGENT_LIST)
            c_name = st.text_input("Agentenname (von GAIA):")
        with c2:
            a_skill = st.text_input("Sichtweise:")
            a_ques = st.text_area("Deine 3 Leitfragen:")

        if save_p and c_name:
            df_p = get_cached_data("Profiles")
            new_p = pd.DataFrame([{"Agent": a_name, "Codename": c_name, "Skill": a_skill, "Questions": a_ques}])
            if not df_p.empty: df_p = df_p[df_p["Agent"] != a_name] # Überschreibt alten Eintrag des Agents
            updated_p = pd.concat([df_p, new_p], ignore_index=True)
            conn.update(worksheet="Profiles", data=updated_p)
            st.success("DATA COMMITTED")
            force_reload()

        st.markdown("---")
        st.subheader("Aktive Personnel Datenbank")
        p_list = get_cached_data("Profiles")
        if not p_list.empty:
            for idx, r in p_list.iterrows():
                with st.expander(f"👤 {r['Agent']} // Code: {r.get('Codename', '')}"):
                    st.write(f"**Perspektive:** {r.get('Skill', '')}")
                    st.write(f"**Leitfragen:** {r.get('Questions', '')}")
                    # Sicheres Löschen anhand des Namens
                    if st.button("🗑️ DATENSATZ LÖSCHEN", key=f"del_p_{r['Agent']}"):
                        cleaned_df = p_list[p_list["Agent"] != r["Agent"]]
                        conn.update(worksheet="Profiles", data=cleaned_df)
                        force_reload()

    # TAB 2: SABOTAGE (Aufgabe 2)
    with t2:
        top_c1s, top_c2s = st.columns([0.7, 0.3])
        with top_c1s: st.header("Task 2: Die Sabotage-Akte")
        with top_c2s: save_s = st.button("SUBMIT REPORT", use_container_width=True)

        s_thema = st.text_input("Name des Saboteurs:")
        s_details = st.text_area("Details der Sabotage:")

        if save_s and s_thema:
            df_s = get_cached_data("Sabotage")
            new_s = pd.DataFrame([{"Thema": s_thema, "Details": s_details}])
            updated_s = pd.concat([df_s, new_s], ignore_index=True).drop_duplicates(subset=["Thema"])
            conn.update(worksheet="Sabotage", data=updated_s)
            st.success("BREACH REGISTERED")
            force_reload()

        st.markdown("---")
        s_list = get_cached_data("Sabotage")
        for idx, r in s_list.iterrows():
            with st.expander(f"🔴 ALERT: {r['Thema']}"):
                st.write(f"DETAILS: {r['Details']}")
                if st.button("🗑️ AKTE SCHLIEẞEN", key=f"del_s_{r['Thema']}"):
                    cleaned_s = s_list[s_list["Thema"] != r["Thema"]]
                    conn.update(worksheet="Sabotage", data=cleaned_s)
                    force_reload()

    # TAB 3: CREDITS (Aufgabe 3)
    with t3:
        st.header("Task 3: Credit Investment")
        df_coins = get_cached_data("Sabotage")
        if df_coins.empty:
            st.info("Warten auf Sabotage-Berichte aus Task 2...")
        else:
            voter = st.selectbox("Assigning Officer:", AGENT_LIST, key="v_sel")
            spent = 0
            investments = {}
            for item in df_coins["Thema"].unique():
                val = st.slider(f"Investment: {item}", 0, 100, 0, key=f"c_{voter}_{item}")
                investments[item] = val
                spent += val
            
            c_status = "#00FF41" if spent == 100 else "#FF4B4B"
            st.markdown(f"### Gesamt: <span style='color:{c_status};'>{spent} / 100</span>", unsafe_allow_html=True)
            
            if spent == 100:
                if st.button("FINALIZE TRANSACTION"):
                    vote_row = {"Voter": voter, "Total": 100}
                    vote_row.update(investments)
                    df_v = get_cached_data("Votes")
                    if not df_v.empty: df_v = df_v[df_v.get("Voter") != voter]
                    conn.update(worksheet="Votes", data=pd.concat([df_v, pd.DataFrame([vote_row])], ignore_index=True))
                    st.balloons()
                    st.success("TRANSACTION SECURED")
