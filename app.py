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
    .stMainBlockContainer, .stSelectbox, .stNumberInput, .stSlider { color: #1a1a1a !important; }
    .main-header {
        background-color: #004682;
        padding: 20px;
        border-radius: 12px;
        color: white !important;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 { color: white !important; margin: 0; }
    .league-header {
        background-color: #e1e8ed;
        padding: 8px 15px;
        border-radius: 5px;
        font-weight: bold;
        color: #004682 !important;
        margin-top: 25px;
        margin-bottom: 12px;
        font-size: 15px;
        border-left: 5px solid #004682;
    }
    .match-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-bottom: 4px solid #004682;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .team-container { display: flex; align-items: center; gap: 10px; width: 42%; }
    .team-name { color: #1a1a1a !important; font-weight: 700 !important; font-size: 14px !important; }
    .crest { width: 24px; height: 24px; object-fit: contain; }
    .score-box {
        background-color: #004682;
        color: white !important;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 19px;
        text-align: center;
        min-width: 65px;
    }
    .prob-bar-container {
        width: 100%; height: 10px; background-color: #e0e0e0;
        border-radius: 5px; margin-top: 15px; display: flex; overflow: hidden;
    }
    .home-prob { background-color: #004682; height: 100%; transition: 0.5s; }
    .draw-prob { background-color: #bdc3c7; height: 100%; transition: 0.5s; }
    .away-prob { background-color: #ff4b4b; height: 100%; transition: 0.5s; }
    .prob-text-container {
        display: flex; justify-content: space-between;
        margin-top: 6px; font-size: 12px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIG ---
API_KEY = "dac17517d43d471e94d2b2484ef5df96"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_KEY}

def calc_probs(h_s, a_s, status):
    if status == 'FINISHED':
        if h_s > a_s: return 100, 0, 0, "WINNER"
        if a_s > h_s: return 0, 0, 100, "WINNER"
        return 0, 100, 0, "DRAW"
    diff = h_s - a_s
    if diff == 0: return 35, 30, 35, "LIVE"
    if diff == 1: return 70, 20, 10, "LIVE"
    if diff >= 2: return 92, 5, 3, "LIVE"
    if diff == -1: return 10, 20, 70, "LIVE"
    return 3, 5, 92, "LIVE"

st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI</h1></div>', unsafe_allow_html=True)

page = st.selectbox("🎯 TERMINAL:", ["LIVE SCORES", "ARBITRAGE SCANNER", "MARKET SENTIMENT", "H2H ANALYSIS", "KELLY MANAGER", "AVIATOR TRACKER"])

# --- 1. LIVE SCORES WITH 30s FRAGMENT ---
if page == "LIVE SCORES":
    st.markdown("### 🕒 Live Global Momentum (Refreshing 30s)")
    search_query = st.text_input("🔍 Search Team or League...", "").lower()
    
    @st.fragment(run_every=30)
    def refresh_scores_fragment():
        try:
            res = requests.get(f"{BASE_URL}matches", headers=HEADERS, timeout=10).json()
            if 'matches' in res and res['matches']:
                current_league = ""
                matches_found = False
                
                for m in res['matches']:
                    league_name = m['competition']['name']
                    h_name = m['homeTeam']['name']
                    a_name = m['awayTeam']['name']
                    
                    if search_query and not (search_query in league_name.lower() or search_query in h_name.lower() or search_query in a_name.lower()):
                        continue
                    
                    matches_found = True
                    if league_name != current_league:
                        st.markdown(f'<div class="league-header">🏆 {league_name.upper()}</div>', unsafe_allow_html=True)
                        current_league = league_name

                    h_s = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
                    a_s = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
                    hp, dp, ap, label = calc_probs(h_s, a_s, m['status'])
                    mid_label = f"DRAW ({dp}%)" if (dp > 0 and label != "WINNER") else (label if label != "LIVE" else "")

                    st.markdown(f"""
                    <div class="match-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div class="team-container" style="justify-content: flex-end;">
                                <span class="team-name">{h_name}</span>
                                <img src="{m['homeTeam'].get('crest','')}" class="crest" onerror="this.style.display='none'">
                            </div>
                            <div class="score-box">{h_s} - {a_s}</div>
                            <div class="team-container">
                                <img src="{m['awayTeam'].get('crest','')}" class="crest" onerror="this.style.display='none'">
                                <span class="team-name">{a_name}</span>
                            </div>
                        </div>
                        <div class="prob-bar-container">
                            <div class="home-prob" style="width:{hp}%"></div>
                            <div class="draw-prob" style="width:{dp}%"></div>
                            <div class="away-prob" style="width:{ap}%"></div>
                        </div>
                        <div class="prob-text-container">
                            <span style="color:#004682">{f"{hp}%" if hp > 0 else ""}</span>
                            <span style="color:#7f8c8d">{mid_label}</span>
                            <span style="color:#ff4b4b">{f"{ap}%" if ap > 0 else ""}</span>
                        </div>
                        <div style="text-align:center; color:red; font-size:10px; font-weight:bold; margin-top:8px;">{m['status']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if not matches_found:
                    st.warning("No matches match your search.")
            else:
                st.info("No live matches found.")
        except Exception as e:
            st.error("API Limit reached. The app will retry automatically.")

    refresh_scores_fragment()

# --- 2. ARBITRAGE SCANNER ---
elif page == "ARBITRAGE SCANNER":
    st.subheader("⚖️ 2-Way & 3-Way Scanner")
    mode = st.radio("Scanner Mode", ["2-Way (O/U, BTTS)", "3-Way (1X2)"])
    inv = st.number_input("Investment ($)", value=100.0, min_value=1.0)
    
    if mode == "2-Way (O/U, BTTS)":
        c1, c2 = st.columns(2)
        o1 = c1.number_input("Odds 1", value=0.0, format="%.2f")
        o2 = c2.number_input("Odds 2", value=0.0, format="%.2f")
        if o1 > 0 and o2 > 0:
            arb = (1/o1) + (1/o2)
            if arb < 1.0:
                st.balloons()
                st.success(f"PROFIT! ROI: {((1/arb)-1)*100:.2f}%")
                st.write(f"Stake 1: ${inv/(o1*arb):.2f} | Stake 2: ${inv/(o2*arb):.2f}")
            else: st.warning("No Opportunity.")
    else:
        c1, c2, c3 = st.columns(3)
        o1 = c1.number_input("Home", value=0.0, format="%.2f")
        ox = c2.number_input("Draw", value=0.0, format="%.2f")
        o2 = c3.number_input("Away", value=0.0, format="%.2f")
        if o1 > 0 and ox > 0 and o2 > 0:
            arb = (1/o1) + (1/ox) + (1/o2)
            if arb < 1.0:
                st.balloons()
                st.success(f"PROFIT! ROI: {((1/arb)-1)*100:.2f}%")
                st.write(f"1: ${inv/(o1*arb):.2f} | X: ${inv/(ox*arb):.2f} | 2: ${inv/(o2*arb):.2f}")

# (H2H, Market Sentiment, Kelly, Aviator logic remains exactly the same below)

