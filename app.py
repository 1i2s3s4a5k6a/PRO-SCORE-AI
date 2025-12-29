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
    
    .team-container { display: flex; align-items: center; gap: 10px; width: 40%; }
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
    if diff == 0: return 35, 30, 35, "IN-PLAY"
    if diff == 1: return 70, 20, 10, "IN-PLAY"
    if diff >= 2: return 92, 5, 3, "IN-PLAY"
    if diff == -1: return 10, 20, 70, "IN-PLAY"
    return 3, 5, 92, "IN-PLAY"

st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI</h1></div>', unsafe_allow_html=True)

page = st.selectbox("🎯 TERMINAL:", ["LIVE SCORES", "ARBITRAGE SCANNER", "MARKET SENTIMENT", "H2H ANALYSIS", "KELLY MANAGER", "AVIATOR TRACKER"])

# --- 1. LIVE SCORES (FIXED INDENTATION) ---
if page == "LIVE SCORES":
    st.markdown("### 🕒 Global Real-Time Board")
    @st.fragment(run_every=60)
    def live_board():
        try:
            res = requests.get(f"{BASE_URL}matches", headers=HEADERS).json()
            if 'matches' in res and res['matches']:
                current_league = ""
                for m in res['matches']:
                    league_name = m['competition']['name']
                    
                    if league_name != current_league:
                        st.markdown(f'<div class="league-header">🏆 {league_name.upper()}</div>', unsafe_allow_html=True)
                        current_league = league_name

                    h, a = m['homeTeam'], m['awayTeam']
                    h_s = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
                    a_s = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
                    hp, dp, ap, label = calc_probs(h_s, a_s, m['status'])
                    
                    # Logic to clean up Draw labels for winners
                    mid_label = f"DRAW ({dp}%)" if (dp > 0 and label != "WINNER") else (label if label != "IN-PLAY" else "")

                    st.markdown(f"""
                        <div class="match-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div class="team-container" style="justify-content: flex-end;">
                                    <span class="team-name">{h['name']}</span>
                                    <img src="{h.get('crest','')}" class="crest" onerror="this.style.display='none'">
                                </div>
                                <div class="score-box">{h_s} - {a_s}</div>
                                <div class="team-container">
                                    <img src="{a.get('crest','')}" class="crest" onerror="this.style.display='none'">
                                    <span class="team-name">{a['name']}</span>
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
            else:
                st.info("No live matches found in official leagues right now.")
        except Exception as e:
            st.error("API is cooling down. Refreshing in 60s...")
    live_board()

# --- OTHER PAGES ---
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

elif page == "MARKET SENTIMENT":
    st.subheader("📰 AI News Vibe Check")
    try:
        n_res = requests.get("https://api.rss2json.com/v1/api.json?rss_url=https://www.skysports.com/rss/12040").json()
        for i in n_res['items'][:6]:
            mood = "🟢 POSITIVE" if TextBlob(i['title']).sentiment.polarity > 0.1 else "⚪ NEUTRAL"
            with st.expander(f"{mood} | {i['title']}"): st.write(i['description'])
    except: st.error("Feed busy.")

elif page == "H2H ANALYSIS":
    st.subheader("⚽ History Deep-Dive")
    league = st.selectbox("League", ["PL", "PD", "SA", "BL1", "FL1"])
    try:
        t_res = requests.get(f"{BASE_URL}competitions/{league}/teams", headers=HEADERS).json()
        t_map = {t['name']: t['id'] for t in t_res['teams']}
        t1 = st.selectbox("Team 1", list(t_map.keys()))
        t2 = st.selectbox("Team 2", list(t_map.keys()), index=1)
        if st.button("RUN"):
            res = requests.get(f"{BASE_URL}teams/{t_map[t1]}/matches?competitors={t_map[t2]}", headers=HEADERS).json()
            if 'matches' in res and res['matches']:
                st.table(pd.DataFrame([{"Date": m['utcDate'][:10], "Score": f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}"} for m in res['matches']]))
    except: st.error("Data error.")

elif page == "KELLY MANAGER":
    st.subheader("💰 Risk Manager")
    bank = st.number_input("Bankroll ($)", value=1000.0)
    odds = st.number_input("Odds", value=2.0)
    prob = st.slider("Win %", 1, 100, 52) / 100
    if odds > 1:
        k = (((odds-1)*prob)-(1-prob))/(odds-1)
        if k > 0: st.success(f"Bet: ${bank * k * 0.5:.2f}")

elif page == "AVIATOR TRACKER":
    st.subheader("🛩️ Multiplier Trend")
    raw = st.text_input("Last results (e.g. 1.2, 5.0)", "1.5, 2.0")
    if raw:
        vals = [float(x.strip()) for x in raw.split(",")]
        st.metric("Avg", f"{np.mean(vals):.2f}x")
            if 'matches' in res and res['matches']:
                # Group matches by league for organization
                current_league = ""
                for m in res['matches']:
                    league_name = m['competition']['name'] # This is the full name from API
                    
                    # Add league header when league changes
                    if league_name != current_league:
                        st.markdown(f'<div class="league-header">🏆 {league_name.upper()}</div>', unsafe_allow_html=True)
                        current_league = league_name

                    h, a = m['homeTeam'], m['awayTeam']
                    h_s = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
                    a_s = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
                    hp, dp, ap, label = calc_probs(h_s, a_s, m['status'])
                    
                    st.markdown(f"""
                        <div class="match-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div class="team-container" style="justify-content: flex-end;"><span class="team-name">{h['name']}</span><img src="{h.get('crest','')}" class="crest"></div>
                                <div class="score-box">{h_s} - {a_s}</div>
                                <div class="team-container"><img src="{a.get('crest','')}" class="crest"><span class="team-name">{a['name']}</span></div>
                            </div>
                            <div class="prob-bar-container"><div class="home-prob" style="width:{hp}%"></div><div class="draw-prob" style="width:{dp}%"></div><div class="away-prob" style="width:{ap}%"></div></div>
                            <div class="prob-text-container">
                                <span style="color:#004682">{f"{hp}%" if hp > 0 else ""}</span>
                                <span style="color:#7f8c8d">{f"DRAW ({dp}%)" if (dp > 0 and label != 'WINNER') else label if label != 'IN-PLAY' else ""}</span>
                                <span style="color:#ff4b4b">{f"{ap}%" if ap > 0 else ""}</span>
                            </div>
                            <div style="text-align:center; color:red; font-size:10px; font-weight:bold; margin-top:5px;">{m['status']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else: st.info("No official league matches currently in progress.")
        except: st.error("API limit reached or connection busy.")
    live_board()

# --- OTHER PAGES REMAIN THE SAME ---
elif page == "MARKET SENTIMENT":
    st.subheader("📰 AI News Vibe Check")
    try:
        news_url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.skysports.com/rss/12040"
        n_res = requests.get(news_url, timeout=10).json()
        if n_res['status'] == 'ok':
            for i in n_res['items'][:8]:
                blob = TextBlob(i['title'])
                score = blob.sentiment.polarity
                mood = "🟢 POSITIVE" if score > 0.1 else "🔴 NEGATIVE" if score < -0.1 else "⚪ NEUTRAL"
                with st.expander(f"{mood} | {i['title']}"):
                    st.write(i['description'])
    except: st.error("News offline.")

elif page == "ARBITRAGE SCANNER":
    mode = st.radio("Scanner Mode", ["2-Way (O/U, BTTS)", "3-Way (1X2)"])
    inv = st.number_input("Total Investment ($)", value=100.0, min_value=1.0)
    if mode == "2-Way (O/U, BTTS)":
        c1, c2 = st.columns(2)
        o1, o2 = c1.number_input("Outcome 1"), c2.number_input("Outcome 2")
        if o1 > 0 and o2 > 0:
            arb = (1/o1) + (1/o2)
            if arb < 1.0:
                st.success(f"PROFIT! ROI: {((1/arb)-1)*100:.2f}%")
                st.write(f"Bet 1: ${inv/(o1*arb):.2f} | Bet 2: ${inv/(o2*arb):.2f}")
    else:
        c1, c2, c3 = st.columns(3)
        o1, ox, o2 = c1.number_input("1"), c2.number_input("X"), c3.number_input("2")
        if o1 > 0 and ox > 0 and o2 > 0:
            arb = (1/o1) + (1/ox) + (1/o2)
            if arb < 1.0:
                st.success(f"PROFIT! ROI: {((1/arb)-1)*100:.2f}%")
                st.write(f"1: ${inv/(o1*arb):.2f} | X: ${inv/(ox*arb):.2f} | 2: ${inv/(o2*arb):.2f}")

# (H2H, Kelly, Aviator logic goes here)
                    
                    st.markdown(f"""
                        <div class="match-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div class="team-container" style="justify-content: flex-end;"><span class="team-name">{h['name']}</span><img src="{h.get('crest','')}" class="crest"></div>
                                <div class="score-box">{h_s} - {a_s}</div>
                                <div class="team-container"><img src="{a.get('crest','')}" class="crest"><span class="team-name">{a['name']}</span></div>
                            </div>
                            <div class="prob-bar-container"><div class="home-prob" style="width:{hp}%"></div><div class="draw-prob" style="width:{dp}%"></div><div class="away-prob" style="width:{ap}%"></div></div>
                            <div class="prob-text-container">
                                <span style="color:#004682">{f"{hp}%" if hp > 0 else ""}</span>
                                <span style="color:#7f8c8d">{f"DRAW ({dp}%)" if (dp > 0 and label != 'WINNER') else label if label != 'IN-PLAY' else ""}</span>
                                <span style="color:#ff4b4b">{f"{ap}%" if ap > 0 else ""}</span>
                            </div>
                            <div style="text-align:center; color:red; font-size:10px; font-weight:bold; margin-top:5px;">{m['status']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else: st.info("No matches live.")
        except: st.error("API Connection Busy.")
    live_board()

# FIXED: More stable RSS feed for sentiment
elif page == "MARKET SENTIMENT":
    st.subheader("📰 AI News Vibe Check")
    try:
        # Switching to a more reliable feed provider
        news_url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.skysports.com/rss/12040"
        n_res = requests.get(news_url, timeout=10).json()
        if n_res['status'] == 'ok':
            for i in n_res['items'][:8]:
                blob = TextBlob(i['title'])
                score = blob.sentiment.polarity
                mood = "🟢 POSITIVE" if score > 0.1 else "🔴 NEGATIVE" if score < -0.1 else "⚪ NEUTRAL"
                with st.expander(f"{mood} | {i['title']}"):
                    st.write(i['description'])
                    st.caption(f"Source: {i['author']} | {i['pubDate']}")
        else:
            st.warning("News servers are temporarily busy. Please try again in a moment.")
    except Exception as e:
        st.error("News feed connection failed. Check your internet connection.")

elif page == "ARBITRAGE SCANNER":
    mode = st.radio("Scanner Mode", ["2-Way (O/U, BTTS)", "3-Way (1X2)"])
    inv = st.number_input("Total Investment ($)", value=100.0, min_value=1.0)
    
    if mode == "2-Way (O/U, BTTS)":
        c1, c2 = st.columns(2)
        o1 = c1.number_input("Outcome 1 Odds", value=0.0, min_value=0.0)
        o2 = c2.number_input("Outcome 2 Odds", value=0.0, min_value=0.0)
        if o1 > 0 and o2 > 0:
            arb = (1/o1) + (1/o2)
            if arb < 1.0:
                st.balloons()
                st.success(f"PROFIT! ROI: {((1/arb)-1)*100:.2f}%")
                st.write(f"Bet 1: ${inv/(o1*arb):.2f} | Bet 2: ${inv/(o2*arb):.2f}")
            else: st.warning("No Arbitrage Opportunity.")
        else: st.info("Enter odds greater than 0.")
        
    else:
        c1, c2, c3 = st.columns(3)
        o1 = c1.number_input("Home (1) Odds", value=0.0, min_value=0.0)
        ox = c2.number_input("Draw (X) Odds", value=0.0, min_value=0.0)
        o2 = c3.number_input("Away (2) Odds", value=0.0, min_value=0.0)
        if o1 > 0 and ox > 0 and o2 > 0:
            arb = (1/o1) + (1/ox) + (1/o2)
            if arb < 1.0:
                st.balloons()
                st.success(f"PROFIT! ROI: {((1/arb)-1)*100:.2f}%")
                st.write(f"1: ${inv/(o1*arb):.2f} | X: ${inv/(ox*arb):.2f} | 2: ${inv/(o2*arb):.2f}")
            else: st.warning("No Arbitrage Opportunity.")
        else: st.info("Enter all odds.")

# --- Keep H2H, Kelly, and Aviator blocks here ---

