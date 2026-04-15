import streamlit as st
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import os

# --- 1. PLUGINS & CONFIG ---
st.set_page_config(page_title="PCS Intelligence HQ", page_icon="🚀", layout="wide")

# --- 2. DATA ENGINE (Google Sheets - HOCHLEISTUNGSMODUS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=30)
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
        elif ws_name == "Sally":
            if "Inhalt" not in df.columns: df["Inhalt"] = ""
                
        return df.dropna(how="all")
    except Exception:
        if ws_name == "Profiles": return pd.DataFrame(columns=["Agent", "Codename", "Skill", "Questions"])
        if ws_name == "Sabotage": return pd.DataFrame(columns=["Thema", "Details"])
        if ws_name == "Votes": return pd.DataFrame(columns=["Voter", "Total"])
        if ws_name == "Deep_Dive": return pd.DataFrame(columns=["Titel", "Diskussion"])
        if ws_name == "Sally": return pd.DataFrame(columns=["Inhalt"])
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

# --- JAVASCRIPT CHRONOMETER ---
def render_js_timer(start_time, duration_min):
    html_code = f"""
    <style>
        body {{ margin: 0; background-color: transparent; overflow: hidden; }}
        .timer-display {{
            font-family: 'Courier New', monospace; font-size: 3.2rem; text-align: center;
            border: 2px solid #00FF41; border-radius: 12px; padding: 10px; background: #000;
            margin-bottom: 5px; font-weight: bold; color: #00FF41;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.15); animation: neon-pulse 2s infinite alternate;
        }}
        @keyframes neon-pulse {{
            0% {{ box-shadow: 0 0 10px rgba(0,255,65,0.2), inset 0 0 10px rgba(0,255,65,0.1); }}
            50% {{ box-shadow: 0 0 30px rgba(0,255,65,0.6), inset 0 0 20px rgba(0,255,65,0.3); }}
            100% {{ box-shadow: 0 0 10px rgba(0,255,65,0.2), inset 0 0 10px rgba(0,255,65,0.1); }}
        }}
    </style>
    <div id="js-timer" class="timer-display">--:--</div>
    <script>
        var startTime = {start_time * 1000};
        var durationSec = {duration_min * 60};
        var timerEl = document.getElementById('js-timer');
        function updateTimer() {{
            var now = Date.now();
            var elapsedSec = (now - startTime) / 1000;
            var remSec = Math.max(0, durationSec - elapsedSec);
            var m = Math.floor(remSec / 60);
            var s = Math.floor(remSec % 60);
            var mStr = m < 10 ? "0" + m : m;
            var sStr = s < 10 ? "0" + s : s;
            timerEl.innerHTML = mStr + ":" + sStr;
            if (remSec <= 60) {{
                timerEl.style.color = "#FF0000";
                timerEl.style.borderColor = "#FF0000";
            }} else {{
                timerEl.style.color = "#00FF41";
                timerEl.style.borderColor = "#00FF41";
            }}
        }}
        setInterval(updateTimer, 1000);
        updateTimer();
    </script>
    """
    components.html(html_code, height=95)

# --- 4. PREMIUM TACTICAL CSS ---
st.markdown("""
<style>
    .stApp { background-color: #030303; color: #FFFFFF; font-family: 'Courier New', Courier, monospace; overflow-x: hidden; }
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

    .splash-box {
        text-align: center; margin-top: 5vh; padding: 50px 30px;
        border: 2px solid #00FF41; background-color: #080808; border-radius: 16px; 
        max-width: 800px; margin-left: auto; margin-right: auto; animation: neon-pulse 3s infinite alternate;
    }
    .splash-title {
        font-size: 5rem; font-weight: 900; letter-spacing: 10px; color: #00FF41;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.4); margin-bottom: 20px; line-height: 1.1;
    }
    .splash-subtitle { font-size: 1.2rem; color: #888; letter-spacing: 4px; margin-bottom: 40px; text-transform: uppercase; }
    [data-testid="stImage"] { animation: neon-pulse 4s infinite alternate; border-radius: 12px; }
    .header-container { display: flex; justify-content: space-between; align-items: flex-start; margin-top: -65px; margin-bottom: 35px; }
    .mission-header {
        background-color: #080808; color: #00FF41; padding: 12px 20px; font-weight: 900; 
        font-size: 1.4rem; letter-spacing: 4px; border-radius: 0 0 12px 12px;
        border: 1px solid #00FF41; border-top: none; box-shadow: 0 4px 15px rgba(0,255,65,0.2);
        overflow: hidden; white-space: nowrap; border-right: .15em solid #00FF41;
        animation: typing 2.5s steps(40, end), blink-caret .75s step-end infinite;
    }
    .radar-wrapper { margin-top: 15px; margin-right: 20px; }
    .radar {
        width: 80px; height: 80px; background: radial-gradient(center, rgba(0, 255, 65, 0.2) 0%, rgba(0, 255, 65, 0) 70%);
        border-radius: 50%; border: 2px solid #00FF41; position: relative; overflow: hidden; box-shadow: 0 0 15px rgba(0,255,65,0.4);
    }
    .radar:before {
        content: ' '; display: block; position: absolute; width: 50%; height: 50%; top: 0; left: 0;
        border-right: 2px solid #00FF41; border-bottom: 2px solid #00FF41; border-bottom-right-radius: 100%;
        background: linear-gradient(45deg, rgba(0,0,0,0) 0%, rgba(0,255,65,0.5) 100%);
        transform-origin: 100% 100%; animation: scan 2s linear infinite;
    }
    .radar-grid {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-image: linear-gradient(rgba(0, 255, 65, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 65, 0.3) 1px, transparent 1px);
        background-size: 15px 15px; border-radius: 50%;
    }
    .stButton>button {
        background-color: #080808 !important; color: #00FF41 !important; border: 2px solid #00FF41 !important; 
        height: 3.8rem; font-weight: bold !important; border-radius: 8px !important; transition: all 0.2s ease !important;
        text-transform: uppercase; letter-spacing: 1px; position: relative;
    }
    .stButton>button:hover { 
        background-color: #00FF41 !important; color: #000 !important; box-shadow: 0 0 25px rgba(0,255,65,0.6) !important;
    }
    [data-testid="stSidebar"] { background-color: #080808; border-right: 2px solid #00FF41; }
    label, p, span, div { color: #E0E0E0 !important; font-size: 1.2rem !important; }
    label { color: #00FF41 !important; font-weight: bold !important; font-size: 1.3rem !important; }
    .stTabs [data-baseweb="tab"] { color: #00FF41 !important; border: 1px solid #00FF41 !important; border-bottom: none !important; background: #080808 !important; font-size: 1.2rem !important; border-radius: 8px 8px 0 0 !important; padding: 10px 20px !important; }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !important; color: #000 !important; font-weight: bold !important; }
    .prompt-box { border: 1px dashed #00FF41; padding: 20px; background: #0A0A0A; margin-bottom: 25px; border-radius: 8px; border-left: 5px solid #00FF41; }
</style>
""", unsafe_allow_html=True)

# --- 5. APP INTERFACE ---
if not st.session_state.access_granted:
    st.markdown('<div class="splash-box"><div style="color: #00FF41; font-weight: bold; letter-spacing: 4px; margin-bottom: 15px;">/// SYSTEM LOCKED ///</div>', unsafe_allow_html=True)
    _, col_img, _ = st.columns([1, 1.2, 1])
    with col_img:
        if os.path.exists(ICON_FILENAME): st.image(ICON_FILENAME, use_container_width=True)
    st.markdown('<div class="splash-title" style="margin-top: 20px;">PCS<br>INTELLIGENCE</div><div class="splash-subtitle">Network Authorization Required &bull; Q1 2026</div></div><br>', unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1,1,1])
    with col_mid:
        if st.button("INITIATE UPLINK", use_container_width=True):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()
else:
    st.markdown("""
    <div class="header-container">
        <div class="mission-header">>> DECRYPTING: PCS MISSION CONTROL ...</div>
        <div class="radar-wrapper">
            <div class="radar"><div class="radar-grid"></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        if os.path.exists(ICON_FILENAME): st.image(ICON_FILENAME, use_container_width=True)
        st.markdown("<h3 style='color:#00FF41; text-align:center;'>CHRONOMETER</h3>", unsafe_allow_html=True)
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        render_js_timer(st.session_state.mission_start_time, active_info['duration'])
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#00FF41; text-align:center;'>MISSION LOG</h3>", unsafe_allow_html=True)
        for k, d in MISSION_DATA.items():
            lbl = f"[{k}] {d['name']}"
            if k == st.session_state.active_mission_key: lbl = f"▶ {lbl}"
            if st.sidebar.button(lbl, key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        if st.button("SYNC SYSTEM", use_container_width=True): force_reload()

    # --- TABS (JETZT MIT SALLY DOKU) ---
    t1, t2, t3, t4, t5 = st.tabs(["👤 TEAM", "📂 SABOTAGE", "💰 RANKING", "🤿 DEEP DIVE", "🤖 SALLY DOKU"])

    with t1:
        st.header("Task 1: Agenten-Identität")
        st.markdown('<div class="prompt-box"><b>GAIA Prompt:</b><br>"Ich nehme heute an einem Workshop zum Thema KI im PM teil. Erstelle mir eine Agenten-Identität für diesen Tag..."</div>', unsafe_allow_html=True)
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
            conn.update(worksheet="Profiles", data=pd.concat([df_p[df_p["Agent"] != a_name], new_p], ignore_index=True))
            force_reload()

    with t2:
        top_c1s, top_c2s = st.columns([0.7, 0.3])
        with top_c1s: st.header("Task 2: Die Sabotage-Akte")
        with top_c2s: save_s = st.button("SUBMIT REPORT", use_container_width=True)
        s_thema = st.text_input("Titel:")
        s_details = st.text_area("Details der Sabotage:")
        if save_s and s_thema:
            df_s = get_cached_data("Sabotage")
            new_s = pd.DataFrame([{"Thema": s_thema, "Details": s_details}])
            conn.update(worksheet="Sabotage", data=pd.concat([df_s, new_s], ignore_index=True).drop_duplicates(subset=["Thema"]))
            force_reload()

    with t3:
        st.header("Live-Ranking der Bedrohungen")
        df_v_live = get_cached_data("Votes")
        if not df_v_live.empty:
            ranking_data = df_v_live.drop(columns=["Voter", "Total"], errors='ignore').sum().reset_index()
            ranking_data.columns = ["Sabotage-Thema", "Investierte Coins"]
            st.bar_chart(ranking_data.set_index("Sabotage-Thema"), use_container_width=True)
        
        st.markdown("---")
        st.subheader("Task 3: Coins investieren")
        df_coins = get_cached_data("Sabotage")
        if not df_coins.empty:
            voter = st.selectbox("Assigning Officer:", AGENT_LIST, key="v_sel")
            spent = 0
            investments = {}
            for item in df_coins["Thema"].unique():
                val = st.slider(f"Investment: {item}", 0, 100, 0, key=f"c_{voter}_{item}")
                investments[item] = val
                spent += val
            st.markdown(f"### Budget-Status: {spent} / 100")
            if st.button("FINALIZE TRANSACTION", use_container_width=True, disabled=(spent != 100)):
                vote_row = {"Voter": voter, "Total": 100}
                vote_row.update(investments)
                df_v = get_cached_data("Votes")
                conn.update(worksheet="Votes", data=pd.concat([df_v[df_v["Voter"] != voter], pd.DataFrame([vote_row])], ignore_index=True))
                force_reload()

    with t4:
        st.header("Live-Diskussion: Deep Dive")
        df_sabotage_dd = get_cached_data("Sabotage")
        df_deepdive = get_cached_data("Deep_Dive")
        for idx, row in df_sabotage_dd.iterrows():
            with st.expander(f"🤿 AKTE: {row['Thema']}"):
                notes = df_deepdive[df_deepdive["Titel"] == row['Thema']]["Diskussion"].iloc[0] if not df_deepdive.empty and row['Thema'] in df_deepdive["Titel"].values else ""
                diskussion_text = st.text_area("Protokoll:", value=notes, key=f"dd_{row['Thema']}")
                if st.button("💾 SPEICHERN", key=f"save_{row['Thema']}"):
                    new_dd = pd.DataFrame([{"Titel": row['Thema'], "Diskussion": diskussion_text}])
                    conn.update(worksheet="Deep_Dive", data=pd.concat([df_deepdive[df_deepdive["Titel"] != row['Thema']], new_dd], ignore_index=True))
                    force_reload()

    # --- NEU: TAB 5 SALLY DOKU ---
    with t5:
        st.header("🤖 Sally Intelligence Protokoll")
        st.write("Fügen Sie hier das Protokoll von Sally (KI-Protokollant) ein.")
        df_sally = get_cached_data("Sally")
        existing_sally = df_sally["Inhalt"].iloc[0] if not df_sally.empty else ""
        sally_content = st.text_area("Intelligence Briefing / Meeting Protokoll:", value=existing_sally, height=500, key="sally_text")
        if st.button("💾 SALLY PROTOKOLL SICHERN", use_container_width=True):
            conn.update(worksheet="Sally", data=pd.DataFrame([{"Inhalt": sally_content}]))
            force_reload()
