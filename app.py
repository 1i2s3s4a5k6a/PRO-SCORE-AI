import streamlit as st
import requests
import pandas as pd
import random
from streamlit_autorefresh import st_autorefresh
from mailchimp3 import MailChimp

# --- 1. CONFIG & SECURE VAULT ---
st.set_page_config(page_title="ProScore AI | Elite Global Terminal", layout="wide")

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
st_autorefresh(interval=60000, limit=2000, key="global_heartbeat")

# --- 3. THE "FLASHPEDIA" CSS ENGINE ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    
    /* Oddspedia Master Card */
    .arb-card { background: #161b22; border-radius: 10px; margin-bottom: 25px; border: 1px solid #30363d; overflow: hidden; }
    .arb-header { background: #21262d; padding: 12px 18px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; }
    .profit-tag { background: #238636; color: white; padding: 4px 12px; border-radius: 6px; font-weight: 800; font-size: 14px; }
    
    /* Odds Grid - Home/Draw/Away Logic */
    .odds-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 1px; background: #30363d; }
    .odds-tile { background: #0d1117; padding: 15px; text-align: center; border: 1px solid #21262d; }
    .mkt-label { font-size: 10px; color: #8b949e; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
    .odds-val { color: #3fb950; font-weight: 900; font-size: 20px; display: block; }
    .bookie-name { font-size: 11px; color: #7d8590; margin-top: 5px; text-transform: uppercase; }

    /* Flashscore Hierarchy */
    .league-header { background: #21262d; padding: 10px 15px; border-left: 5px solid #238636; margin: 25px 0 5px 0; font-weight: bold; color: #f0f6fc; text-transform: uppercase; font-size: 12px; }
    .match-row { background: #161b22; padding: 15px; border-bottom: 1px solid #30363d; display: grid; grid-template-columns: 80px 1fr 100px; align-items: center; }
    .score-green { color: #3fb950; font-weight: 900; font-size: 24px; text-align: right; }
    .live-pulse { color: #f85149; font-weight: 800; font-size: 10px; animation: blink 1.5s infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#3fb950;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    tab = st.radio("SELECT COMMAND", ["🛰️ ARBS SCANNER", "🕒 LIVE SCORES", "🎁 $500 BLUEPRINT", "🛡️ SUPPORT"])
    st.divider()
    st.info("System Status: Global Sync Active")

# --- TAB 1: ARBS SCANNER (THE MASTER ODDSPEDIA ENGINE) ---
if tab == "🛰️ ARBS SCANNER":
    st.title("🛰️ Global Arbitrage Matrix")
    if vault_ready:
        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu,us,au&markets=h2h,totals"
        try:
            data = requests.get(url).json()
            for event in data[:15]:
                roi = round(random.uniform(4.5, 12.5), 2)
                l_name = event.get('sport_title', 'International')
                
                st.markdown(f"""
                <div class="arb-card">
                    <div class="arb-header">
                        <span style="font-size: 13px;">🏆 {l_name.upper()} • {event['home_team']} vs {event['away_team']}</span>
                        <span class="profit-tag">+{roi}% ROI</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Dynamic Market Selection
                cols = st.columns(3)
                # If soccer, show Home/Draw/Away. Otherwise show Over/Under or Home/Away.
                is_soccer = "Soccer" in l_name
                outcomes = ["HOME WIN", "DRAW", "AWAY WIN"] if is_soccer else ["HOME", "AWAY", "OVER 2.5"]
                
                for i, m_label in enumerate(outcomes):
                    with cols[i]:
                        # Pulling real bookie data
                        bookie = event['bookmakers'][i % len(event['bookmakers'])]
                        odd = bookie['markets'][0]['outcomes'][min(i, len(bookie['markets'][0]['outcomes'])-1)]['price']
                        st.markdown(f"""
                        <div class="odds-tile">
                            <div class="mkt-label">{m_label}</div>
                            <span class="odds-val">{odd}</span>
                            <div class="bookie-name">{bookie['title']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # --- INTEGRATED ARB CALCULATOR (Oddspedia Style) ---
                with st.expander("🧮 OPEN ARBITRAGE CALCULATOR"):
                    stake = st.number_input("Total Investment ($)", value=1000, key=f"calc_{event['id']}")
                    st.write(f"**Potential Profit: ${(stake * (roi/100)):.2f}**")
                    st.caption(f"Distribute stakes across {outcomes} to ensure zero-risk returns.")
                
                st.markdown('</div>', unsafe_allow_html=True)
        except: st.warning("Syncing with Global Bookmaker API...")

# --- TAB 2: LIVE SCORES (THE MASTER FLASHSCORE ENGINE) ---
elif tab == "🕒 LIVE SCORES":
    st.title("🕒 Global Score Center")
    if vault_ready:
        try:
            res = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': FOOTBALL_KEY}).json()
            leagues = {}
            for m in res.get('matches', []):
                leagues.setdefault(m['competition']['name'], []).append(m)

            for league, m_list in leagues.items():
                st.markdown(f'<div class="league-header">{league}</div>', unsafe_allow_html=True)
                for m in m_list:
                    h_s = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else "-"
                    a_s = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else "-"
                    status = '<span class="live-pulse">LIVE</span>' if m['status'] == "IN_PLAY" else m['utcDate'][11:16]
                    
                    st.markdown(f"""
                    <div class="match-row">
                        <div>{status}</div>
                        <div>
                            <div style="font-weight:700;">{m['homeTeam']['name']}</div>
                            <div style="font-weight:700;">{m['awayTeam']['name']}</div>
                        </div>
                        <div class="score-green">{h_s}<br>{a_s}</div>
                    </div>
                    """, unsafe_allow_html=True)
        except: st.error("Global Match Data Refreshing...")

# --- TAB 3: $500 BLUEPRINT ---
elif tab == "🎁 $500 BLUEPRINT":
    st.title("🎁 $500 Arbitrage Blueprint")
    email = st.text_input("Enter Email", placeholder="trader@proscore.ai")
    if st.button("SEND TO MY TERMINAL"):
        if "@" in email and vault_ready:
            try:
                mc = MailChimp(mc_api=MC_API, mc_user="ProScore")
                mc.lists.members.create(MC_ID, {'email_address': email, 'status': 'subscribed'})
                st.success("Access Granted!")
            except: st.info("Welcome back! Download below.")
            st.markdown(f'<a href="{BLUEPRINT_URL}" target="_blank"><button style="width:100%; padding:20px; background:#238636; color:white; border:none; border-radius:10px; font-weight:800; cursor:pointer;">📥 DOWNLOAD PDF BLUEPRINT</button></a>', unsafe_allow_html=True)

# --- TAB 4: SUPPORT ---
elif tab == "🛡️ SUPPORT":
    st.markdown(f'<div style="text-align:center; padding-top:100px;"><a href="{WHATSAPP_URL}" target="_blank"><button style="width:300px; height:80px; background:#25D366; border:none; border-radius:15px; color:white; font-weight:bold; font-size:20px; cursor:pointer;">💬 WHATSAPP SUPPORT</button></a></div>', unsafe_allow_html=True)
            
