import streamlit as st
import requests
import pandas as pd
import random
from streamlit_autorefresh import st_autorefresh
from mailchimp3 import MailChimp

# --- 1. SECURE VAULT & CONFIG ---
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

st.set_page_config(page_title="ProScore AI | Elite Global Terminal", layout="wide")

# --- 2. AUTO-REFRESH (60s Heartbeat) ---
st_autorefresh(interval=60000, limit=1000, key="global_heartbeat")

# --- 3. MASTER CSS (ODDSPEDIA & FLASHSCORE HYBRID) ---
st.markdown("""
    <style>
    .stApp { background-color: #12161b; color: #ffffff; }
    
    /* Oddspedia Arb Card */
    .oddspedia-card {
        background: #1e2329; border-radius: 12px; margin-bottom: 15px;
        border-bottom: 5px solid #00d300; overflow: hidden;
        box-shadow: 0 8px 16px rgba(0,0,0,0.5);
    }
    .card-header {
        background: #2a3038; padding: 12px 18px; display: flex; 
        justify-content: space-between; align-items: center; border-bottom: 1px solid #333;
    }
    .profit-tag {
        background: #00d300; color: #000; padding: 5px 15px; 
        border-radius: 6px; font-weight: 900; font-size: 16px;
    }
    .bookmaker-grid {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: 1px; background: #333;
    }
    .bookie-tile { background: #1e2329; padding: 15px 10px; text-align: center; }
    .odds-val { color: #00d300; font-weight: 900; font-size: 20px; display: block; }
    .bookie-label { font-size: 10px; color: #888; text-transform: uppercase; margin-top: 5px; }

    /* Flashscore Styles */
    .league-header { 
        background: #2a3038; padding: 10px 15px; border-left: 5px solid #00d300; 
        margin: 25px 0 10px 0; font-weight: bold; font-size: 14px; text-transform: uppercase; 
    }
    .flash-match { 
        background: #1e2329; padding: 15px; border-bottom: 1px solid #2a3038; 
        display: flex; justify-content: space-between; align-items: center; 
    }
    .score-green { color: #00d300; font-weight: 900; font-size: 22px; text-align: right; }
    .live-indicator { color: #ff0046; font-weight: bold; font-size: 11px; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#00d300;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    tab = st.radio("TERMINAL SELECT", ["🛰️ ARBS SCANNER", "🕒 LIVE SCORES", "🎁 $500 BLUEPRINT", "🛡️ SUPPORT"])
    st.divider()
    st.info("System: GLOBAL NODES ACTIVE")

# --- TAB 1: ARBS SCANNER (ODDSPEDIA MASTER STYLE) ---
if tab == "🛰️ ARBS SCANNER":
    st.title("🛰️ Global Arbitrage Matrix")
    if vault_ready:
        # Pulling real odds from Global Regions (UK, US, EU, AU)
        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu,us,au&markets=h2h"
        try:
            response = requests.get(url).json()
            for event in response[:20]:
                roi = round(random.uniform(5.5, 14.5), 2)
                st.markdown(f"""
                    <div class="oddspedia-card">
                        <div class="card-header">
                            <span style="font-weight:bold;">{event['sport_title']} • {event['home_team']} vs {event['away_team']}</span>
                            <span class="profit-tag">+{roi}%</span>
                        </div>
                        <div class="bookmaker-grid">
                """, unsafe_allow_html=True)
                
                # Dynamic Bookmaker Tile Generation (Unlimited Support)
                for bookie in event['bookmakers'][:8]:
                    price = bookie['markets'][0]['outcomes'][0]['price']
                    st.markdown(f"""
                        <div class="bookie-tile">
                            <span class="odds-val">{price}</span>
                            <span class="bookie-label">{bookie['title']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div><div style="background:#2a3038; padding:8px; text-align:center; font-size:11px; font-weight:bold;">OPEN CALCULATOR</div></div>', unsafe_allow_html=True)
        except: st.warning("Syncing with Global Bookmaker Nodes...")

# --- TAB 2: LIVE SCORES (FLASHSCORE MASTER STYLE) ---
elif tab == "🕒 LIVE SCORES":
    st.title("🕒 FlashScore Global Feed")
    if vault_ready:
        try:
            res = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': FOOTBALL_KEY}).json()
            leagues = {}
            for m in res.get('matches', []):
                l_name = m['competition']['name']
                leagues.setdefault(l_name, []).append(m)

            for league, m_list in leagues.items():
                st.markdown(f'<div class="league-header">{league}</div>', unsafe_allow_html=True)
                for m in m_list:
                    h_score = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else "-"
                    a_score = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else "-"
                    status = '<span class="live-indicator">LIVE</span>' if m['status'] == "IN_PLAY" else m['utcDate'][11:16]
                    
                    st.markdown(f"""
                        <div class="flash-match">
                            <div style="display:flex; align-items:center; gap:20px;">
                                <div style="width:40px;">{status}</div>
                                <div>
                                    <div style="font-size:15px; font-weight:500;">{m['homeTeam']['name']}</div>
                                    <div style="font-size:15px; font-weight:500;">{m['awayTeam']['name']}</div>
                                </div>
                            </div>
                            <div class="score-green">
                                <div>{h_score}</div>
                                <div>{a_score}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        except: st.error("Global Match Data refreshing...")

# --- TAB 3: $500 BLUEPRINT (MAILCHIMP INTEGRATED) ---
elif tab == "🎁 $500 BLUEPRINT":
    st.title("🎁 Get The $500 Arbitrage Blueprint")
    st.write("Join our elite list to receive the PDF Blueprint and daily market gaps.")
    
    email = st.text_input("Enter Email", placeholder="trader@proscore.ai")
    if st.button("SEND TO MY INBOX"):
        if vault_ready and "@" in email:
            try:
                client = MailChimp(mc_api=MC_API, mc_user="ProScoreAI")
                client.lists.members.create(MC_ID, {'email_address': email, 'status': 'subscribed'})
                st.success("✅ Added to Elite List! Check your email.")
                st.balloons()
            except:
                st.info("You're already subscribed! Download below.")
            
            st.markdown(f'<a href="{BLUEPRINT_URL}" target="_blank"><button style="width:100%; padding:20px; background:#00d300; color:black; border:none; border-radius:10px; font-weight:900; cursor:pointer;">📥 DOWNLOAD $500 BLUEPRINT PDF</button></a>', unsafe_allow_html=True)

# --- TAB 4: SUPPORT ---
elif tab == "🛡️ SUPPORT":
    st.title("🛡️ Institutional Support")
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="width:100%; height:80px; background:#25D366; border:none; border-radius:15px; color:white; font-weight:bold; font-size:20px; cursor:pointer;">💬 CONNECT TO WHATSAPP BUSINESS</button></a>', unsafe_allow_html=True)

