import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# Autorefresh für den Live-Timer laden
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# 1. Basis-Konfiguration
st.set_page_config(
    page_title="Mission: Intelligence HQ", 
    page_icon="🕵️‍♂️", 
    layout="wide"
)

# 2. Zentralspeicher (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

def safe_read(ws_name):
    try:
        return conn.read(worksheet=ws_name, ttl="0")
    except Exception:
        if ws_name == "Profiles":
            return pd.DataFrame(columns=["Agent", "Codename", "Skill", "Avatar"])
        if ws_name == "Sabotage":
            return pd.DataFrame(columns=["Thema", "Details"])
        return pd.DataFrame()

# 3. Konstanten & Missionen
AGENT_LIST = ["Sören", "Laura", "Tamara", "Janina", "Christin", "Leo", "Claudine"]
BOSS_LIST = {
    "The Awakened One": "🦅",
    "Time Eater": "⏳",
    "Donu & Deca": "💎",
    "The Corrupt Heart": "❤️",
    "The Champ": "🏆"
}
MISSION_DATA = {
    "09:00": {"name": "Operation: Agent Profile", "duration": 30},
    "09:30": {"name": "The Intelligence Briefing (Nico)", "duration": 90},
    "11:15": {"name": "The Deep-Dive Mission", "duration": 90},
    "12:45": {"name": "Field Rations (Lunch)", "duration": 60},
    "13:45": {"name": "Final Briefing (Wrap-up)", "duration": 30},
    "15:30": {"name": "Field Operation (Museum)", "duration": 120},
    "17:30": {"name": "Safe House Drinks & Dinner", "duration": 180}
}

# 4. Session State (Das Gedächtnis der App)
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'active_mission_key' not in st.session_state:
    st.session_state.active_mission_key = "09:00"
if 'mission_start_time' not in st.session_state:
    st.session_state.mission_start_time = time.time()
if 'selected_boss' not in st.session_state:
    st.session_state.selected_boss = "The Awakened One"

# 5. CSS Styling (Sicher verpackt in eine Variable)
style_css = """
<style>
    .stApp { background-color: #000000; color: #FFFFFF; font-size: 1.2rem; }
    
    .splash-box {
        text-align: center; margin-top: 5%; padding: 50px;
        border: 4px solid #00FF41; background-color: #050505;
        box-shadow: 0 0 40px #00FF41;
    }
    
    [data-testid="stSidebar"] { 
        background-color: #050505; 
        border-right: 3px solid #00FF41; 
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] b, 
    [data-testid="stSidebar"] span {
        color: #FFFFFF !important; font-size: 1.2rem !important; opacity: 1 !important;
    }

    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        color: #00FF41; font-size: 3.2rem; text-align: center;
        padding: 15px; border: 3px solid #00FF41; background: #000;
        font-weight: bold; text-shadow: 0 0 10px #00FF41;
    }

    .mission-header {
        width: 100%; background: #00FF41; color: #000000; padding: 15px 0;
        text-align: center; font-weight: bold; letter-spacing: 5px;
        margin-top: -70px; margin-bottom: 30px; font-size: 1.3rem;
    }

    .stButton>button { 
        background-color: #00FF41 !important; color: #000000 !important; 
        font-weight: bold !important; font-size: 1.2rem !important; 
        height: 3.8rem; border: none !important;
    }
    .stButton>button:hover { background-color: #FFFFFF !important; }

    .agent-card { 
        border: 2px solid #00FF41; padding: 20px; background: #111; 
        border-radius: 12px; margin-bottom: 15px; 
    }
    .agent-card b { color: #00FF41; font-size: 1.6rem; }
    
    label { color: #00FF41 !important; font-size: 1.4rem !important; }
    input, textarea, select { 
        background-color: #000000 !important; color: #FFFFFF !important; 
        border: 2px solid #00FF41 !important; font-size: 1.2rem !important;
    }

    .stTabs [data-baseweb="tab"] { 
        color: #00FF41 !important; border: 1px solid #00FF41 !important; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #00FF41 !important; color: #000000 !important; 
    }
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# 6. Timer-Start
if st.session_state.access_granted and st_autorefresh:
    st_autorefresh(interval=2000, key="global_tick")

# 7. Startbildschirm (Login & Character Select)
if not st.session_state.access_granted:
    st.markdown('<div class="splash-box"><h1 style="color:#00FF41; font-size:4.5rem;">MISSION:<br>INTELLIGENCE</h1><p style="color:#FFF; font-size:1.6rem;">PCS DIVISION | Q1 2026</p></div>', unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1,2,1])
    with col_mid:
        st.write("")
        st.markdown("<p style='text-align:center; color:#00FF41; font-weight:bold;'>WÄHLE DEINEN BOSS-AVATAR:</p>", unsafe_allow_html=True)
        
        # Sicherer Radio-Button
        choice = st.radio(
            "Bosse:", 
            options=list(BOSS_LIST.keys()), 
            horizontal=True, 
            label_visibility="collapsed"
        )
        st.session_state.selected_boss = choice
        
        icon = BOSS_LIST[st.session_state.selected_boss]
        st.markdown(f"<div style='text-align:center; font-size:9rem;'>{icon}</div>", unsafe_allow_html=True)
        
        if st.button("ENTER HQ / IDENTITÄT BESTÄTIGEN"):
            st.session_state.access_granted = True
            st.session_state.mission_start_time = time.time()
            st.rerun()

# 8. Haupt-HQ
else:
    st.markdown('<div class="mission-header">NETWORK ACCESS GRANTED // BOSS MODE: ACTIVE</div>', unsafe_allow_html=True)

    # SIDEBAR
    with st.sidebar:
        st.markdown("### ⏳ MISSION CLOCK")
        active_info = MISSION_DATA[st.session_state.active_mission_key]
        rem_sec = max(0, (active_info['duration'] * 60) - (time.time() - st.session_state.mission_start_time))
        m, s = divmod(int(rem_sec), 60)
        t_color = "#00FF41" if rem_sec > 300 else "#FF4B4B"
        st.markdown(f'<div class="timer-display" style="color:{t_color}; border-color:{t_color};">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.header("📍 EINSATZPLAN")
        for k, d in MISSION_DATA.items():
            lbl = f"{k} | {d['name']}"
            if k == st.session_state.active_mission_key: lbl = f"▶ {lbl}"
            if st.button(lbl, key=f"sb_{k}"):
                st.session_state.active_mission_key = k
                st.session_state.mission_start_time = time.time()
                st.rerun()
        
        st.markdown("---")
        st.write("**TEAM IM EINSATZ:**")
        for agent in AGENT_LIST:
            st.write(f"• {agent}")

    # HAUPTBEREICH (TABS)
    st.title(f"🕵️‍♂️ HQ: {active_info['name']}")
    t1, t2, t3 = st.tabs(["👤 PCS-PROFILE", "📂 SABOTAGE-AKTE", "💰 COIN-INVESTMENT"])

    with t1:
        st.header("Operation: Agent Profile")
        with st.form("p_form"):
            a_name = st.selectbox("Wer bist du?", AGENT_LIST)
            c_name = st.text_input("KI-Codename:")
            a_skill = st.text_input("KI-Skill:")
            cur_icon = BOSS_LIST[st.session_state.selected_boss]
            st.info(f"Dein Avatar: {st.session_state.selected_boss} {cur_icon}")
            
            if st.form_submit_button("PROFIL SPEICHERN"):
                if c_name and a_skill:
                    new_p = pd.DataFrame([{"Agent": a_name, "Codename": c_name, "Skill": a_skill, "Avatar": cur_icon}])
                    conn.update(worksheet="Profiles", data=pd.concat([safe_read("Profiles"), new_p], ignore_index=True))
                    st.success("Profil gesichert!")
                    time.sleep(1)
                    st.rerun()

        st.subheader("Aktive Boss-Agenten")
        p_df = safe_read("Profiles").dropna(subset=["Agent"])
        if not p_df.empty:
            c_grid = st.columns(2)
            for idx, row in p_df.iterrows():
                with c_grid[idx % 2]:
                    av = row["Avatar"] if "Avatar" in row and str(row["Avatar"]) != "nan" else "🕵️‍♂️"
                    st.markdown(f'<div class="agent-card"><div style="font-size:4rem; float:right;">{av}</div><b>{row["Agent"]}</b><br><span style="color:#FFF;">CODE:</span> {row["Codename"]}<br><span style="color:#FFF;">SKILL:</span> {row["Skill"]}</div>', unsafe_allow_html=True)
                    if st.button(f"🗑️ LÖSCHEN: {row['Agent']}", key=f"del_{idx}"):
                        conn.update(worksheet="Profiles", data=safe_read("Profiles").drop(idx))
                        st.rerun()

    with t2:
        st.header("Die Sabotage-Akte")
        with st.form("s_form"):
            s_thema = st.text_input("Thema:")
            s_desc = st.text_area("Details:")
            if st.form_submit_button("SENDEN"):
                if s_thema:
                    new_s = pd.DataFrame([{"Thema": s_thema, "Details": s_desc}])
                    conn.update(worksheet="Sabotage", data=pd.concat([safe_read("Sabotage"), new_s], ignore_index=True))
                    st.success("Archiviert.")
                    time.sleep(1)
                    st.rerun()

    with t3:
        st.header("💰 Operation: Golden Coin")
        df_s = safe_read("Sabotage").dropna(subset=["Thema"])
        if df_s.empty:
            st.info("Warte auf Sabotage-Themen...")
        else:
            v_agent = st.selectbox("Wer investiert?", AGENT_LIST, key="v_sel")
            t_spent = 0
            v_dict = {}
            for item in df_s["Thema"].unique():
                v_dict[item] = st.slider(f"INVEST: {item}", 0, 100, 0, key=f"sl_{v_agent}_{item}")
                t_spent += v_dict[item]
            
            st.markdown(f"## Status {v_agent}: {t_spent} / 100 Coins")
            if t_spent == 100:
                if st.button(f"VOTING FÜR {v_agent} SPEICHERN"):
                    st.balloons()
