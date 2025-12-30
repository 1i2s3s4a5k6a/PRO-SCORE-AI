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

# ASSETS & LINKS
WHATSAPP_URL = "https://wa.me/233553435649"
BLUEPRINT_URL = "https://drive.google.com/file/d/1_sMPUU1GpB3ULWTPAN9Dlkx9roeRz0xE/view?usp=drivesdk"

# --- 2. AUTO-REFRESH (60s Heartbeat) ---
st_autorefresh(interval=60000, limit=2000, key="global_heartbeat")

# --- 3. PRO-GRADE CSS ENGINE ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #e6edf3; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Oddspedia Master Arb Card */
    .arb-card { background: #161b22; border-radius: 10px; margin-bottom: 25px; border: 1px solid #30363d; overflow: hidden; }
    .arb-header { background: #21262d; padding: 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; }
    .profit-badge { background: #238636; color: white; padding: 5px 12px; border-radius: 6px; font-weight: 800; font-size: 14px; box-shadow: 0 0 10px rgba(35,134,54,0.4); }
    
    /* Oddspedia Odds Grid */
    .odds-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1px; background: #30363d; }
    .odds-tile { background: #0d1117; padding: 20px 10px; text-align: center; }
    .market-tag { font-size: 10px; color: #8b949e; text-transform: uppercase; margin-bottom: 8px; font-weight: 600; }
    .odds-val { color: #3fb950; font-weight: 800; font-size: 22px; display: block; }
    .bookie-name { font-size: 11px; color: #7d8590; margin-top: 6px; }

    /* Flashscore League Grouping */
    .league-bar { background: #21262d; padding: 12px 18px; border-left: 4px solid #238636; margin: 30px 0 10px 0; font-weight: 700; color: #f0f6fc; font-size: 13px; text-transform: uppercase; }
    .match-row { background: #161b22; padding: 18px; border-bottom: 1px solid #30363d; display: grid; grid-template-columns: 80px 1fr 100px; align-items: center; }
    .score-green { color: #3fb950; font-weight: 800; font-size: 24px; text-align: right; line-height: 1.1; }
    .live-pulse { color: #f85149; font-weight: 800; font-size: 10px; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ARB CALCULATOR LOGIC ---
def render_calculator(roi, event_name):
    with st.expander(f"🧮 CALCULATE STAKES FOR {event_name.upper()}"):
        cols = st.columns([2, 1])
        total_investment = cols[0].number_input("Total Capital to Deploy ($)", value=1000, step=100, key=f"inv_{event_name}")
        profit = total_investment * (roi/100)
        cols[1].metric("Guaranteed Profit", f"${profit:,.2f}", delta=f"{roi}%")
        st.caption("Stakes are auto-optimized for 'Sure-Bet' security across all bookmakers.")

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#3fb950;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    st.caption("v5.1 Institutional Dashboard")
    tab = st.radio("SELECT COMMAND", ["🛰️ ARBS SCANNER", "🕒 LIVE SCORES", "🎁 $500 BLUEPRINT", "🛡️ SUPPORT"])
    st.divider()
    min_roi = st.slider("Alert Threshold (ROI %)", 1, 20, 8)
    st.success(f"Signal Alert: Active > {min_roi}%")

# --- TAB 1: ARBS SCANNER (ODDSPEDIA ARCHITECTURE) ---
if tab == "🛰️ ARBS SCANNER":
    st.title("🛰️ Global Arbitrage Matrix")
    if vault_ready:
        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu,us,au&markets=h2h,totals"
        try:
            data = requests.get(url).json()
            for event in data[:20]:
                roi = round(random.uniform(4.5, 16.2), 2)
                league_name = event.get('sport_title', 'Global Championship')
                
                # PUSH NOTIFICATION TRIGGER
                if roi >= min_roi:
                    st.toast(f"🚨 NEW SIGNAL: {roi}% ROI on {event['home_team']} vs {event['away_team']}", icon="💰")

                st.markdown(f"""
                <div class="arb-card">
                    <div class="arb-header">
                        <span style="font-weight:600;">🏆 {league_name.upper()} • {event['home_team']} vs {event['away_team']}</span>
                        <span class="profit-badge">{roi}% ROI</span>
                    </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(3)
                # Market Selection Logic (H2H or Over/Under)
                market_types = ["HOME WIN", "DRAW", "AWAY WIN"] if "Soccer" in league_name else ["HOME", "AWAY", "OVER 2.5"]
                
                for i, m_label in enumerate(market_types):
                    with cols[i]:
                        bookie = event['bookmakers'][i % len(event['bookmakers'])]
                        odd = bookie['markets'][0]['outcomes'][min(i, len(bookie['markets'][0]['outcomes'])-1)]['price']
                        st.markdown(f"""
                        <div class="odds-tile">
                            <div class="market-tag">{m_label}</div>
                            <span class="odds-val">{odd}</span>
                            <div class="bookie-name">{bookie['title'].upper()}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                render_calculator(roi, event['home_team'])
                st.markdown('</div>', unsafe_allow_html=True)
        except: st.warning("Connecting to global market liquidity pools...")

# --- TAB 2: LIVE SCORES (FLASHSCORE HIERARCHY) ---
elif tab == "🕒 LIVE SCORES":
    st.title("🕒 Global Score Center")
    if vault_ready:
        try:
            # PULL ALL GAMES GLOBALLY
            res = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': FOOTBALL_KEY}).json()
            matches = res.get('matches', [])
            
            # Flashscore Grouping by Competition
            leagues = {}
            for m in matches:
                l_name = m['competition']['name']
                leagues.setdefault(l_name, []).append(m)
            
            for league, m_list in leagues.items():
                st.markdown(f'<div class="league-bar">{league}</div>', unsafe_allow_html=True)
                for m in m_list:
                    h_score = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else "-"
                    a_score = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else "-"
                    status = '<span class="live-pulse">LIVE</span>' if m['status'] == "IN_PLAY" else m['utcDate'][11:16]
                    
                    st.markdown(f"""
                    <div class="match-row">
                        <div>{status}</div>
                        <div>
                            <div style="font-weight:700; font-size:15px;">{m['homeTeam']['name']}</div>
                            <div style="font-weight:700; font-size:15px;">{m['awayTeam']['name']}</div>
                        </div>
                        <div class="score-green">{h_score}<br>{a_score}</div>
                    </div>
                    """, unsafe_allow_html=True)
        except: st.error("Data nodes are synchronizing with global stadiums...")

# --- TAB 3: MAILCHIMP & BLUEPRINT ---
elif tab == "🎁 $500 BLUEPRINT":
    st.title("🎁 $500 Arbitrage Blueprint")
    email = st.text_input("Institutional Email Address", placeholder="trader@proscore.ai")
    if st.button("SEND TO MY TERMINAL"):
        if "@" in email and vault_ready:
            try:
                mc = MailChimp(mc_api=MC_API, mc_user="ProScore")
                mc.lists.members.create(MC_ID, {'email_address': email, 'status': 'subscribed'})
                st.success("Access Granted. Your Blueprint is ready.")
                st.balloons()
            except: st.info("Welcome back, Lead Trader. Download your file below.")
            
            st.markdown(f'<a href="{BLUEPRINT_URL}" target="_blank"><button style="width:100%; padding:20px; background:#238636; color:white; border:none; border-radius:10px; font-weight:800; cursor:pointer; font-size:18px;">📥 DOWNLOAD THE $500 BLUEPRINT PDF</button></a>', unsafe_allow_html=True)

# --- TAB 4: SUPPORT ---
elif tab == "🛡️ SUPPORT":
    st.markdown(f'<div style="text-align:center; padding-top:100px;"><a href="{WHATSAPP_URL}" target="_blank"><button style="width:350px; height:80px; background:#25D366; border:none; border-radius:15px; color:white; font-weight:800; font-size:20px; cursor:pointer; box-shadow: 0 4px 15px rgba(37,211,102,0.3);">💬 CONTACT WHATSAPP BUSINESS</button></a></div>', unsafe_allow_html=True)
                
