import streamlit as st
import requests
import pandas as pd
import numpy as np
import io
from datetime import datetime

# --- CONFIGURATION ---
FOOTBALL_KEY = "dac17517d43d471e94d2b2484ef5df96"
ODDS_API_KEY = "4dddf9e30c2f645e609beddeaec61540"
FB_HEADERS = {'X-Auth-Token': FOOTBALL_KEY}

st.set_page_config(page_title="ProScore AI Global", layout="wide")

# --- APP HEADER ---
st.title("🏟️ PRO-SCORE AI TERMINAL")
st.divider()

# --- SESSION STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR & RISK ---
st.sidebar.header("🛡️ RISK WATCHDOG")
bankroll = st.sidebar.number_input("Total Bankroll ($)", value=10000.0)
risk_limit = st.sidebar.slider("Safety Limit (%)", 0.5, 5.0, 2.0)
safe_stake = bankroll * (risk_limit / 100)

page = st.sidebar.selectbox("🎯 SELECT MODULE", ["AUTO-ARB SCANNER", "LIVE PULSE", "BANKROLL ANALYTICS"])

# --- MODULE: AUTO-ARB SCANNER ---
if page == "AUTO-ARB SCANNER":
    st.header("🤖 AI ARBITRAGE SCANNER")
    c1, c2 = st.columns(2)
    sport = c1.selectbox("Market", ["basketball_nba", "soccer_epl", "americanfootball_nfl"])
    stake = c2.number_input("Proposed Stake ($)", value=500.0)
    
    if stake > safe_stake:
        st.warning(f"⚠️ RISK ADVISORY: Stake exceeds your ${safe_stake:.2f} limit.")
    
    if st.button("🚀 START SCAN"):
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_API_KEY}&regions=us,uk&markets=h2h"
            data = requests.get(url).json()
            found = False
            for event in data:
                best = {"1": 0, "2": 0, "X": 0}
                for b in event['bookmakers']:
                    for m in b['markets']:
                        for o in m['outcomes']:
                            if o['name'] == event['home_team'] and o['price'] > best["1"]: best["1"] = o['price']
                            elif o['name'] == event['away_team'] and o['price'] > best["2"]: best["2"] = o['price']
                            elif o['name'] == "Draw" and o['price'] > best["X"]: best["X"] = o['price']
                
                inv_p = (1/best["1"]) + (1/best["2"]) + (1/best["X"] if best["X"] > 0 else 0)
                if inv_p < 1.0:
                    found = True
                    roi = (1/inv_p - 1) * 100
                    with st.expander(f"✅ {roi:.2f}% PROFIT: {event['home_team']} vs {event['away_team']}", expanded=True):
                        st.write(f"🏠 **Home Odds:** {best['1']} | ✈️ **Away Odds:** {best['2']}")
                        st.success(f"Guaranteed Profit on ${stake}: **${(stake/inv_p - stake):.2f}**")
            if not found: st.info("No arbitrage gaps detected currently.")
        except: st.error("API Connection Error.")

# --- MODULE: LIVE PULSE ---
elif page == "LIVE PULSE":
    st.header("🕒 LIVE SCORES")
    sport_type = st.radio("Feed", ["Football", "NBA"], horizontal=True)
    if sport_type == "Football":
        res = requests.get("https://api.football-data.org/v4/matches", headers=FB_HEADERS).json()
        for m in res.get('matches', [])[:10]:
            st.write(f"⚽ {m['homeTeam']['name']} vs {m['awayTeam']['name']} | Status: {m['status']}")
    else:
        url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?apiKey={ODDS_API_KEY}"
        data = requests.get(url).json()
        for s in data[:10]:
            st.write(f"🏀 {s['home_team']} vs {s['away_team']}")

# --- MODULE: ANALYTICS ---
elif page == "BANKROLL ANALYTICS":
    st.header("📈 PERFORMANCE")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df, y="Profit")
    else:
        st.info("Log your trades to see your bankroll growth.")
                        
