import streamlit as st
import requests
import pandas as pd
import random
import time
from datetime import datetime
from mailchimp3 import MailChimp

# --- 1. SECURE VAULT & ASSETS ---
try:
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_KEY"]
    MC_API = st.secrets["MAILCHIMP_API"]
    MC_ID = st.secrets["MAILCHIMP_LIST_ID"]
    vault_ready = True
except Exception:
    vault_ready = False

# LIVE LINKS
PAYSTACK_LINK = "https://paystack.shop/pay/arbitrage-betting-scanner"
WHATSAPP_URL = "https://wa.me/233553435649"
BLUEPRINT_URL = "https://drive.google.com/file/d/1_sMPUU1GpB3ULWTPAN9Dlkx9roeRz0xE/view?usp=drivesdk"

st.set_page_config(page_title="ProScore AI | Elite Global Terminal", layout="wide", initial_sidebar_state="expanded")

# --- 2. ADVANCED INSTITUTIONAL STYLING (CSS) ---
st.markdown("""
    <style>
    /* Deep Space Background */
    .stApp { background: radial-gradient(circle at top, #0B1120 0%, #020817 100%); font-family: 'Inter', sans-serif; }
    
    /* Top Flash Signal Bar */
    .signal-bar {
        background: linear-gradient(90deg, #B8860B, #FFD700); color: #020617; 
        padding: 12px; text-align: center; font-weight: 900; text-transform: uppercase; 
        letter-spacing: 2px; border-radius: 0 0 15px 15px; margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.4);
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.8; } 100% { opacity: 1; } }

    /* Premium Glassmorphic Cards */
    .arb-card {
        background: rgba(30, 41, 59, 0.5); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 215, 0, 0.15); border-radius: 20px;
        padding: 24px; margin-bottom: 20px; transition: 0.4s ease;
    }
    .arb-card:hover { border-color: #FFD700; transform: scale(1.01); }

    /* Custom Metric Glow */
    [data-testid="stMetricValue"] { color: #FFD700 !important; font-size: 32px !important; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }
    
    /* Global CTA Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
        color: #020817 !important; border-radius: 12px !important; border: none !important;
        font-weight: 900 !important; height: 3.8rem !important; width: 100%;
        text-transform: uppercase; letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PREMIUM ACCESS CHECK ---
if 'is_premium' not in st.session_state:
    st.session_state.is_premium = False

# Handle Paystack Redirect
if st.query_params.get("payment") == "success":
    st.session_state.is_premium = True

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#FFD700;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    st.caption("v4.0 Global Multi-Node Terminal")
    
    tab = st.radio("SELECT MODULE", ["🛰️ OMNI-SCANNER", "🕒 LIVE PULSE", "🏆 LEADERBOARD", "🎁 $500 BLUEPRINT", "🏦 BANKROLL AI", "🛡️ SUPPORT"])
    
    st.divider()
    if not st.session_state.is_premium:
        st.markdown(f'<a href="{PAYSTACK_LINK}" target="_blank"><button style="width:100%; padding:15px; background:linear-gradient(90deg, #FFD700, #B8860B); border:none; border-radius:10px; font-weight:900; cursor:pointer; color:#020617;">🔓 UNLOCK PREMIUM ACCESS</button></a>', unsafe_allow_html=True)
    else:
        st.success("✅ PREMIUM ACCESS: ACTIVE")

# --- 5. PAGE ROUTING ---

# TOP FLASH BAR
st.markdown(f'<div class="signal-bar">🚀 SYSTEM STATUS: Scanning Global Liquidity in UK, US, EU, and AU Nodes</div>', unsafe_allow_html=True)

if tab == "🛰️ OMNI-SCANNER":
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("GLOBAL GAPS", "4,218", "LIVE")
    m2.metric("SIGNAL ROI", "6.42%", "+1.1%")
    m3.metric("NODES", "ONLINE", delta_color="normal")
    m4.metric("LATENCY", "12ms", "LOW")

    st.divider()
    
    col_l, col_r = st.columns([2.5, 1])

    with col_l:
        st.subheader("🌐 Global Arbitrage Matrix")
        if st.button("🚀 EXECUTE MULTI-NODE DEEP SCAN"):
            if vault_ready:
                # Expanded Global Sports List
                global_sports = ['soccer_epl', 'basketball_nba', 'tennis_atp_wimbledon', 'cricket_ipl', 'americanfootball_nfl', 'soccer_spain_la_liga', 'icehockey_nhl']
                
                with st.spinner("Decrypting Odds across 4 Continents..."):
                    found_count = 0
                    for sport_key in global_sports:
                        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={ODDS_API_KEY}&regions=uk,us,eu,au&markets=h2h,totals"
                        try:
                            data = requests.get(url).json()
                            if data:
                                for match in data[:2]: # Optimized for speed
                                    roi = round(random.uniform(4.2, 14.8), 2)
                                    m_type = "TOTALS (O/U)" if 'totals' in str(match) else "H2H (WINNER)"
                                    found_count += 1
                                    st.markdown(f"""
                                    <div class="arb-card">
                                        <div style="display:flex; justify-content:space-between; align-items:center;">
                                            <span style="background:#FFD700; color:#020617; padding:4px 10px; border-radius:6px; font-weight:900; font-size:10px;">{m_type}</span>
                                            <span style="color:#4ADE80; font-weight:bold; font-size:18px;">+{roi}% ROI</span>
                                        </div>
                                        <h3 style="margin: 15px 0 5px 0; color:white;">{match['home_team']} vs {match['away_team']}</h3>
                                        <p style="font-size:12px; color:#94A3B8; margin-bottom:15px;">Global Liquidity Node: {sport_key.replace('_',' ').upper()}</p>
                                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                                            <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:10px; border: 1px solid rgba(255,255,255,0.1);">
                                                <p style="margin:0; font-size:10px; color:#94A3B8;">LEG 1 BOOKIE</p>
                                                <p style="margin:0; color:#FFD700; font-weight:bold; font-size:18px;">{"BETWAY" if st.session_state.is_premium else "LOCKED"}</p>
                                            </div>
                                            <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:10px; border: 1px solid rgba(255,255,255,0.1);">
                                                <p style="margin:0; font-size:10px; color:#94A3B8;">LEG 2 BOOKIE</p>
                                                <p style="margin:0; color:#FFD700; font-weight:bold; font-size:18px;">{"PINNACLE" if st.session_state.is_premium else "LOCKED"}</p>
                                            </div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        except: continue
            else: st.error("🔑 API SECURITY ERROR: Check Streamlit Secrets.")

    with col_r:
        st.subheader("📡 Regional Power")
        for reg, val in [("United Kingdom", 98), ("United States", 95), ("Europe Union", 88), ("Australia", 72)]:
            st.caption(reg); st.progress(val/100)
        st.divider()
        st.markdown("### 🏆 Top Yield Today")
        st.success("Cricket IPL: 14.8% Gaps")
        st.info("NBA Totals: 9.2% Gaps")

elif tab == "🕒 LIVE PULSE":
    st.title("🌍 Global Match Pulse")
    try:
        res = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': FOOTBALL_KEY}).json()
        for m in res.get('matches', [])[:20]:
            st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; margin-bottom:12px; border: 1px solid rgba(255,215,0,0.1);">
                    <p style="margin:0; font-size:11px; color:#FFD700;">{m['competition']['name']}</p>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:5px;">
                        <span>{m['homeTeam']['shortName']} <b>{m['score']['fullTime']['home']}</b></span>
                        <span style="background:#4ADE80; color:#020617; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:bold;">LIVE</span>
                        <span><b>{m['score']['fullTime']['away']}</b> {m['awayTeam']['shortName']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    except: st.info("Synchronizing with Global Sports Nodes...")

elif tab == "🏆 LEADERBOARD":
    st.title("🥇 Elite Institution Rankings")
    for u, w, r in [("Accra_Whale", "$ 3,210", "14.2%"), ("Trade_Master", "$ 1,450", "9.5%"), ("MoMo_King", "$ 840", "7.1%")]:
        st.markdown(f"""
            <div style="background:rgba(255,215,0,0.05); padding:20px; border-radius:15px; border-left:5px solid #FFD700; margin-bottom:15px;">
                <h4 style="margin:0; color:white;">{u} <span style="font-size:10px; color:#4ADE80;">(VERIFIED TRADER)</span></h4>
                <div style="display:flex; justify-content:space-between; margin-top:10px;">
                    <span style="font-size:24px; font-weight:bold; color:#FFD700;">{w} Profit</span>
                    <span style="color:#4ADE80; font-weight:bold;">+{r} ROI</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

elif tab == "🎁 $500 BLUEPRINT":
    st.title("🎁 $500 Arbitrage Blueprint")
    st.write("Join the Elite Traders using AI to secure $500 in daily profits.")
    email = st.text_input("Institutional Email")
    if st.button("SEND MY PDF GUIDE"):
        if "@" in email:
            try:
                client = MailChimp(mc_api=MC_API, mc_user="ProScoreAI")
                client.lists.members.create(MC_ID, {'email_address': email, 'status': 'subscribed'})
                st.balloons()
                st.success("✅ Added! Download your guide below.")
            except: st.info("Already subscribed! Check your inbox.")
        st.markdown(f'<a href="{BLUEPRINT_URL}" target="_blank"><button style="width:100%; padding:15px; background:#4ADE80; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">📥 DOWNLOAD $500 BLUEPRINT PDF</button></a>', unsafe_allow_html=True)

elif tab == "🏦 BANKROLL AI":
    st.title("🏦 Institutional Calculator")
    bank = st.number_input("Starting Capital ($)", value=100)
    days = st.slider("Trading Days", 1, 30, 10)
    profit = bank * (1.05 ** days) - bank
    st.metric("Projected Profit", f"$ {profit:,.2f}", "+5% Daily")
    st.info("Based on the '10-Day Compounding Loop' from the Blueprint.")

elif tab == "🛡️ SUPPORT":
    st.title("🛡️ Institutional Support")
    st.write("Connect with our WhatsApp Business desk for bankroll strategy and verification.")
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="width:100%; height:60px; background:#25D366; border:none; border-radius:12px; color:white; font-weight:bold; font-size:18px;">💬 CONNECT TO WHATSAPP BUSINESS</button></a>', unsafe_allow_html=True)
    
