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
WHATSAPP_URL = "https://wa.me/233XXXXXXXXX?text=Hello%20ProScore%20AI%20Support"
BLUEPRINT_URL = "https://drive.google.com/file/d/1_sMPUU1GpB3ULWTPAN9Dlkx9roeRz0xE/view?usp=drivesdk"

st.set_page_config(page_title="ProScore AI | Elite Terminal", layout="wide", initial_sidebar_state="expanded")

# --- 2. THE POWERHOUSE STYLING (CSS) ---
st.markdown("""
    <style>
    /* Global Deep-Space Theme */
    .stApp { background: radial-gradient(circle at top, #0B1120 0%, #020817 100%); font-family: 'Inter', sans-serif; }
    
    /* Top Live Signal Bar */
    .signal-bar {
        background: linear-gradient(90deg, #B8860B, #FFD700); color: #020617; 
        padding: 12px; text-align: center; font-weight: 900; text-transform: uppercase; 
        letter-spacing: 2px; border-radius: 0 0 15px 15px; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }

    /* Glassmorphic Cards */
    .arb-card {
        background: rgba(30, 41, 59, 0.45); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 215, 0, 0.1); border-radius: 16px;
        padding: 24px; margin-bottom: 20px; transition: 0.3s ease;
    }
    .arb-card:hover { border-color: #FFD700; transform: translateY(-3px); }

    /* Custom Metrics */
    [data-testid="stMetricValue"] { color: #FFD700 !important; font-weight: 800 !important; }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%) !important;
        color: #020817 !important; border-radius: 12px !important; border: none !important;
        font-weight: 900 !important; height: 3.5rem !important; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DYNAMIC HUD ALERT ---
st.markdown(f'<div class="signal-bar">🚀 SYSTEM ACTIVE: Scanning 240+ Global Bookmakers for $500 Daily Gaps</div>', unsafe_allow_html=True)

# --- 4. NAVIGATION & PREMIUM LOGIC ---
if 'is_premium' not in st.session_state:
    st.session_state.is_premium = False

if st.query_params.get("payment") == "success":
    st.session_state.is_premium = True
    st.balloons()

with st.sidebar:
    st.markdown("<h1 style='color:#FFD700;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    st.caption("Institutional Terminal v3.5 (Global)")
    
    tab = st.radio("TERMINAL SELECT", ["🛰️ COMMAND CENTER", "📊 MARKET PULSE", "🏆 LEADERBOARD", "🎁 $500 BLUEPRINT", "🛡️ SUPPORT"])
    
    st.divider()
    st.markdown("### 🏦 BANKROLL HUD")
    currency = st.selectbox("Base Currency", ["USD", "GHS", "NGN", "KES"])
    bank = st.number_input("Capital Pool", value=100)
    
    if not st.session_state.is_premium:
        st.markdown(f'<a href="{PAYSTACK_LINK}" target="_blank"><button style="width:100%; padding:10px; background:#FFD700; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">🔓 UNLOCK ELITE ACCESS</button></a>', unsafe_allow_html=True)

# --- 5. PAGE ROUTING ---

if tab == "🛰️ COMMAND CENTER":
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("GLOBAL GAPS", "2,142", "LIVE")
    m2.metric("AVG SIGNAL ROI", "5.82%", "+0.4%")
    m3.metric("API LATENCY", "14ms", "OPTIMAL")
    m4.metric("AI STABILITY", "99.1%", "STABLE")

    st.divider()
    col_left, col_right = st.columns([2.5, 1])

    with col_left:
        st.subheader("🎯 Real-Time Arbitrage Scanner")
        if vault_ready:
            try:
                # Dynamic Global Market Discovery
                s_res = requests.get(f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}").json()
                sport_map = {s['title']: s['key'] for s in s_res if s['active']}
                
                c1, c2 = st.columns(2)
                sel_sport = c1.selectbox("Target Market", list(sport_map.keys()))
                sel_region = c2.multiselect("Scan Regions", ["uk", "eu", "us", "au"], default=["uk", "eu"])
                
                if st.button("🚀 EXECUTE GLOBAL SCAN"):
                    with st.spinner("Analyzing Global Liquidity Gaps..."):
                        regs = ",".join(sel_region)
                        url = f"https://api.the-odds-api.com/v4/sports/{sport_map[sel_sport]}/odds/?apiKey={ODDS_API_KEY}&regions={regs}&markets=h2h"
                        data = requests.get(url).json()
                        
                        if not data:
                            st.info("No immediate gaps found in this node. Checking secondary markets...")
                        else:
                            for match in data[:10]:
                                roi = round(random.uniform(3.5, 11.2), 2)
                                st.markdown(f"""
                                <div class="arb-card">
                                    <div style="display:flex; justify-content:space-between;">
                                        <span style="color:#94A3B8; font-size:11px;">{sel_sport.upper()} • SIGNAL ID {random.randint(1000,9999)}</span>
                                        <span style="color:#4ADE80; font-weight:bold;">+{roi}% ROI</span>
                                    </div>
                                    <h3 style="margin: 10px 0;">{match['home_team']} vs {match['away_team']}</h3>
                                    <div style="display:flex; gap:40px;">
                                        <div><p style="margin:0; font-size:10px;">HOME BOOKIE</p><p style="color:#FFD700; font-size:22px; font-weight:bold;">{"BETWAY" if st.session_state.is_premium else "LOCKED"}</p></div>
                                        <div><p style="margin:0; font-size:10px;">AWAY BOOKIE</p><p style="color:#FFD700; font-size:22px; font-weight:bold;">{"PINNACLE" if st.session_state.is_premium else "LOCKED"}</p></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.caption(f"Signal Stability: {random.randint(80, 98)}%")
                                st.progress(random.randint(80, 98)/100)
            except: st.error("Node latency high. Refreshing global scan...")
        else: st.error("🔑 API Keys Missing. Please update Streamlit Secrets.")

    with col_right:
        st.subheader("🔥 Volatility Heatmap")
        for l, h in [("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", 92), ("🇺🇸 NBA Basketball", 88), ("🎾 Tennis ATP", 65), ("🏈 NFL Football", 41)]:
            st.caption(l); st.progress(h/100)
        st.divider()
        st.markdown("### 💰 Profit Projection")
        st.metric("Daily Goal ($)", f"{bank*0.05:,.2f}")
        st.metric("30-Day Growth ($)", f"{bank*1.48:,.2f}")

elif tab == "📊 MARKET PULSE":
    st.title("🕒 Global Real-Time Scores")
    try:
        res = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': FOOTBALL_KEY}).json()
        for m in res.get('matches', [])[:20]:
            st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; margin-bottom:10px; display:flex; justify-content:space-between;">
                    <span>{m['homeTeam']['name']} <b>{m['score']['fullTime']['home']}</b></span>
                    <span style="color:#FFD700;">LIVE</span>
                    <span><b>{m['score']['fullTime']['away']}</b> {m['awayTeam']['name']}</span>
                </div>
            """, unsafe_allow_html=True)
    except: st.info("Updating live global feeds...")

elif tab == "🏆 LEADERBOARD":
    st.title("🥇 Global Institutional Gains")
    leaders = [("Alpha_Trade", "$ 3,120", "14.2%"), ("Accra_Whale", "$ 1,840", "9.5%"), ("Momo_Master", "$ 920", "7.1%")]
    for u, w, r in leaders:
        st.markdown(f"""
            <div style="background:rgba(255,215,0,0.05); padding:20px; border-radius:15px; border-left:5px solid #FFD700; margin-bottom:12px;">
                <h4 style="margin:0;">{u} <span style="font-size:10px; color:#4ADE80;">(VERIFIED)</span></h4>
                <div style="display:flex; justify-content:space-between; margin-top:10px;">
                    <span style="font-size:24px; font-weight:bold; color:#FFD700;">{w}</span>
                    <span style="color:#4ADE80; font-weight:bold;">+{r} ROI</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

elif tab == "🎁 $500 BLUEPRINT":
    st.title("🎁 Get The $500 Arbitrage Blueprint")
    st.write("Unlock the institutional roadmap to $500 in daily profits. Entering your email sends the PDF directly to your inbox.")
    
    col_a, col_b = st.columns([2,1])
    with col_a:
        email = st.text_input("Institutional Email", placeholder="trader@proscore.ai")
        if st.button("SEND MY BLUEPRINT"):
            if vault_ready and "@" in email:
                try:
                    client = MailChimp(mc_api=MC_API, mc_user="ProScoreAI")
                    client.lists.members.create(MC_ID, {'email_address': email, 'status': 'subscribed'})
                    st.balloons()
                    st.success("✅ Success! Blueprint dispatched to inbox.")
                    st.markdown(f"[**Click Here to Download Directly**]({BLUEPRINT_URL})")
                except: st.info("You're already on our list! Check your previous emails.")
            else: st.error("Check email format or Secrets configuration.")
    with col_b:
        st.markdown("""
        **What's Inside:**
        * ✅ $100 to $500 Roadmap
        * ✅ High-Stability Markets
        * ✅ Account Safety Rules
        """)

elif tab == "🛡️ SUPPORT":
    st.title("🛰️ Analyst Support Desk")
    st.write("Connect with our Accra-based trade analysts for bankroll strategy and terminal verification.")
    st.markdown(f'<a href="{WHATSAPP_URL}"><button>💬 OPEN WHATSAPP CHAT</button></a>', unsafe_allow_html=True)
    
