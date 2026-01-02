import streamlit as st
import requests
import pandas as pd
import sqlite3
import hashlib
import os
import math
import numpy as np
from streamlit_autorefresh import st_autorefresh

# ======================================================
# 1. SYSTEM UI & HIGH-CONTRAST VISIBILITY FIX
# ======================================================
st.set_page_config(
    page_title="ProScore AI | Sharp Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Styles */
    .stApp { background:#f4f7f9; color:#1a1a1a; font-family: 'Inter', sans-serif; }
    
    /* CRITICAL VISIBILITY FIX: Forces black text on white inputs */
    input { color: #000000 !important; background-color: #ffffff !important; font-weight: 700 !important; }
    .stNumberInput div div input { color: #000000 !important; border: 1px solid #00468c !important; }
    .stTextInput div div input { color: #000000 !important; border: 1px solid #00468c !important; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background:#003366 !important; color: white !important; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: white !important; font-weight: 600; }
    
    /* Component Styles */
    .league-header { background: #00468c; color: white; padding: 12px; border-radius: 8px 8px 0 0; font-weight: bold; }
    .score-card { background: #ffffff; border-radius: 0 0 8px 8px; padding: 20px; margin-bottom: 15px; border: 1px solid #d1d8e0; color: #1a1a1a; }
    .score-box { font-size: 32px; font-weight: 900; color: #00468c; font-family: 'Courier New', monospace; }
    .roi-badge { background:#00c853; color:white; padding:5px 12px; border-radius:6px; font-weight:bold; }
    .tool-header { color: #003366; border-left: 6px solid #00468c; padding-left: 12px; margin-bottom: 20px; font-weight: 800; }
    
    /* Tab Navigation Contrast */
    .stTabs [data-baseweb="tab"] { color: #1a1a1a !important; background: #e2e8f0; border-radius: 5px 5px 0 0; margin-right: 5px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background: #00468c !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 2. CORE ANALYTICAL ENGINES
# ======================================================
DB = "proscore_final_2026.db"
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS profits (email TEXT, profit REAL, date DATE DEFAULT CURRENT_DATE)")
    conn.commit()
    conn.close()

init_db()

def calculate_arbitrage(bankroll, odds):
    if not odds or any(o <= 1 for o in odds): return None
    margin = sum(1 / o for o in odds)
    if margin >= 1: return None 
    stakes = [(bankroll * (1 / o)) / margin for o in odds]
    profit = (bankroll / margin) - bankroll
    return [round(s, 2) for s in stakes], round((profit/bankroll)*100, 2), round(profit, 2)

def poisson_prob(lmbda, x):
    return (math.exp(-lmbda) * (lmbda**x)) / math.factorial(x)

# ======================================================
# 3. SIDEBAR & ACCESS CONTROL
# ======================================================
st_autorefresh(interval=60000, key="global_refresh")

with st.sidebar:
    st.markdown("## 🛰️ PRO-SCORE AI")
    license_key = st.text_input("License Key (Optional)", placeholder="Enter key for Elite Tools")
    user_status = "ELITE" if license_key == "SHARP-99" else "GUEST"
    st.caption(f"Access Level: {user_status}")
    
    menu = st.radio("SELECT HUB", ["📡 SCANNER", "⚽ LIVE CENTER", "🧮 SHARP SUITE", "📊 TRACKER"])
    st.divider()
    st.info("System Online: 2026-01-02")

# ======================================================
# 4. HUB MODULES
# ======================================================

if menu == "📡 SCANNER":
    st.markdown("<h2 class='tool-header'>📡 Live Global Intelligence</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class='score-card'><div class='league-header'>Premier League Arb</div>
            <b>Liverpool vs Arsenal</b><br>H Win: 2.18 (Pinnacle) | D/A: 2.08 (1xBet)<br>
            <span class='roi-badge'>ROI: 6.22%</span></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class='score-card'><div class='league-header'>Steam Detector</div>
            <b>Golden State vs Celtics</b><br>Moneyline: GS dropping 1.95 -> 1.72<br>
            <span style='color:red; font-weight:bold;'>🔥 SHARP MONEY FLOW</span></div>""", unsafe_allow_html=True)

elif menu == "⚽ LIVE CENTER":
    st.markdown("<h2 class='tool-header'>⚽ Real-Time Match Analytics</h2>", unsafe_allow_html=True)
    st.markdown("""<div class='score-card'>
        <div style='display:flex; justify-content:space-between;'><b>UEFA CL</b> <span>78'</span></div>
        <div style='text-align:center; padding:15px;'><span class='score-box'>PSG 1 - 2 Bayern</span></div>
        <div style='font-size:13px; color:#555;'>Total xG: 2.45 | Pressure: High (Away)</div>
        </div>""", unsafe_allow_html=True)

elif menu == "🧮 SHARP SUITE":
    st.markdown("<h2 class='tool-header'>🧮 Pro Betting Model Suite</h2>", unsafe_allow_html=True)
    
    t = st.tabs(["💰 Arb/EV", "📈 Risk", "⚽ Goals", "🏀 NBA", "🧠 Market", "🔗 Correlation", "🎯 Efficiency"])

    with t[0]: # Arb & EV
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("+EV Calculator")
            s_o = st.number_input("Soft Odds", 1.01, 50.0, 2.10, key="seo")
            sh_o = st.number_input("Fair Odds", 1.01, 50.0, 2.00, key="sho")
            st.metric("Expected Value", f"{round(((s_o/sh_o)-1)*100, 2)}%")
        with c2:
            st.subheader("Manual Arb")
            oa = st.number_input("Odds A", 1.01, 50.0, 2.05, key="marb1")
            ob = st.number_input("Odds B", 1.01, 50.0, 2.05, key="marb2")
            res = calculate_arbitrage(1000, [oa, ob])
            if res: st.success(f"ROI: {res[1]}% | Profit: ${res[2]}")

    with t[1]: # Risk/Kelly
        st.subheader("Kelly Stake Optimizer")
        ko = st.number_input("Decimal Odds", 1.01, 50.0, 2.00, key="kod")
        kw = st.slider("Win Probability %", 1, 99, 52)/100
        kf = ((ko-1)*kw - (1-kw))/(ko-1)
        st.metric("Stake %", f"{max(0, round(kf*100, 2))}%")
        
        st.divider()
        st.subheader("Bankroll Path Simulator")
        
        wr = st.slider("Win Rate %", 1, 100, 55)/100
        paths = [np.cumsum([1 if np.random.random() < wr else -1 for _ in range(50)]) + 100 for _ in range(10)]
        st.line_chart(np.transpose(paths))

    with t[2]: # Goals
        st.subheader("Poisson Score Matrix")
        
        c_p1, c_p2 = st.columns(2)
        h_xg = c_p1.number_input("Home xG", 0.0, 5.0, 1.8)
        a_xg = c_p2.number_input("Away xG", 0.0, 5.0, 1.3)
        st.write(f"0-0 CS Prob: {round(poisson_prob(h_xg,0)*poisson_prob(a_xg,0)*100, 2)}%")
        
        st.divider()
        st.subheader("Referee Card Bias")
        ref_avg = st.number_input("Ref Avg Yellows", 0.0, 10.0, 4.5)
        st.warning("OVER BIAS" if ref_avg > 4.2 else "UNDER BIAS")

    with t[3]: # NBA
        st.subheader("NBA Clutch Win Edge")
        c_pct = st.slider("Home Clutch Win %", 0, 100, 58)
        pos = st.radio("Ball Possession", ["Home", "Away"])
        if c_pct > 60 and pos == "Home": st.success("🎯 CLUTCH EDGE DETECTED")
        
        st.divider()
        st.subheader("Prop Consistency (CV%)")
        prop_in = st.text_input("Player Last 10 Stats", "22, 19, 25, 21, 20")
        try:
            pts = [float(x.strip()) for x in prop_in.split(",")]
            cv = (np.std(pts)/np.mean(pts))*100
            st.metric("Consistency (CV%)", f"{round(cv,1)}%")
        except: st.error("Format: 22, 19, 25...")

    with t[4]: # Market Depth & Fatigue
        st.subheader("Market Momentum (Steam)")
        
        o_o = st.number_input("Opening Line", 1.0, 10.0, 2.0, key="ml1")
        c_o = st.number_input("Current Line", 1.0, 10.0, 1.8, key="ml2")
        drop = ((o_o-c_o)/o_o)*100
        st.metric("Steam Drop", f"-{round(drop,1)}%", delta="SHARP MOVE" if drop > 5 else "STABLE")
        
        st.divider()
        st.subheader("Market Depth Analyzer")
        exchange_vol = st.number_input("Exchange Volume ($)", 0, 1000000, 50000)
        bookie_max = st.number_input("Bookie Max Stake ($)", 1, 10000, 500)
        liquidity = (exchange_vol / bookie_max) / 100
        st.metric("Liquidity Index", round(liquidity, 2), delta="Liquid" if liquidity > 1 else "Illiquid")

    with t[5]: # Correlation
        st.subheader("Soccer Parlay Correlation")
        
        wp = st.slider("Team Win Prob %", 1, 99, 50)/100
        op = st.slider("Over 2.5 Prob %", 1, 99, 55)/100
        jp = (wp * op) + 0.15 * math.sqrt(wp*(1-wp)*op*(1-op))
        st.metric("Fair Correlated Odds", round(1/jp, 2))

    with t[6]: # Efficiency
        st.subheader("Goal Efficiency Index")
        ag = st.number_input("Actual Goals (Last 5)", 0, 20, 6)
        xg = st.number_input("xG (Last 5)", 0.1, 20.0, 9.2)
        eff = (ag / xg) * 100
        if eff < 85: st.success(f"Efficiency: {round(eff,1)}% - UNLUCKY (Potential Value)")
        elif eff > 115: st.error(f"Efficiency: {round(eff,1)}% - OVERPERFORMING (Potential Fade)")

elif menu == "📊 TRACKER":
    st.markdown("<h2 class='tool-header'>📊 Session Growth Log</h2>", unsafe_allow_html=True)
    p = st.number_input("Session Result ($)", value=0.0)
    if st.button("Save To DB"):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO profits (email, profit) VALUES (?,?)", ("guest", p))
        conn.commit()
        conn.close()
        st.success("Result Logged Locally.")
    
