import streamlit as st
import requests
import pandas as pd
import numpy as np
import math
from textblob import TextBlob
import nltk

# --- THEME & STYLING ---
st.set_page_config(page_title="ProScore AI", layout="wide")

# Custom CSS for Blue/White Pro Look
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .main-header {
        background-color: #004682;
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .match-card {
        background-color: white;
        padding: 12px;
        border-radius: 10px;
        border-bottom: 3px solid #004682;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .score-box {
        background-color: #004682;
        color: white;
        padding: 5px 12px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 18px;
    }
    .stButton>button {
        background-color: #004682;
        color: white;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BOOTSTRAP AI ---
@st.cache_resource
def install_ai():
    try: nltk.download('punkt', quiet=True)
    except: pass
install_ai()

# --- CONFIG ---
API_KEY = "dac17517d43d471e94d2b2484ef5df96"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_KEY}

# --- HEADER ---
st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI</h1></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
page = st.selectbox("⚡ SELECT TERMINAL:", 
                    ["LIVE SCORES", "H2H ANALYSIS", "MARKET SENTIMENT", "ARBITRAGE SCANNER", "KELLY MANAGER", "AVIATOR TRACKER"])
st.divider()

# --- 1. LIVE SCORES ---
if page == "LIVE SCORES":
    st.subheader("🕒 Real-Time Board")
    @st.fragment(run_every=60)
    def live_board():
        try:
            res = requests.get(f"{BASE_URL}matches", headers=HEADERS).json()
            if 'matches' in res and res['matches']:
                for m in res['matches']:
                    home, away = m['homeTeam']['name'], m['awayTeam']['name']
                    h_s = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
                    a_s = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
                    st.markdown(f"""
                        <div class="match-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="width: 35%; text-align: right;"><b>{home}</b></div>
                                <div class="score-box">{h_s} - {a_s}</div>
                                <div style="width: 35%; text-align: left;"><b>{away}</b></div>
                            </div>
                            <div style="text-align: center; font-size: 12px; color: gray; margin-top: 5px;">{m['status']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                st.caption(f"Last updated: {pd.Timestamp.now().strftime('%H:%M:%S')}")
            else: st.info("No active matches.")
        except: st.error("API Limit reached. Wait 60s.")
    live_board()

# --- 2. H2H ANALYSIS ---
elif page == "H2H ANALYSIS":
    st.subheader("⚽ Matchup Deep-Dive")
    league = st.selectbox("League", ["PL", "PD", "SA", "BL1", "FL1"], index=1)
    res_teams = requests.get(f"{BASE_URL}competitions/{league}/teams", headers=HEADERS).json()
    team_map = {t['name']: t['id'] for t in res_teams['teams']}
    col1, col2 = st.columns(2)
    t1 = col1.selectbox("Home Team", list(team_map.keys()))
    t2 = col2.selectbox("Away Team", list(team_map.keys()), index=1)
    if st.button("RUN ANALYSIS"):
        res = requests.get(f"{BASE_URL}teams/{team_map[t1]}/matches?competitors={team_map[t2]}", headers=HEADERS).json()
        if 'matches' in res and res['matches']:
            h2h = [{"Date": m['utcDate'][:10], "Score": f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}"} for m in res['matches']]
            st.table(pd.DataFrame(h2h))
        else: st.warning("No history found.")

# --- 3. MARKET SENTIMENT ---
elif page == "MARKET SENTIMENT":
    st.subheader("📰 AI Vibe Check")
    news_url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.goal.com/en/feeds/news"
    news_res = requests.get(news_url).json()
    for item in news_res['items'][:6]:
        score = TextBlob(item['title']).sentiment.polarity
        mood = "🟢 POSITIVE" if score > 0.1 else "🔴 NEGATIVE" if score < -0.1 else "⚪ NEUTRAL"
        with st.expander(f"{mood} | {item['title']}"):
            st.write(item['description'])

# --- 4. ARBITRAGE SCANNER ---
elif page == "ARBITRAGE SCANNER":
    st.subheader("⚖️ 3-Way Profit Scanner")
    inv = st.number_input("Total Capital ($)", value=100.0)
    c1, c2, c3 = st.columns(3)
    o1 = c1.number_input("Home Odds", value=3.50)
    ox = c2.number_input("Draw Odds", value=3.20)
    o2 = c3.number_input("Away Odds", value=3.80)
    arb_pct = (1/o1) + (1/ox) + (1/o2)
    if arb_pct < 1.0:
        st.balloons()
        st.success(f"PROFIT GAP FOUND! ROI: {((1/arb_pct)-1)*100:.2f}%")
        st.write(f"Home Stake: **${inv/(o1*arb_pct):.2f}** | Draw Stake: **${inv/(ox*arb_pct):.2f}** | Away Stake: **${inv/(o2*arb_pct):.2f}**")
    else: st.error("No Profit Gap found.")

# ---
