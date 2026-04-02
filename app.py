import streamlit as st

# Grundkonfiguration
st.set_page_config(page_title="Mission: Intelligence HQ", page_icon="🕵️‍♂️", layout="wide")

# --- DESIGN & STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #00FF41; }
    .main-header {
        font-family: 'Courier New', Courier, monospace;
        text-align: center;
        padding: 20px;
        border-bottom: 2px solid #00FF41;
        text-shadow: 0 0 10px #00FF41;
    }
    .agent-card {
        background-color: #1A1C23;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00FF41;
        margin-bottom: 10px;
    }
    /* Buttons */
    .stButton>button {
        background-color: #00FF41 !important;
        color: #0B0E14 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="main-header"><h1>🕵️‍♂️ MISSION: INTELLIGENCE</h1><p>Quarterday Q1 2026 - Project Management Division</p></div>', unsafe_allow_html=True)

# --- SIDEBAR AGENDA ---
st.sidebar.header("📍 Einsatzplan")
agenda = {
    "09:00": "Operation: Agent Profile (Warmup)",
    "09:30": "The Intelligence Briefing (Niko)",
    "11:15": "The Deep-Dive Mission (Workshop)",
    "12:45": "Field Rations (Lunch)",
    "15:30": "Field Operation (Museum)",
    "17:30": "Safe House (Dinner)"
}
for zeit, event in agenda.items():
    st.sidebar.write(f"**{zeit}** : {event}")

# --- TABS FÜR DIE INTERAKTION ---
tab1, tab2, tab3 = st.tabs(["👤 Agenten-Check-in", "📂 Sabotage-Akte", "💡 KI-Missionen"])

with tab1:
    st.header("Operation: Agent Profile")
    st.info("Nutze eine KI deiner Wahl, um deinen Agenten-Codenamen und eine Spezialfähigkeit basierend auf deinen PM-Stärken zu erstellen!")
    
    with st.form("checkin"):
        name = st.selectbox("Echter Name:", ["---", "Claudine", "Sören", "Laura", "Tamara", "Janina", "Christin", "Leo"])
        codename = st.text_input("Dein KI-generierter Codename:")
        skill = st.text_input("Deine KI-Spezialfähigkeit:")
        
        if st.form_submit_button("Profil im HQ aktivieren"):
            if name != "---" and codename:
                st.success(f"Agent '{codename}' ({name}) ist jetzt online.")
                st.balloons()
            else:
                st.error("Bitte wähle deinen Namen und gib deinen Codenamen ein!")

with tab2:
    st.header("Die Sabotage-Akte")
    st.write("Welche Prozesse fühlen sich wie 'absichtliche Sabotage' an?")
    
    with st.form("sabotage"):
        prozess = st.text_input("Name des Sabotage-Prozesses:")
        beschreibung = st.text_area("Warum hält uns das auf?")
        schwere = st.slider("Schweregrad der Behinderung", 1, 10, 5)
        
        if st.form_submit_button("Akte verschlüsselt senden"):
            st.warning("Akte gespeichert. Niko wird diese in der Intelligence Session analysieren.")

with tab3:
    st.header("Deep-Dive: KI-Konzepte")
    st.info("Dieser Bereich wird nach dem Intelligence Briefing für die Workshop-Ergebnisse freigeschaltet.")
