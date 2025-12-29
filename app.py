import streamlit as st
import requests
import pandas as pd
import numpy as np
import math
from textblob import TextBlob
import nltk

# --- STABILITY SETUP ---
@st.cache_resource
def install_ai_brain():
    try:
        nltk.download('punkt', quiet=True)
    except:
        pass

install_ai_brain()

# --- CONFIG ---
API_KEY = "dac17517d43d471e94d2b2484ef5df96"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_KEY}

st.set_page_config(page_title="AI Betting HQ", layout="wide")

# --- NAVIGATION (Mobile-First Top Menu) ---
st.title("🛡️ AI Betting HQ")
page = st.selectbox("🎯 Select Tool:", 
                    ["Live Scores", "H2H Research", "News & Sentiment", "Arbitrage Scanner", "Bankroll Manager", "Aviator Tracker"])
st.divider()

# --- 1. LIVE SCORES (AUTO-REFRESHING) ---
if page == "Live Scores":
    st.header("🕒 Live Match Tracker")
    st.caption("Scoreboard updates automatically every 60 seconds.")

    @st.fragment(run_every=60)
    def auto_score_display():
        try:
            res = requests.get(f"{BASE_URL}matches", headers=HEADERS).json()
            if 'matches' in res and res['matches']:
                match_list = []
                for m in res['matches']:
                    match_list.append({
                        "League": m['competition']['name'],
                        "Match": f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}",
                        "Score": f"{m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0} - {m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0}",
                        "Status": m['status']
                    })
                st.table(pd.DataFrame(match_list))
                st.write(f"✅ Last Auto-Sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")
            else:
                st.info("No matches live or scheduled for today.")
        except:
            st.error("API Connection busy. Retrying in 60s...")

    auto_score_display()

# --- 2. H2H RESEARCH ---
elif page == "H2H Research":
    st.header("⚽ Team Matchup Analysis")
    league = st.selectbox("League", ["PL", "PD", "SA", "BL1", "FL1"], index=1)
    try:
        res_teams = requests.get(f"{BASE_URL}competitions/{league}/teams", headers=HEADERS).json()
        team_map = {t['name']: t['id'] for t in res_teams['teams']}
        t1 = st.selectbox("Home Team", list(team_map.keys()))
        t2 = st.selectbox("Away Team", list(team_map.keys()), index=1)
        
        if st.button("Run H2H Analysis"):
            res = requests.get(f"{BASE_URL}teams/{team_map[t1]}/matches?competitors={team_map[t2]}", headers=HEADERS).json()
            if 'matches' in res and res['matches']:
                h2h = [{"Date": m['utcDate'][:10], "Result": f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}", "Winner": m['score']['winner']} for m in res['matches']]
                st.table(pd.DataFrame(h2h))
            else: st.warning("No historical data found for this pair.")
    except: st.error("Could not load teams.")

# --- 3. NEWS & SENTIMENT ---
elif page == "News & Sentiment":
    st.header("📰 AI News Vibe Check")
    news_url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.goal.com/en/feeds/news"
    try:
        news_res = requests.get(news_url).json()
        for item in news_res['items'][:8]:
            score = TextBlob(item['title']).sentiment.polarity
            mood = "🟢 POSITIVE" if score > 0.1 else "🔴 NEGATIVE" if score < -0.1 else "⚪ NEUTRAL"
            with st.expander(f"{mood} | {item['title']}"):
                st.write(item['description'])
                st.link_button("Read Full Story", item['link'])
    except: st.error("News server is down.")

# --- 4. ARBITRAGE SCANNER ---
elif page == "Arbitrage Scanner":
    st.header("⚖️ 3-Way Arbitrage Calculator")
    inv = st.number_input("Total Investment ($)", value=100.0)
    c1, c2, c3 = st.columns(3)
    o1 = c1.number_input("Home Odds (1)", value=3.40)
    ox = c2.number_input("Draw Odds (X)", value=3.40)
    o2 = c3.number_input("Away Odds (2)", value=3.40)
    
    arb_pct = (1/o1) + (1/ox) + (1/o2)
    st.metric("Implied Probability", f"{arb_pct*100:.2f}%")
    
    if arb_pct < 1.0:
        profit = (inv / arb_pct) - inv
        st.success(f"💰 ARB FOUND! Guaranteed Profit: ${profit:.2f}")
        st.write(f"👉 Bet on Home: **${(inv/(o1*arb_pct)):.2f}**")
        st.write(f"👉 Bet on Draw: **${(inv/(ox*arb_pct)):.2f}**")
        st.write(f"👉 Bet on Away: **${(inv/(o2*arb_pct)):.2f}**")
    else: st.error("No Profit Gap found. Try different bookies.")

# --- 5. BANKROLL MANAGER ---
elif page == "Bankroll Manager":
    st.header("💰 Risk & Kelly Optimizer")
    bank = st.number_input("Current Bankroll ($)", value=1000.0)
    odds = st.number_input("Odds", value=2.0)
    win_p = st.slider("Your Win Probability (%)", 1, 100, 52) / 100
    
    kelly = (((odds-1)*win_p)-(1-win_p))/(odds-1)
    if kelly > 0:
        st.success(f"Suggested Stake: ${bank * kelly * 0.5:.2f} (Safe Half-Kelly)")
    else: st.error("Math says: Do not take this bet.")

# --- 6. AVIATOR TRACKER ---
elif page == "Aviator Tracker":
    st.header("🛩️ Multiplier Trend Tracker")
    raw = st.text_input("Enter last results (comma-separated):", "1.5, 2.0, 1.1, 8.4")
    if raw:
        vals = [float(x.strip()) for x in raw.split(",")]
        st.metric("Session Average", f"{np.mean(vals):.2f}x")
        streak = 0
        for v in reversed(vals):
            if v < 2.0: streak += 1
            else: break
        if streak >= 3: st.warning(f"⚠️ {streak} LOWS IN A ROW. A 'Purple' (2x+) event is statistically due.")
        else: st.info("Game is currently balanced.")

