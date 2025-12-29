import streamlit as st
import requests
import pandas as pd
import numpy as np
from textblob import TextBlob
import nltk

# --- THEME & STYLING ---
st.set_page_config(page_title="ProScore AI", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    
    /* Global Text Visibility */
    html, body, [class*="css"], .stMarkdown, p, span, label {
        color: #1a1a1a !important; 
    }

    .main-header {
        background-color: #004682;
        padding: 20px;
        border-radius: 12px;
        color: white !important;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .main-header h1 { color: white !important; margin: 0; }

    .match-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-bottom: 4px solid #004682;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .team-container {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 38%;
    }
    
    .team-name {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }

    .crest { width: 25px; height: 25px; object-fit: contain; }

    .score-box {
        background-color: #004682;
        color: white !important;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 20px;
        text-align: center;
        min-width: 65px;
    }

    .prob-bar-container {
        width: 100%; height: 8px; background-color: #e0e0e0;
        border-radius: 4px; margin-top: 15px; display: flex; overflow: hidden;
    }
    .home-prob { background-color: #004682; height: 100%; }
    .draw-prob { background-color: #bdc3c7; height: 100%; }
    .away-prob { background-color: #ff4b4b; height: 100%; }

    .prob-labels {
        display: flex; justify-content: space-between;
        font-size: 10px; font-weight: bold; margin-top: 4px; color: #7f8c8d !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BOOTSTRAP ---
@st.cache_resource
def install_ai():
    try: nltk.download('punkt', quiet=True)
    except: pass
install_ai()

API_KEY = "dac17517d43d471e94d2b2484ef5df96"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_KEY}

def get_win_prob(h_s, a_s, status):
    if status == 'FINISHED':
        if h_s > a_s: return 100, 0, 0
        elif a_s > h_s: return 0, 0, 100
        else: return 0, 100, 0
    diff = h_s - a_s
    if diff == 0: return 38, 30, 32
    if diff == 1: return 65, 20, 15
    if diff >= 2: return 92, 5, 3
    if diff == -1: return 15, 20, 65
    return 3, 5, 92

st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI</h1></div>', unsafe_allow_html=True)

page = st.selectbox("⚡ SELECT TERMINAL:", 
                    ["LIVE SCORES", "H2H ANALYSIS", "MARKET SENTIMENT", "ARBITRAGE SCANNER", "KELLY MANAGER", "AVIATOR TRACKER"])

# --- 1. LIVE SCORES ---
if page == "LIVE SCORES":
    st.markdown("### 🕒 Live Momentum Tracker")
    @st.fragment(run_every=60)
    def live_board():
        try:
            res = requests.get(f"{BASE_URL}matches", headers=HEADERS).json()
            if 'matches' in res and res['matches']:
                for m in res['matches']:
                    h, a = m['homeTeam'], m['awayTeam']
                    h_s = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
                    a_s = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
                    hp, dp, ap = get_win_prob(h_s, a_s, m['status'])
                    st.markdown(f"""
                        <div class="match-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div class="team-container" style="justify-content: flex-end;"><span class="team-name">{h['name']}</span><img src="{h.get('crest','')}" class="crest"></div>
                                <div class="score-box">{h_s} - {a_s}</div>
                                <div class="team-container"><img src="{a.get('crest','')}" class="crest"><span class="team-name">{a['name']}</span></div>
                            </div>
                            <div class="prob-bar-container"><div class="home-prob" style="width:{hp}%"></div><div class="draw-prob" style="width:{dp}%"></div><div class="away-prob" style="width:{ap}%"></div></div>
                            <div class="prob-labels"><span>{hp}%</span><span>DRAW</span><span>{ap}%</span></div>
                            <div style="text-align:center; color:red; font-size:10px; font-weight:bold; margin-top:5px;">{m['status']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else: st.info("No matches live.")
        except: st.error("API Limit reached. Wait 60s.")
    live_board()

# --- 2. H2H ---
elif page == "H2H ANALYSIS":
    st.subheader("⚽ Matchup History")
    league = st.selectbox("League", ["PL", "PD", "SA", "BL1", "FL1"])
    try:
        t_res = requests.get(f"{BASE_URL}competitions/{league}/teams", headers=HEADERS).json()
        t_map = {t['name']: t['id'] for t in t_res['teams']}
        t1 = st.selectbox("Home", list(t_map.keys()))
        t2 = st.selectbox("Away", list(t_map.keys()), index=1)
        if st.button("RUN"):
            res = requests.get(f"{BASE_URL}teams/{t_map[t1]}/matches?competitors={t_map[t2]}", headers=HEADERS).json()
            if 'matches' in res and res['matches']:
                df = pd.DataFrame([{"Date": m['utcDate'][:10], "Score": f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}"} for m in res['matches']])
                st.table(df)
    except: st.error("Error loading data.")

# --- 3. SENTIMENT ---
elif page == "MARKET SENTIMENT":
    st.subheader("📰 AI Vibe Check")
    try:
        n_res = requests.get("https://api.rss2json.com/v1/api.json?rss_url=https://www.goal.com/en/feeds/news").json()
        for i in n_res['items'][:5]:
            score = TextBlob(i['title']).sentiment.polarity
            mood = "🟢" if score > 0.1 else "🔴" if score < -0.1 else "⚪"
            with st.expander(f"{mood} {i['title']}"): st.write(i['description'])
    except: st.error("News offline.")

# --- 4. ARBITRAGE ---
elif page == "ARBITRAGE SCANNER":
    st.subheader("⚖️ Profit Scanner")
    inv = st.number_input("Capital ($)", value=100.0)
    o1 = st.number_input("Home Odds", value=3.0)
    ox = st.number_input("Draw Odds", value=3.0)
    o2 = st.number_input("Away Odds", value=3.0)
    arb = (1/o1) + (1/ox) + (1/o2)
    if arb < 1.0:
        st.balloons()
        st.success(f"PROFIT! ROI: {((1/arb)-1)*100:.2f}%")
        st.write(f"Stake 1: ${inv/(o1*arb):.2f} | Stake X: ${inv/(ox*arb):.2f} | Stake 2: ${inv/(o2*arb):.2f}")
    else: st.warning("No Gap.")

# --- 5. KELLY ---
elif page == "KELLY MANAGER":
    st.subheader("💰 Risk Manager")
    bank = st.number_input("Bankroll ($)", value=1000.0)
    odds = st.number_input("Odds", value=2.0)
    prob = st.slider("Win Prob %", 1, 100, 52) / 100
    k = (((odds-1)*prob)-(1-prob))/(odds-1)
    if k > 0: st.success(f"Bet: ${bank * k * 0.5:.2f}")
    else: st.error("No Value.")

# --- 6. AVIATOR ---
elif page == "AVIATOR TRACKER":
    st.subheader("🛩️ Multiplier Tracker")
    raw = st.text_input("Last results (e.g. 1.2, 5.0)", "1.5, 2.0")
    if raw:
        vals = [float(x.strip()) for x in raw.split(",")]
        st.metric("Avg", f"{np.mean(vals):.2f}x")
        streak = 0
        for v in reversed(vals):
            if v < 2.0: streak += 1
            else: break
        if streak >= 3: st.warning(f"⚠️ {streak} Lows! Purple due.")
