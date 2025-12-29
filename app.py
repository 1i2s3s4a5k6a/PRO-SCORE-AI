import streamlit as st
import requests
import pandas as pd
import math
import numpy as np
from textblob import TextBlob
import nltk

# --- STABILITY: AI DATA DOWNLOAD ---
@st.cache_resource
def load_ai():
    try:
        nltk.download('punkt', quiet=True)
    except: pass
load_ai()

# --- CONFIG ---
API_KEY = "dac17517d43d471e94d2b2484ef5df96"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_KEY}

st.set_page_config(page_title="AI Betting HQ", layout="wide")

# --- NAVIGATION ---
page = st.sidebar.selectbox("Go to:", ["Live Scores", "H2H Research", "News & Sentiment", "Arbitrage Scanner", "Bankroll Manager", "Aviator Tracker"])

# --- 1. LIVE SCORES ---
if page == "Live Scores":
    st.header("🕒 Today's Matches")
    if st.button("Refresh"):
        res = requests.get(f"{BASE_URL}matches", headers=HEADERS).json()
        if 'matches' in res and res['matches']:
            data = [{"Home": m['homeTeam']['name'], "Away": m['awayTeam']['name'], "Score": f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}", "Status": m['status']} for m in res['matches']]
            st.table(pd.DataFrame(data))
        else: st.info("No games scheduled today.")

# --- 2. H2H RESEARCH ---
elif page == "H2H Research":
    st.header("⚽ H2H History")
    league = st.selectbox("League", ["PL", "PD", "SA", "BL1", "FL1"])
    # Helper to get teams
    res_teams = requests.get(f"{BASE_URL}competitions/{league}/teams", headers=HEADERS).json()
    team_map = {t['name']: t['id'] for t in res_teams['teams']}
    t1 = st.selectbox("Team A", list(team_map.keys()))
    t2 = st.selectbox("Team B", list(team_map.keys()), index=1)
    if st.button("Analyze"):
        id1, id2 = team_map[t1], team_map[t2]
        res = requests.get(f"{BASE_URL}teams/{id1}/matches?competitors={id2}", headers=HEADERS).json()
        if 'matches' in res and res['matches']:
            history = [{"Date": m['utcDate'][:10], "Result": f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}"} for m in res['matches']]
            st.table(pd.DataFrame(history))

# --- 3. NEWS & SENTIMENT ---
elif page == "News & Sentiment":
    st.header("📰 AI News Vibe")
    news_url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.goal.com/en/feeds/news"
    news_res = requests.get(news_url).json()
    for item in news_res['items'][:5]:
        score = TextBlob(item['title']).sentiment.polarity
        mood = "🟢" if score > 0.1 else "🔴" if score < -0.1 else "⚪"
        with st.expander(f"{mood} {item['title']}"):
            st.write(item['description'])

# --- 4. ARBITRAGE SCANNER ---
elif page == "Arbitrage Scanner":
    st.header("⚖️ 3-Way Arbitrage")
    inv = st.number_input("Investment ($)", value=100.0)
    o1 = st.number_input("Home Odds", value=3.0)
    ox = st.number_input("Draw Odds", value=3.0)
    o2 = st.number_input("Away Odds", value=3.0)
    arb_pct = (1/o1) + (1/ox) + (1/o2)
    if arb_pct < 1.0:
        st.success(f"Profit Found! ROI: {((1/arb_pct)-1)*100:.2f}%")
        st.write(f"Stake 1: ${inv/(o1*arb_pct):.2f} | Stake X: ${inv/(ox*arb_pct):.2f} | Stake 2: ${inv/(o2*arb_pct):.2f}")
    else: st.error("No Arbitrage.")

# --- 5. BANKROLL MANAGER ---
elif page == "Bankroll Manager":
    st.header("💰 Risk Management")
    br = st.number_input("Bankroll ($)", value=1000.0)
    odds = st.number_input("Odds", value=2.0)
    prob = st.slider("Win Prob %", 1, 100, 52) / 100
    kelly = (((odds-1)*prob)-(1-prob))/(odds-1)
    if kelly > 0: st.success(f"Suggested Bet: ${br*kelly*0.5:.2f} (Half-Kelly)")
    else: st.error("No Value Bet found.")

# --- 6. AVIATOR TRACKER ---
elif page == "Aviator Tracker":
    st.header("🛩️ Aviator Patterns")
    raw = st.text_input("Last 10 results (e.g. 1.2, 5.0, 1.1)", "1.5, 2.0")
    vals = [float(x.strip()) for x in raw.split(",")]
    st.write(f"Average: {np.mean(vals):.2f}x")
    streak = 0
    for v in reversed(vals):
        if v < 2.0: streak += 1
        else: break
    if streak >= 3: st.warning(f"⚠️ {streak} Lows in a row. High Multiplier overdue!")
