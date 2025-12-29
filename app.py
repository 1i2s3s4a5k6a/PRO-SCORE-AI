import streamlit as st
import requests
import pandas as pd
import numpy as np
import io
from datetime import datetime

# --- 1. CONFIGURATION ---
FOOTBALL_KEY = "dac17517d43d471e94d2b2484ef5df96"
ODDS_API_KEY = "4dddf9e30c2f645e609beddeaec61540"
FB_HEADERS = {'X-Auth-Token': FOOTBALL_KEY}

st.set_page_config(page_title="ProScore AI Global", layout="wide", page_icon="🏟️")

# --- 2. HIGH-CONTRAST CSS OVERRIDE ---
# This forces dark text on a light background to fix the visibility issues
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, h4, p, span, li, label, div {
        color: #001f3f !important; /* Force all text to Dark Navy */
    }
    .main-header {
        background-color: #002d62 !important;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    .main-header h1 { color: #ffffff !important; }
    .arb-card {
        background-color: #f8f9fa !important;
        padding: 20px;
        border-radius: 12px;
        border-left: 10px solid #28a745;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .roi-badge {
        background-color: #28a745 !important;
        color: #ffffff !important;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #002d62 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 4. CORE LOGIC FUNCTIONS ---
def get_excel_download(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- 5. SIDEBAR & RISK MANAGEMENT ---
st.sidebar.markdown("## 🛡️ RISK WATCHDOG")
bankroll = st.sidebar.number_input("Total Bankroll ($)", value=10000.0)
risk_limit_pct = st.sidebar.slider("Safety Limit (%)", 0.5, 5.0, 2.0)
safe_stake = bankroll * (risk_limit_pct / 100)

st.sidebar.divider()
page = st.sidebar.selectbox("🎯 SELECT MODULE", ["AUTO-ARB SCANNER", "LIVE PULSE", "BANKROLL ANALYTICS"])

# --- 6. MODULE: AUTO-ARB SCANNER ---
if page == "AUTO-ARB SCANNER":
    st.markdown('<div class="main-header"><h1>🤖 AI ARBITRAGE SCANNER</h1></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    sport = c1.selectbox("Market", ["basketball_nba", "soccer_epl", "americanfootball_nfl"])
    stake = c2.number_input("Proposed Stake ($)", value=500.0)
    
    if stake > safe_stake:
        st.warning(f"⚠️ RISK ADVISORY: Proposed stake exceeds your {risk_limit_pct}% safety threshold (${safe_stake:.2f}).")
    
    if st.button("🚀 INITIATE SCAN"):
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_API_KEY}&regions=us,uk&markets=h2h"
            data = requests.get(url).json()
            found = False
            for event in data:
                best = {"1": 0, "2": 0, "X": 0}
                bk = {"1": "", "2": "", "X": ""}
                for b in event['bookmakers']:
                    for m in b['markets']:
                        for o in m['outcomes']:
                            if o['name'] == event['home_team'] and o['price'] > best["1"]:
                                best["1"], bk["1"] = o['price'], b['title']
                            elif o['name'] == event['away_team'] and o['price'] > best["2"]:
                                best["2"], bk["2"] = o['price'], b['title']
                            elif o['name'] == "Draw" and o['price'] > best["X"]:
                                best["X"], bk["X"] = o['price'], b['title']
                inv_p = (1/best["1"]) + (1/best["2"]) + (1/best["X"] if best["X"] > 0 else 0)
                if inv_p < 1.0:
                    found = True
                    roi = (1/inv_p - 1) * 100
                    st.markdown(f"""
                    <div class="arb-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0;">{event['home_team']} vs {event['away_team']}</h3>
                            <span class="roi-badge">{roi:.2f}% ROI</span>
                        </div>
                        <p style="margin-top:10px;">🏠 <b>{event['home_team']}:</b> {best['1']} at {bk['1']}</p>
                        <p>✈️ <b>{event['away_team']}:</b> {best['2']} at {bk['2']}</p>
                        {f'<p>🤝 <b>Draw:</b> {best["X"]} at {bk["X"]}</p>' if best["X"] > 0 else ""}
                        <hr>
                        <h4 style="color:#28a745 !important;">Guaranteed Profit: ${(stake/inv_p - stake):.2f}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Confirm {event['home_team']} Log"):
                        st.session_state.history.append({"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Match": f"{event['home_team']} vs {event['away_team']}", "Profit": (stake/inv_p - stake), "ROI": roi})
                        st.toast("Bet Logged!")
            if not found: st.info("Scanning complete. No arbitrage windows open currently.")
        except: st.error("API Limit reached.")

# --- 7. MODULE: LIVE PULSE (SAFE DATA EXTRACT) ---
elif page == "LIVE PULSE":
    st.markdown('<div class="main-header"><h1>🕒 LIVE PULSE</h1></div>', unsafe_allow_html=True)
    sport_type = st.radio("Select Feed", ["Football (Soccer)", "NBA Basketball"], horizontal=True)
    
    @st.fragment(run_every=30)
    def update_scores():
        if sport_type == "Football (Soccer)":
            try:
                res = requests.get("https://api.football-data.org/v4/matches", headers=FB_HEADERS).json()
                matches = res.get('matches', [])
                for m in matches[:10]:
                    score_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else "-"
                    score_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else "-"
                    st.write(f"⚽ **{m['homeTeam']['name']}** {score_h} - {score_a} **{m['awayTeam']['name']}** | Status: `{m['status']}`")
            except: st.error("Football feed connection issue.")
        else:
            try:
                url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/scores/?apiKey={ODDS_API_KEY}"
                data = requests.get(url).json()
                for s in data[:10]:
                    score_str = "UPCOMING"
                    if s.get('scores'):
                        score_str = f"{s['scores'][0]['score']} - {s['scores'][1]['score']}"
                    st.write(f"🏀 **{s['home_team']}** vs **{s['away_team']}** | `{score_str}`")
            except: st.error("NBA feed connection issue.")
    update_scores()

# --- 8. MODULE: BANKROLL ANALYTICS ---
elif page == "BANKROLL ANALYTICS":
    st.markdown('<div class="main-header"><h1>📈 PERFORMANCE ANALYTICS</h1></div>', unsafe_allow_html=True)
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        df['Cumulative'] = df['Profit'].cumsum()
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Profit", f"${df['Profit'].sum():.2f}")
        m2.metric("Average ROI", f"{df['ROI'].mean():.2f}%")
        m3.metric("Trades Executed", len(df))
        st.line_chart(df, x="Date", y="Cumulative")
        st.download_button("📥 Export Excel History", data=get_excel_download(df), file_name="proscore_report.xlsx")
    else:
        st.info("No trades logged yet. Start scanning to see your growth chart!")
                                
