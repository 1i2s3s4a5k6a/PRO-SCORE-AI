import streamlit as st
import requests
import pandas as pd
import math
import numpy as np

# --- CONFIG ---
API_KEY = "dac17517d43d471e94d2b2484ef5df96"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_KEY}

st.set_page_config(page_title="AI Betting Suite", layout="wide")

# --- SIDEBAR: TEAM ID LOOK-UP ---
st.sidebar.header("🔍 Team ID Look-up")
look_league = st.sidebar.selectbox("Select League for IDs", ["PL", "BL1", "SA", "PD", "FL1"])

@st.cache_data(ttl=86400)
def get_team_ids(league_code):
    try:
        response = requests.get(f"{BASE_URL}competitions/{league_code}/teams", headers=HEADERS)
        data = response.json()
        return pd.DataFrame([{"ID": t['id'], "Name": t['name']} for t in data['teams']])
    except:
        return pd.DataFrame(columns=["ID", "Name"])

st.sidebar.dataframe(get_team_ids(look_league), hide_index=True)

# --- MAIN INTERFACE ---
st.title("🛡️ AI Betting & Strategy Suite")

tabs = st.tabs(["Research & H2H", "Arbitrage Scanner", "Bankroll & Risk", "Goal Path", "Aviator Tracker", "Glossary"])

with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.header("League Standings")
        league = st.selectbox("League", ["PL", "BL1", "SA", "PD", "FL1"], key="res_league")
        if st.button("Fetch Table"):
            data = requests.get(f"{BASE_URL}competitions/{league}/standings", headers=HEADERS).json()
            if 'standings' in data:
                table = data['standings'][0]['table']
                st.table(pd.DataFrame([{"Pos": t['position'], "Team": t['team']['name'], "Form": t['form'], "Pts": t['points']} for t in table]).set_index("Pos"))
    with col2:
        st.header("H2H History")
        id_a = st.number_input("Team A ID", value=64)
        id_b = st.number_input("Team B ID", value=65)
        if st.button("Analyze Matchup"):
            res = requests.get(f"{BASE_URL}teams/{id_a}/matches?competitors={id_b}", headers=HEADERS).json()
            if 'matches' in res and len(res['matches']) > 0:
                st.dataframe(pd.DataFrame([{"Date": m['utcDate'][:10], "Score": f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}", "Winner": m['score']['winner']} for m in res['matches']]))

with tabs[1]:
    st.header("⚖️ Arbitrage Calculator")
    c1, c2 = st.columns(2)
    o1 = c1.number_input("Bookie A Odds", value=2.10)
    o2 = c2.number_input("Bookie B Odds", value=2.10)
    inv = st.number_input("Total Investment ($)", value=100.0)
    arb_pct = (1/o1) + (1/o2)
    if arb_pct < 1.0:
        st.success(f"Arb Found! Profit: ${(inv/arb_pct)-inv:.2f}")
    else: st.error(f"No Arb. Market Efficiency: {arb_pct*100:.2f}%")

with tabs[2]:
    st.header("Bankroll Manager")
    br = st.number_input("Current Bankroll ($)", value=1000.0)
    o = st.number_input("Odds", value=2.0)
    p = st.slider("Win Prob (%)", 1, 100, 52) / 100
    f = (((o-1)*p)-(1-p))/(o-1)
    if f > 0:
        st.success(f"Bet Amount: ${br*f*0.5:.2f}")
        ror = ((1-p)/p) ** (br/(br*f*0.5))
        st.metric("Risk of Ruin", f"{ror*100:.4f}%")
    else: st.error("No Mathematical Edge.")

with tabs[3]:
    st.header("🚀 Goal Path")
    target = st.number_input("Target Bankroll ($)", value=5000.0)
    if f > 0:
        ev = (p * (br*f*0.5*(o-1))) - ((1-p)*br*f*0.5)
        st.title(f"{math.ceil((target-br)/ev) if ev > 0 else 0} Bets to Goal")

with tabs[4]:
    st.header("🛩️ Aviator Pattern Tracker")
    st.write("Input the last multipliers to find statistical clusters.")
    raw_data = st.text_input("Enter last 10-20 multipliers (comma separated)", "1.2, 3.5, 1.0, 2.1, 1.8")
    if raw_data:
        vals = [float(x.strip()) for x in raw_data.split(",")]
        lows = sum(1 for x in vals if x < 2.0)
        st.progress(lows/len(vals), text=f"Cold Streak (Blue) Density: {lows/len(vals)*100:.0f}%")
        
        # Streak Counter
        streak = 0
        for v in reversed(vals):
            if v < 2.0: streak += 1
            else: break
        if streak >= 3:
            st.warning(f"⚠️ {streak} LOWS IN A ROW. Statistical 'Purple' (2x+) event is trending upward.")
        else: st.info("Game is currently in a balanced cycle.")

with tabs[5]:
    st.header("📚 Glossary")
    st.markdown("- **Kelly:** Optimizes bet size.\n- **RoR:** Chance of going broke.\n- **Arb:** Guaranteed profit from split odds.\n- **Aviator Cluster:** When the RNG 'balances' after a long streak of low multipliers.")
    st.write("**H2H:** Head-to-Head. The historical record of matches between two specific teams.")
