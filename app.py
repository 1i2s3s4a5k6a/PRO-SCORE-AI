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
    html, body, [class*="css"], .stMarkdown, p, span, label { color: #1a1a1a !important; }

    .main-header {
        background-color: #004682;
        padding: 20px;
        border-radius: 12px;
        color: white !important;
        text-align: center;
        margin-bottom: 20px;
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
    
    .team-container { display: flex; align-items: center; gap: 8px; width: 40%; }
    .team-name { color: #1a1a1a !important; font-weight: 700 !important; font-size: 14px !important; }
    .crest { width: 22px; height: 22px; object-fit: contain; }

    .score-box {
        background-color: #004682;
        color: white !important;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 18px;
        text-align: center;
        min-width: 60px;
    }

    /* Win Probability UI Fix */
    .prob-bar-container {
        width: 100%; height: 10px; background-color: #e0e0e0;
        border-radius: 5px; margin-top: 15px; display: flex; overflow: hidden;
    }
    .home-prob { background-color: #004682; height: 100%; transition: 0.5s; }
    .draw-prob { background-color: #bdc3c7; height: 100%; transition: 0.5s; }
    .away-prob { background-color: #ff4b4b; height: 100%; transition: 0.5s; }

    .prob-text-container {
        display: flex; justify-content: space-between;
        margin-top: 5px; font-size: 11px; font-weight: bold;
    }
    .draw-label { color: #7f8c8d !important; text-align: center; flex-grow: 1; }
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

# Logic to calculate momentum based on result
def calc_probs(h_s, a_s, status):
    if status == 'FINISHED':
        if h_s > a_s: return 100, 0, 0
        if a_s > h_s: return 0, 0, 100
        return 0, 100, 0
    # Live Logic
    diff = h_s - a_s
    if diff == 0: return 35, 30, 35
    if diff == 1: return 70, 20, 10
    if diff >= 2: return 95, 4, 1
    if diff == -1: return 10, 20, 70
    return 1, 4, 95

st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI</h1></div>', unsafe_allow_html=True)

page = st.selectbox("🎯 TERMINAL:", ["LIVE SCORES", "ARBITRAGE SCANNER", "H2H ANALYSIS", "MARKET SENTIMENT", "KELLY MANAGER", "AVIATOR TRACKER"])

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
                    hp, dp, ap = calc_probs(h_s, a_s, m['status'])
                    
                    st.markdown(f"""
                        <div class="match-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div class="team-container" style="justify-content: flex-end;"><span class="team-name">{h['name']}</span><img src="{h.get('crest','')}" class="crest"></div>
                                <div class="score-box">{h_s} - {a_s}</div>
                                <div class="team-container"><img src="{a.get('crest','')}" class="crest"><span class="team-name">{a['name']}</span></div>
                            </div>
                            <div class="prob-bar-container"><div class="home-prob" style="width:{hp}%"></div><div class="draw-prob" style="width:{dp}%"></div><div class="away-prob" style="width:{ap}%"></div></div>
                            <div class="prob-text-container">
                                <span style="color:#004682">{hp}%</span>
                                <span class="draw-label">DRAW ({dp}%)</span>
                                <span style="color:#ff4b4b">{ap}%</span>
                            </div>
                            <div style="text-align:center; color:red; font-size:10px; font-weight:bold; margin-top:5px;">{m['status']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else: st.info("No matches live.")
        except: st.error("API Limit. Retrying in 60s.")
    live_board()

elif page == "ARBITRAGE SCANNER":
    mode = st.radio("Scanner Mode", ["2-Way (O/U, BTTS)", "3-Way (1X2)"])
    inv = st.number_input("Total Investment ($)", value=100.0)
    
    if mode == "2-Way (O/U, BTTS)":
        c1, c2 = st.columns(2)
        o1 = c1.number_input("Outcome 1 Odds", value=2.10)
        o2 = c2.number_input("Outcome 2 Odds", value=2.10)
        arb = (1/o1) + (1/o2)
        if arb < 1.0:
            st.success(f"PROFIT! ROI: {((1/arb)-1)*100:.2f}%")
            st.info(f"Bet 1: ${inv/(o1*arb):.2f} | Bet 2: ${inv/(o2*arb):.2f}")
        else: st.warning("No Gap.")
        
    else:
        c1, c2, c3 = st.columns(3)
        o1, ox, o2 = c1.number_input("1"), c2.number_input("X"), c3.number_input("2")
        arb = (1/o1) + (1/ox) + (1/o2)
        if arb < 1.0:
            st.success(f"PROFIT! ROI: {((1/arb)-1)*100:.2f}%")
            st.info(f"1: ${inv/(o1*arb):.2f} | X: ${inv/(ox*arb):.2f} | 2: ${inv/(o2*arb):.2f}")
        else: st.warning("No Gap.")

# --- Keep remaining elif blocks for H2H, Market, Kelly, Aviator ---
