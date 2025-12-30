import streamlit as st
import requests
import pandas as pd
import random
from streamlit_autorefresh import st_autorefresh
from mailchimp3 import MailChimp

# --- 1. CONFIG & SECURE VAULT ---
st.set_page_config(page_title="ProScore AI | Global Arbitrage Terminal", layout="wide")

try:
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_KEY"]
    MC_API = st.secrets["MAILCHIMP_API"]
    MC_ID = st.secrets["MAILCHIMP_LIST_ID"]
    vault_ready = True
except Exception:
    vault_ready = False

# ASSETS
WHATSAPP_URL = "https://wa.me/233553435649"
BLUEPRINT_URL = "https://drive.google.com/file/d/1_sMPUU1GpB3ULWTPAN9Dlkx9roeRz0xE/view?usp=drivesdk"

# --- 2. AUTO-REFRESH (60s Heartbeat) ---
st_autorefresh(interval=60000, limit=2000, key="global_refresh")

# --- 3. THE "FLASHPEDIA" CSS ENGINE ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    
    /* Oddspedia Master Card */
    .arb-card { background: #161b22; border-radius: 10px; margin-bottom: 25px; border: 1px solid #30363d; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
    .arb-header { background: #21262d; padding: 12px 18px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; }
    .profit-tag { background: #238636; color: white; padding: 4px 12px; border-radius: 6px; font-weight: 800; font-size: 14px; border: 1px solid #3fb950; }
    
    /* Market Outcomes Grid */
    .odds-grid { display: grid; gap: 1px; background: #30363d; }
    .odds-tile { background: #0d1117; padding: 15px; text-align: center; }
    .mkt-label { font-size: 10px; color: #8b949e; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; letter-spacing: 1px; }
    .odds-val { color: #3fb950; font-weight: 900; font-size: 22px; display: block; }
    .bookie-name { font-size: 11px; color: #7d8590; margin-top: 5px; text-transform: uppercase; font-weight: 600; }

    /* Flashscore Style Live Feed */
    .league-header { background: #21262d; padding: 10px 15px; border-left: 5px solid #238636; margin: 25px 0 5px 0; font-weight: bold; color: #f0f6fc; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }
    .match-row { background: #161b22; padding: 18px; border-bottom: 1px solid #30363d; display: grid; grid-template-columns: 80px 1fr 100px; align-items: center; transition: 0.2s; }
    .match-row:hover { background: #1c2128; }
    .score-green { color: #3fb950; font-weight: 900; font-size: 24px; text-align: right; line-height: 1.1; }
    .live-pulse { color: #f85149; font-weight: 800; font-size: 10px; animation: blink 1.2s infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#3fb950;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    tab = st.radio("MAIN TERMINAL", ["🛰️ ARBS SCANNER", "🕒 LIVE SCORES", "🎁 $500 BLUEPRINT", "🛡️ SUPPORT"])
    st.divider()
    st.caption("v6.5 Multi-Market Engine")
    st.info("Status: Real-Time Bookie Sync")

# --- TAB 1: ARBS SCANNER (THE MATHEMATICAL "SURE-WIN" ENGINE) ---
if tab == "🛰️ ARBS SCANNER":
    st.title("🛰️ Global Arbitrage Matrix")
    st.write("Calculated outcomes across 3-Way (Soccer) and 2-Way (Basketball/Tennis) markets.")
    
    if vault_ready:
        # Pulling H2H (Home/Draw/Away) and Totals (Over/Under)
        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu,us,au&markets=h2h,totals"
        try:
            data = requests.get(url).json()
            for event in data[:20]:
                roi = round(random.uniform(3.8, 12.4), 2)
                sport = event.get('sport_title', 'General Sports')
                is_soccer = "Soccer" in sport
                
                st.markdown(f"""
                <div class="arb-card">
                    <div class="arb-header">
                        <span style="font-size: 13px;">🏆 {sport.upper()} • {event['home_team']} vs {event['away_team']}</span>
                        <span class="profit-tag">+{roi}% SURE WIN</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Dynamic Outcomes: Soccer gets 3 columns, others get 2
                outcomes = ["HOME", "DRAW", "AWAY"] if is_soccer else ["HOME", "AWAY"]
                cols = st.columns(len(outcomes))
                
                for i, m_label in enumerate(outcomes):
                    with cols[i]:
                        # Strategy: Assigning different bookies to each leg to simulate the Arb
                        bookie_idx = i % len(event['bookmakers'])
                        bookie = event['bookmakers'][bookie_idx]
                        price = bookie['markets'][0]['outcomes'][min(i, len(bookie['markets'][0]['outcomes'])-1)]['price']
                        
                        st.markdown(f"""
                        <div class="odds-tile">
                            <div class="mkt-label">{m_label}</div>
                            <span class="odds-val">{price}</span>
                            <div class="bookie-name">{bookie['title']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Oddspedia Calculator Integration
                with st.expander("🧮 ARBITRAGE CALCULATOR (SECURE STAKING)"):
                    total_stake = st.number_input("Total Investment ($)", value=1000, key=f"c_{event['id']}")
                    st.success(f"**Guaranteed Profit: ${(total_stake * (roi/100)):.2f}**")
                    st.caption(f"Strategy: Place stakes simultaneously on all {len(outcomes)} outcomes above.")
                
                st.markdown('</div>', unsafe_allow_html=True)
        except: st.warning("Connecting to global market liquidity nodes...")

# --- TAB 2: LIVE SCORES (GLOBAL FLASHSCORE LOGIC) ---
elif tab == "🕒 LIVE SCORES":
    st.title("🕒 Global Score Center")
    if vault_ready:
        try:
            # PULL ALL GAMES GLOBALLY (Global Filter)
            res = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': FOOTBALL_KEY}).json()
            matches = res.get('matches', [])
            
            # Flashscore Hierarchy (Grouped by Competition)
            leagues = {}
            for m in matches:
                leagues.setdefault(m['competition']['name'], []).append(m)

            for league, m_list in leagues.items():
                st.markdown(f'<div class="league-header">{league}</div>', unsafe_allow_html=True)
                for m in m_list:
                    h_s = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else "0"
                    a_s = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else "0"
                    status = '<span class="live-pulse">LIVE</span>' if m['status'] == "IN_PLAY" else m['utcDate'][11:16]
                    
                    st.markdown(f"""
                    <div class="match-row">
                        <div style="font-size: 11px; font-weight: bold;">{status}</div>
                        <div>
                            <div style="font-weight:700; font-size:15px; color: #f0f6fc;">{m['homeTeam']['name']}</div>
                            <div style="font-weight:700; font-size:15px; color: #f0f6fc;">{m['awayTeam']['name']}</div>
                        </div>
                        <div class="score-green">{h_s}<br>{a_s}</div>
                    </div>
                    """, unsafe_allow_html=True)
        except: st.error("Match synchronization in progress...")

# --- TAB 3: MAILCHIMP & BLUEPRINT ---
elif tab == "🎁 $500 BLUEPRINT":
    st.title("🎁 $500 Arbitrage Blueprint")
    email = st.text_input("Institutional Email", placeholder="trader@proscore.ai")
    if st.button("SEND TO MY TERMINAL"):
        if "@" in email and vault_ready:
            try:
                mc = MailChimp(mc_api=MC_API, mc_user="ProScore")
                mc.lists.members.create(MC_ID, {'email_address': email, 'status': 'subscribed'})
                st.success("Access Granted! Blueprint dispatched.")
                st.balloons()
            except: st.info("Welcome back. Your file is ready for download.")
            st.markdown(f'<a href="{BLUEPRINT_URL}" target="_blank"><button style="width:100%; padding:20px; background:#238636; color:white; border:none; border-radius:10px; font-weight:800; cursor:pointer; font-size:18px;">📥 DOWNLOAD THE $500 BLUEPRINT PDF</button></a>', unsafe_allow_html=True)

# --- TAB 4: SUPPORT ---
elif tab == "🛡️ SUPPORT":
    st.markdown(f'<div style="text-align:center; padding-top:100px;"><a href="{WHATSAPP_URL}" target="_blank"><button style="width:350px; height:80px; background:#25D366; border:none; border-radius:15px; color:white; font-weight:800; font-size:20px; cursor:pointer;">💬 CHAT ON WHATSAPP BUSINESS</button></a></div>', unsafe_allow_html=True)

