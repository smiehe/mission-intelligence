# TAB 3: RANKING
    with t3:
        st.header("Live-Ranking der Bedrohungen")
        df_v_live = get_cached_data("Votes")
        
        # NEU: Wir prüfen, ob es überhaupt schon Spalten für Themen gibt (alles außer Voter/Total)
        vote_cols = [c for c in df_v_live.columns if c not in ["Voter", "Total"]]
        
        if df_v_live.empty or not vote_cols:
            # Custom Info-Box, falls noch keine echten Abstimmungsdaten da sind
            st.markdown("""
            <div style="border: 1px dashed #FF4B4B; padding: 20px; background: rgba(255, 75, 75, 0.05); border-radius: 8px; border-left: 5px solid #FF4B4B; text-align: center; margin-bottom: 20px;">
                <span style="color: #FF4B4B; font-weight: bold; font-family: 'Courier New', monospace;">[!] KEINE DATEN VORHANDEN. SYSTEM WARTET AUF COIN-TRANSAKTIONEN.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 1. Daten aufbereiten (nur wenn wirklich Themen da sind!)
            ranking_data = df_v_live[vote_cols].sum().reset_index()
            ranking_data.columns = ["Thema", "Coins"]
            ranking_data = ranking_data.sort_values(by="Coins", ascending=False)
            
            # Höchstwert für die Prozentrechnung ermitteln (für die Balkenlänge)
            max_coins = ranking_data["Coins"].max()
            if max_coins == 0: max_coins = 1 # Verhindert Division durch 0
            
            # 2. Unser massgeschneidertes Cyber-Balkendiagramm generieren
            html_bars = "<div style='margin-bottom: 40px; padding: 20px; border: 1px solid #111; background: #050505; border-radius: 12px; box-shadow: inset 0 0 20px rgba(0,255,65,0.05);'>"
            
            for idx, row in ranking_data.iterrows():
                thema = row["Thema"]
                coins = int(row["Coins"])
                percentage = int((coins / max_coins) * 100)
                
                # Jeder Balken bekommt einen Text und eine animierte Leiste
                html_bars += f"""
                <div style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #FFF; font-weight: bold; font-family: 'Courier New', monospace; font-size: 1.1rem; text-transform: uppercase;">> {thema}</span>
                        <span style="color: #00FF41; font-weight: bold; font-family: 'Courier New', monospace; font-size: 1.2rem; text-shadow: 0 0 5px rgba(0,255,65,0.5);">{coins} COINS</span>
                    </div>
                    <div style="width: 100%; background-color: #0a0a0a; border: 1px solid #222; border-radius: 4px; height: 28px; overflow: hidden; box-shadow: inset 0 0 10px rgba(0,0,0,1);">
                        <div style="width: {percentage}%; background: linear-gradient(90deg, rgba(0,180,45,1) 0%, rgba(0,255,65,1) 100%); height: 100%; border-radius: 2px; box-shadow: 0 0 15px rgba(0, 255, 65, 0.8); animation: growBar 1.5s ease-out forwards;"></div>
                    </div>
                </div>
                """
            html_bars += "</div>"
            st.markdown(html_bars, unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader("Task 3: Coins investieren")
        df_coins = get_cached_data("Sabotage")
        
        if df_coins.empty:
            st.warning("Warten auf Sabotage-Berichte aus Task 2...")
        else:
            voter = st.selectbox("Assigning Officer:", AGENT_LIST, key="v_sel")
            spent = 0
            investments = {}
            for item in df_coins["Thema"].unique():
                val = st.slider(f"Investment: {item}", 0, 100, 0, key=f"c_{voter}_{item}")
                investments[item] = val
                spent += val
            
            c_status = "#00FF41" if spent == 100 else "#FF4B4B"
            st.markdown(f"### Budget-Status: <span style='color:{c_status}; font-weight:bold;'>{spent} / 100 Coins</span>", unsafe_allow_html=True)
            
            # Der Button ist IMMER sichtbar, aber ausgegraut, wenn man nicht bei exakt 100 Coins ist
            if st.button("FINALIZE TRANSACTION", use_container_width=True, disabled=(spent != 100)):
                st.toast("💰 Transaktion wird validiert...", icon="⏳")
                vote_row = {"Voter": voter, "Total": 100}
                vote_row.update(investments)
                df_v = get_cached_data("Votes")
                if not df_v.empty: df_v = df_v[df_v.get("Voter") != voter]
                
                conn.update(worksheet="Votes", data=pd.concat([df_v, pd.DataFrame([vote_row])], ignore_index=True))
                st.cache_data.clear()
                st.balloons()
                st.success("TRANSACTION SECURED")
                time.sleep(1.5)
                st.rerun()
