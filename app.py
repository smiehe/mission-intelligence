import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import os

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
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        if df is None: df = pd.DataFrame()
        
        if ws_name == "Profiles":
            for col in ["Agent", "Codename", "Skill", "Questions"]:
                if col not in df.columns: df[col] = ""
        elif ws_name == "Sabotage":
            for col in ["Thema", "Details"]:
                if col not in df.columns: df[col] = ""
        elif ws_name == "Votes":
            for col in ["Voter", "Total"]:
                if col not in df.columns: df[col] = ""
        elif ws_name == "Deep_Dive":
            for col in ["Titel", "Diskussion"]:
                if col not in df.columns: df[col] = ""
                
        return df.dropna(how="all")
    except Exception:
        if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill", "Questions"])
        if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
        if ws_name == "Votes": return pd.DataFrame(columns=["Voter", "Total"])
        if ws_name == "Deep_Dive": return pd.DataFrame(columns=["Titel", "Diskussion"])
        return pd.DataFrame()

def force_reload():
    st.cache_data.clear()
    st.rerun()

# --- 3. MISSION SETUP ---
AGENT_LIST = ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"]

MISSION_DATA = {
    "09:00": {"name": "Mission Warmup", "duration": 30},
    "09:30": {"name": "The intelligence Briefing with Nico", "duration": 90},
    "11:15": {"name": "The Deep-Dive Mission", "duration": 90},
    "12:45": {"name": "Field Rations (Lunch)", "duration": 45},
    "13:30": {"name": "Final Briefing (Wrap-up)", "duration": 45},
    "15:30": {"name": "Field Operation", "duration": 120},
    "17:30": {"name": "Safe House Drinks & Dinner", "duration": 180}
}

ICON_FILENAME = "icon.png"

if 'access_granted' not in st.session_state: st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state: st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state: st.session_state.mission_start_time = time.time()

# --- 4. PREMIUM TACTICAL CSS (MIT NEUEN EFFEKTEN) ---
st.markdown("""
<style>
    /* Basis Layout */
    .stApp { background-color: #030303; color: #FFFFFF; font-family: 'Courier New', Courier, monospace; overflow-x: hidden; }
    
    /* ANIMATIONEN */
    @keyframes neon-pulse {
        0% { box-shadow: 0 0 10px rgba(0,255,65,0.2), inset 0 0 10px rgba(0,255,65,0.1); }
        50% { box-shadow: 0 0 30px rgba(0,255,65,0.6), inset 0 0 20px rgba(0,255,65,0.3); }
        100% { box-shadow: 0 0 10px rgba(0,255,65,0.2), inset 0 0 10px rgba(0,255,65,0.1); }
    }
    
    @keyframes glitch-anim {
        0% { clip-path: inset(10% 0 80% 0); transform: translate(-2px, 2px); }
        20% { clip-path: inset(80% 0 10% 0); transform: translate(2px, -2px); }
        40% { clip-path: inset(30% 0 50% 0); transform: translate(-2px, 2px); }
        60% { clip-path: inset(90% 0 5% 0); transform: translate(2px, -2px); }
        80% { clip-path: inset(5% 0 80% 0); transform: translate(-2px, 2px); }
        100% { clip-path: inset(40% 0 40% 0); transform: translate(0); }
    }
    
    @keyframes typing { from { width: 0 } to { width: 100% } }
    @keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #00FF41; } }

    @keyframes scan { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

    /* STARTBILDSCHIRM & WAPPEN (Neon Pulse) */
    .splash-box {
        text-align: center; margin-top: 5vh; padding: 50px 30px;
        border: 2px solid #00FF41; background-color: #080808;
        border-radius: 16px; max-width: 800px; margin-left: auto; margin-right: auto;
        animation: neon-pulse 3s infinite alternate; /* GLOW EFFEKT */
    }
    .splash-title {
        font-size: 5rem; font-weight: 900; letter-spacing: 10px; color: #00FF41;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.4); margin-bottom: 20px; line-height: 1.1;
    }
    .splash-subtitle { font-size: 1.2rem; color: #888; letter-spacing: 4px; margin-bottom: 40px; text-transform: uppercase; }

    /* Wappen Glow */
    [data-testid="stImage"] { animation: neon-pulse 4s infinite alternate; border-radius: 12px; }

    /* TYPEWRITER HEADER */
    .mission-header {
        width: fit-content; max-width: 100%; background-color: #080808; color: #00FF41; 
        padding: 12px 20px; font-weight: 900; font-size: 1.4rem; letter-spacing: 4px; 
        margin-top: -65px; margin-bottom: 35px; border-radius: 0 0 12px 12px;
        border: 1px solid #00FF41; border-top: none;
        box-shadow: 0 4px 15px rgba(0,255,65,0.2);
        
        /* Typewriter Settings */
        overflow: hidden; white-space: nowrap; border-right: .15em solid #00FF41;
        animation: typing 2.5s steps(40, end), blink-caret .75s step-end infinite;
    }

    /* CSS RADAR ANIMATION (Lottie Alternative) */
    .radar-container { display: flex; justify-content: center; margin: 20px 0; }
    .radar {
        width: 120px; height: 120px;
        background: radial-gradient(center, rgba(0, 255, 65, 0.2) 0%, rgba(0, 255, 65, 0) 70%);
        border-radius: 50%; border: 2px solid #00FF41; position: relative; overflow: hidden;
        box-shadow: 0 0 20px rgba(0,255,65,0.4);
    }
    .radar:before {
        content: ' '; display: block; position: absolute;
        width: 50%; height: 50%; top: 0; left: 0;
        border-right: 2px solid #00FF41; border-bottom: 2px solid #00FF41;
        border-bottom-right-radius: 100%;
        background: linear-gradient(45deg, rgba(0,0,0,0) 0%, rgba(0,255,65,0.5) 100%);
        transform-origin: 100% 100%; animation: scan 2s linear infinite;
    }
    .radar-grid {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            linear-gradient(rgba(0, 255, 65, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 65, 0.3) 1px, transparent 1px);
        background-size: 20px 20px; border-radius: 50%;
    }

    /* BUTTONS & GLITCH HOVER */
    .stButton>button {
        background-color: #080808 !important; color: #00FF41 !important;
        border: 2px solid #00FF41 !important; height: 3.8rem; font-weight: bold !important;
        border-radius: 8px !important; transition: all 0.2s ease !important;
        text-transform: uppercase; letter-spacing: 1px; position: relative;
    }
    .stButton>button:hover { 
        background-color: #00FF41 !important; color: #000 !important; 
        box-shadow: 0 0 25px rgba(0,255,65,0.6) !important;
        /* Glitch Trigger */
        animation: glitch-skew 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
    }
    @keyframes glitch-skew {
        0% { transform: skew(0deg); }
        20% { transform: skew(-10deg); }
        40% { transform: skew(10deg); }
        60% { transform: skew(-5deg); }
        80% { transform: skew(5deg); }
        100% { transform: skew(0deg); }
    }

    /* Timer Pulse */
    .timer-display {
        font-family: 'Courier New', monospace; color: #00FF41; font-size: 3.8rem; text-align: center;
        border: 2px solid #00FF41; border-radius: 12px; padding: 15px; background: #000;
        animation: neon-pulse 2s infinite alternate; /* GLOW EFFEKT */
        margin-bottom: 25px; font-weight: bold;
    }

    /* Sidebar, Tabs & Inputs - Gleiches Design wie zuvor */
    [data-testid="stSidebar"] { background-color: #080808; border-right: 2px solid #00FF41; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; font-size: 1.1rem !important; }
    
    label, p, span, div { color: #E0E0E0 !important; font-size: 1.2rem !important; }
    label { color: #00FF41 !important; font-weight: bold !important; font-size: 1.3rem !important; margin-bottom: 8px; }
    
    input, textarea { 
        background-color: #050505 !important; color: #FFF !important; 
        border: 1px solid #00FF41 !important; border-radius: 6px !important;
        font-size: 1.2rem !important; padding: 10px !important;
    }
    input:focus, textarea:focus { box-shadow: 0 0 15px rgba(0,255,65,0.5) !important; outline: none !important; }

    /* Dropdown Fix */
    div[data-baseweb="select"] > div { background-color: #00FF41 !important; border: none !important; border-radius: 6px !important; cursor: pointer !important; }
    div[data-baseweb="select"] input { caret-color: transparent !important; pointer-events: none !important; }
    div[data-baseweb="select"] span { color: #000000 !important; font-weight: 900 !important; }
    div[data-baseweb="select"] svg { fill: #000000 !important; }
    div[data-baseweb="popover"], ul[role="listbox"] { background-color: #080808 !important; border: 1px solid #00FF41 !important; border-radius: 6px !important; }
    li[role="option"] { background-color: #080808 !important; color: #00FF41 !important; font-weight: bold !important; border-bottom: 1px solid #111; padding: 12px !important; }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #00FF41 !important; color: #000000 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        color: #00FF41 !important; border: 1px solid #00FF41 !important; border-bottom: none !important;
        background: #080808 !important; font-size: 1.2rem !important; border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important; transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !important; color: #000 !important; font-weight: bold !important; }
    
    .prompt-box { border: 1px dashed #00FF41; padding: 20px; background: #0A0A0A; margin-bottom: 25px; border-radius: 8px; border-left: 5px solid #00FF41; }
    [data-testid="stExpander"] { border: 1px solid #00FF41 !important; border-radius: 8px !important; background: #080808 !important; margin-bottom: 15px; }
    [data-testid="stExpander"] summary p { color: #00FF41 !important; font-weight: bold !important; font-size: 1.3rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 5. APP INTERFACE ---
if not st.session_state.access_granted:
    # STARTBILDSCHIRM
    st.markdown("""
        <div class="splash-box">
            <div style="color: #00FF41; font-weight: bold; letter-spacing: 4px; margin-bottom: 15px;">/// SYSTEM LOCKED ///</div>
    """, unsafe_allow_html=True)
    
    _, col_img, _ = st.columns([1, 1.2, 1])
    with col_img:
        if os.path.exists(ICON_FILENAME):
            st.image(ICON_FILENAME, use_container_width=True)
            
    st.markdown("""
            <div class="splash-title" style="margin-top: 20px;">PCS<br>INTELLIGENCE</div>
            <div class="splash-subtitle">Network Authorization Required &nbsp;&bull;&nbsp; Q1 2026</div>
        </div><br>
    """, unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1,1,1])
    with col_mid:
        if st.button("INITIATE UPLINK", use_container_width=True):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    # HAUPTMENÜ & TIMER
    if st_autorefresh:
        st_autorefresh(interval=1000, key="timer_tick")

    # TYPEWRITER EFFEKT HIER
    st.markdown('<div class="mission-header">>> DECRYPTING: PCS MISSION CONTROL ...</div>', unsafe_allow_html=True)

    # -- SIDEBAR --
    with st.sidebar:
        
        # WAPPEN IN DER SIDEBAR
        _, col_logo, _ = st.columns([1, 1.5, 1]) 
        with col_logo:
            if os.path.exists(ICON_FILENAME):
                st.image(ICON_FILENAME, use_container_width=True)
        
        # NEU: LOTTIE-ALTERNATIVE (CSS RADAR)
        st.markdown("""
            <div class="radar-container">
                <div class="radar"><div class="radar-grid"></div></div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='color:#00FF41; text-align:center;'>CHRONOMETER</h3>", unsafe_allow_html=True)
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
        if st.button("SYNC SYSTEM", use_container_width=True): force_reload()

    # -- TABS --
    t1, t2, t3, t4 = st.tabs(["👤 TEAM", "📂 SABOTAGE", "💰 RANKING", "🤿 DEEP DIVE"])

    # TAB 1: TEAM
    with t1:
        st.header("Task 1: Agenten-Identität")
        st.markdown('<div class="prompt-box"><b>GAIA Prompt:</b><br>"Ich nehme heute an einem Workshop zum Thema KI im PM teil. Erstelle mir eine Agenten-Identität für diesen Tag. Meine 2 PM-Stärken: [X], Meine 2 PM-Schwächen: [Y]. Generiere: Agentenname, Sichtweise und drei Leitfragen."</div>', unsafe_allow_html=True)
        
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
            if not df_p.empty: df_p = df_p[df_p["Agent"] != a_name] 
            updated_p = pd.concat([df_p, new_p], ignore_index=True)
            conn.update(worksheet="Profiles", data=updated_p)
            st.success("DATA COMMITTED")
            force_reload()

        st.markdown("---")
        st.subheader("Aktive Team Datenbank")
        p_list = get_cached_data("Profiles")
        if not p_list.empty:
            for idx, r in p_list.iterrows():
                with st.expander(f"👤 {r['Agent']} // Code: {r.get('Codename', '')}"):
                    st.write(f"**Perspektive:** {r.get('Skill', '')}")
                    st.write(f"**Leitfragen:** {r.get('Questions', '')}")
                    if st.button("🗑️ DATENSATZ LÖSCHEN", key=f"del_p_{r['Agent']}"):
                        cleaned_df = p_list[p_list["Agent"] != r["Agent"]]
                        conn.update(worksheet="Profiles", data=cleaned_df)
                        force_reload()

    # TAB 2: SABOTAGE
    with t2:
        top_c1s, top_c2s = st.columns([0.7, 0.3])
        with top_c1s: st.header("Task 2: Die Sabotage-Akte")
        with top_c2s: save_s = st.button("SUBMIT REPORT", use_container_width=True)

        s_thema = st.text_input("Titel:")
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

    # TAB 3: RANKING
    with t3:
        st.header("Task 3: Ranking")
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
            st.markdown(f"### Gesamt: <span style='color:{c_status}; font-weight:bold;'>{spent} / 100</span>", unsafe_allow_html=True)
            
            if spent == 100:
                if st.button("FINALIZE TRANSACTION", use_container_width=True):
                    vote_row = {"Voter": voter, "Total": 100}
                    vote_row.update(investments)
                    df_v = get_cached_data("Votes")
                    if not df_v.empty: df_v = df_v[df_v.get("Voter") != voter]
                    conn.update(worksheet="Votes", data=pd.concat([df_v, pd.DataFrame([vote_row])], ignore_index=True))
                    st.balloons()
                    st.success("TRANSACTION SECURED")

    # TAB 4: DEEP DIVE
    with t4:
        st.header("Live-Diskussion: Deep Dive")
        st.write("Hier dokumentieren wir die Lösungsansätze zu den identifizierten Sabotage-Akten.")
        st.markdown("---")
        
        df_sabotage_dd = get_cached_data("Sabotage")
        df_deepdive = get_cached_data("Deep_Dive")
        
        if df_sabotage_dd.empty:
            st.info("Keine aktiven Sabotage-Akten für einen Deep Dive verfügbar.")
        else:
            for idx, row in df_sabotage_dd.iterrows():
                thema = row["Thema"]
                details = row["Details"]
                
                existing_notes = ""
                if not df_deepdive.empty and thema in df_deepdive["Titel"].values:
                    existing_notes = df_deepdive[df_deepdive["Titel"] == thema]["Diskussion"].iloc[0]
                
                with st.expander(f"🤿 AKTE: {thema}"):
                    st.write(f"**Ursprüngliches Problem:** {details}")
                    st.write("")
                    
                    diskussion_text = st.text_area("Diskussions-Protokoll (Live):", value=existing_notes, height=150, key=f"dd_text_{thema}")
                    
                    if st.button("💾 NOTIZEN SPEICHERN", key=f"dd_save_{thema}"):
                        new_dd_row = pd.DataFrame([{"Titel": thema, "Diskussion": diskussion_text}])
                        
                        df_current_dd = get_cached_data("Deep_Dive")
                        if not df_current_dd.empty:
                            df_current_dd = df_current_dd[df_current_dd["Titel"] != thema]
                            
                        updated_dd = pd.concat([df_current_dd, new_dd_row], ignore_index=True)
                        conn.update(worksheet="Deep_Dive", data=updated_dd)
                        
                        st.success(f"Notizen für '{thema}' erfolgreich im Archiv gesichert!")
                        time.sleep(1)
                        force_reload()
