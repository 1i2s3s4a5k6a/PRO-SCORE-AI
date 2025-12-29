import streamlit as st
import requests
import pandas as pd
import numpy as np
import io
from datetime import datetime

# --- 1. CONFIGURATION & API KEYS ---
FOOTBALL_KEY = "dac17517d43d471e94d2b2484ef5df96"
ODDS_API_KEY = "4dddf9e30c2f645e609beddeaec61540"
FB_HEADERS = {'X-Auth-Token': FOOTBALL_KEY}

# --- 2. THEME & GLOBAL STYLING ---
st.set_page_config(page_title="ProScore AI Global", layout="wide", page_icon="🏟️")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-header {
        background-color: #002d62;
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .arb-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-left: 8px solid #28a745;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .roi-badge {
        background-color: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 4. HELPER FUNCTIONS ---
def calculate_stakes(total_inv, odds_list):
    probs = [1/o for o in odds_list]
    total_prob = sum(probs)
    stakes = [(total_inv * p) / total_prob for p in probs]
    profit = (stakes[0] * odds_list[0]) - total_inv
    return stakes, profit

def get_excel_download(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- 5. SIDEBAR / RISK WATCHDOG ---
st.sidebar.markdown("## 🛡️ RISK MANAGEMENT")
total_bankroll = st.sidebar.number_input("Total Bankroll ($)", value=10000.0)
risk_pct = st.sidebar.slider("Max Trade Risk (%)", 0.5, 5.0, 2.0)
safe_limit = total_bankroll * (risk_pct / 100)

st.sidebar.divider()
page = st.sidebar.selectbox("🎯 TERMINAL", ["AUTO-ARB SCANNER", "LIVE & UPCOMING", "BANKROLL ANALYTICS"])

# --- 6. MODULE 1: AUTO-ARB SCANNER ---
if page == "AUTO-ARB SCANNER":
    st.markdown('<div class="main-header"><h1>🤖 AI ARBITRAGE SCANNER</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    sport_key = col1.selectbox("Market", ["basketball_nba", "americanfootball_nfl", "soccer_epl", "soccer_usa_mls"])
    invest_amt = col2.number_input("Investment for this trade ($)", value=500.0)
    
    # Risk Watchdog
    if invest_amt > safe_limit:
        st.error(f"⚠️ EXPOSURE ALERT: Max safe stake is ${safe_limit:.2f} ({risk_pct}%)")
    
    if st.button("🚀 SCAN LIVE MARKETS"):
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={ODDS_API_KEY}&regions=us,uk&markets=h2h"
            data = requests.get(url).json()
            
            found = False
            for event in data:
                best_odds = {"1": 0, "2": 0, "X": 0}
                bookies = {"1": "", "2": "", "X": ""}
                
                for b in event['bookmakers']:
                    for m in b['markets']:
                        for o in m['outcomes']:
                            if o['name'] == event['home_team'] and o['price'] > best_odds["1"]:
                                best_odds["1"], bookies["1"] = o['price'], b['title']
                            elif o['name'] == event['away_team'] and o['price'] > best_odds["2"]:
                                best_odds["2"], bookies["2"] = o['price'], b['title']
                            elif o['name'] == "Draw" and o['price'] > best_odds["X"]:
                                best_odds["X"], bookies["X"] = o['price'], b['title']

                # Arb Math
                inv_prob = (1/best_odds["1"]) + (1/best_odds["2"])
                if best_odds["X"] > 0: inv_prob += (1/best_odds["X"])
                
                if inv_prob < 1.0:
                    found = True
                    roi = (1/inv_prob - 1) * 100
                    o_list = [best_odds["1"], best_odds["2"]]
                    if best_odds["X"] > 0: o_list.append(best_odds["X"])
                    
                    stakes, profit = calculate_stakes(invest_amt, o_list)
                    
                    st.markdown(f"""
                    <div class="arb-card">
                        <div style="display:flex; justify-content:space-between;">
                            <h3>🔥 {event['home_team']} vs {event['away_team']}</h3>
                            <span class="roi-badge">{roi:.2f}% ROI</span>
                        </div>
                        <p>🏠 <b>{event['home_team']}:</b> {best_odds['1']} ({bookies['1']}) → <b>Stake: ${stakes[0]:.2f}</b></p>
                        <p>✈️ <b>{event['away_team']}:</b> {best_odds['2']} ({bookies['2']}) → <b>Stake: ${stakes[1]:.2f}</b></p>
                        {f'<p>🤝 <b>Draw:</b> {best_odds["X"]} ({bookies["X"]}) → <b>Stake: ${stakes[2]:.2f}</b></p>' if best_odds["X"] > 0 else ""}
                        <h4 style="color:#28a745;">Guaranteed Profit: ${profit:.2f}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Log {event['home_team']} Bet"):
                        st.session_state.history.append({
                            "Date": datetime.now().strftime("%Y-%m-%d"),
                            "Match": f"{event['home_team']} vs {event['away_team']}",
                            "Investment": invest_amt,
                            "Profit": profit,
                            "ROI": roi
                        })
                        st.toast("Bet logged!")
            if not found: st.info("No arbitrage windows open currently.")
        except: st.error("API Limit reached.")

# --- 7. MODULE 2: LIVE & UPCOMING (30S REFRESH) ---
elif page == "LIVE & UPCOMING":
    st.markdown('<div class="main-header"><h1>🕒 LIVE PULSE</h1></div>', unsafe_allow_html=True)
    sport = st.radio("Sport", ["Football", "NBA", "NFL"], horizontal=True)
    
    @st.fragment(run_every=30)
    def live_scores():
        if sport == "Football":
            try:
                res = requests.get("https://api.football-data.org/v4/matches", headers=FB_HEADERS).json()
                for m in res['matches'][:10]:
                    st.write(f"⚽ {m['homeTeam']['name']} {m['score']['fullTime']['home']} - {m['score']['fullTime']['away']} {m['awayTeam']['name']}")
            except: st.warning("Connecting...")
        else:
            s_key = "basketball_nba" if sport == "NBA" else "americanfootball_nfl"
            try:
                url = f"https://api.the-odds-api.com/v4/sports/{s_key}/scores/?apiKey={ODDS_API_KEY}"
                data = requests.get(url).json()
                for s in data[:10]:
                    score = f"{s['scores'][0]['score']} - {s['scores'][1]['score']}" if s['scores'] else "UPCOMING"
                    st.write(f"🏀 {s['home_team']} vs {s['away_team']} | **{score}**")
            except: st.warning("Feed Busy...")
    live_scores()

# --- 8. MODULE 3: BANKROLL ANALYTICS ---
elif page == "BANKROLL ANALYTICS":
    st.markdown('<div class="main-header"><h1>📊 PERFORMANCE CENTER</h1></div>', unsafe_allow_html=True)
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        df['Cumulative'] = df['Profit'].cumsum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Profit", f"${df['Profit'].sum():.2f}")
        m2.metric("Avg ROI", f"{df['ROI'].mean():.2f}%")
        m3.metric("Trades", len(df))
        
        st.line_chart(df, x="Date", y="Cumulative")
        
        st.download_button("📥 Export Excel", data=get_excel_download(df), file_name="proscore_log.xlsx")
        if st.button("🗑️ Clear History"): st.session_state.history = []; st.rerun()
    else:
        st.info("No trades logged yet.")
                    
