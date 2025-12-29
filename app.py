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
    html, body, [class*="css"], .stMarkdown, p, span {
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
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
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

    /* Win Probability Bar */
    .prob-bar-container {
        width: 100%;
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        margin-top: 15px;
        display: flex;
        overflow: hidden;
    }
    .home-prob { background-color: #004682; height: 100%; }
    .draw-prob { background-color: #bdc3c7; height: 100%; }
    .away-prob { background-color: #ff4b4b; height: 100%; }

    .prob-labels {
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        font-weight: bold;
        margin-top: 4px;
        color: #7f8c8d !important;
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

# --- PROBABILITY LOGIC ---
def get_win_prob(h_score, a_score, status):
    if status == 'FINISHED':
        if h_score > a_score: return 100, 0, 0
        if a_score > h_score: return 0, 0, 100
        return 0, 100, 0
    
    # Simple AI Logic: Lead by 1 goal = +30% chance. Lead by 2+ = 90% chance.
    diff = h_score - a_score
    if diff == 0: return 38, 30, 32 # Slight Home edge
    if diff == 1: return 65, 20, 15
    if diff >= 2: return 92, 5, 3
    if diff == -1: return 15, 20, 65
    if diff <= -2: return 3, 5, 92
    return 33, 34, 33

st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI</h1></div>', unsafe_allow_html=True)

page = st.selectbox("⚡ SELECT TERMINAL:", 
                    ["LIVE SCORES", "H2H ANALYSIS", "MARKET SENTIMENT", "ARBITRAGE SCANNER", "KELLY MANAGER", "AVIATOR TRACKER"])

if page == "LIVE SCORES":
    st.markdown("### 🕒 Live Momentum Tracker")
    @st.fragment(run_every=60)
    def live_board():
        try:
            res = requests.get(f"{BASE_URL}matches", headers=HEADERS).json()
            if 'matches' in res and res['matches']:
                for m in res['matches']:
                    home, away = m['homeTeam'], m['awayTeam']
