import streamlit as st
import requests
import pandas as pd
import numpy as np
import math
from textblob import TextBlob
import nltk

# --- THEME & STYLING ---
st.set_page_config(page_title="ProScore AI", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for that Sofascore/Flashscore look
st.markdown("""
    <style>
    /* Main background and font */
    .stApp { background-color: #f8f9fa; }
    
    /* Header styling */
    .main-header {
        background-color: #004682; /* Deep Blue */
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Card styling for matches */
    .match-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #004682;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] { color: #004682; font-weight: bold; }
    
    /* Button styling */
    .stButton>button {
        background-color: #004682;
        color: white;
        border-radius: 20px;
        width: 100%;
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
st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI</h1><p>Live Intelligence & Betting Strategy</p></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
page = st.selectbox("⚡ SELECT TERMINAL:", 
                    ["LIVE SCORES", "H2H ANALYSIS", "MARKET SENTIMENT", "ARBITRAGE SCANNER", "KELLY MANAGER", "AVIATOR TRACKER"])

# --- 1. LIVE SCORES (SOFASCORE STYLE) ---
if page == "LIVE SCORES":
    st.subheader("🕒 Real-Time Board")
    
    @st.fragment(run_every=60)
    def live_board():
        try:
            res = requests.get(f"{BASE_URL}matches", headers=HEADERS).json()
            if 'matches' in res and res['matches']:
                for m in res['matches']:
                    home = m['homeTeam']['name']
                    away = m['awayTeam']['name']
                    h_score = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
                    a_score = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
                    status = m['status']
                    
                    # Creating a "Card" for each match
                    st.markdown(f"""
                        <div class="match-card">
                            <table style="width:100%">
                                <tr>
                                    <td style="width:10%; color:red; font-weight:bold;">{status}</td>
                                    <td style="width:35%; text-align:right;">{home}</td>
                                    <td style="width:20%; text-align:center; background:#004682; color:white; border-radius:5px; font-size:20px;">{h_score} - {a_score}</td>
                                    <td style="width:35%; text-align:left;">{away}</td>
                                </tr>
                            </table>
                        </div>
                    """, unsafe_allow_html=True)
                st.caption(f"Last updated: {pd.Timestamp.now().strftime('%H:%M:%S')}")
            else: st.info("No active matches found.")
        except: st.error("Connection lag...")
    live_board()

# --- 4. ARBITRAGE SCANNER (CLEAN INTERFACE) ---
elif page == "ARBITRAGE SCANNER":
    st.markdown("### ⚖️ Arbi-Scan Tool")
    with st.container(border=True):
        inv = st.number_input("Total Investment ($)", value=100.0)
        c1, c2, c3 = st.columns(3)
        o1 = c1.number_input("Home (1)", value=2.10)
        ox = c2.number_input("Draw (X)", value=3.20)
        o2 = c3.number_input("Away (2)", value=4.50)
        
        arb_pct = (1/o1) + (1/ox) + (1/o2)
        if arb_pct < 1.0:
            profit = (inv / arb_pct) - inv
            st.balloons()
            st.success(f"PROFIT DETECTED: +${profit:.2f}")
            st.info(f"Home: ${inv/(o1*arb_pct):.2f} | Draw: ${inv/(ox*arb_pct):.2f} | Away: ${inv/(o2*arb_pct):.2f}")
        else:
            st.warning(f"Market Efficiency: {arb_pct*100:.1f}%. No Gap.")

# ... (Previous H2H, Sentiment, Bankroll, and Aviator logic stays here, but wrapped in similar 'st.container' boxes)
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

