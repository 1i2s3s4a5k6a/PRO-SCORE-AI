import streamlit as st
import requests
import pandas as pd
from mailchimp3 import MailChimp
from datetime import datetime

# --- 1. SECURE CONFIGURATION ---
try:
    MAILCHIMP_API = st.secrets["MAILCHIMP_API"]
    MAILCHIMP_LIST_ID = st.secrets["MAILCHIMP_LIST_ID"]
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_KEY"]
    # Replace the link below with your actual Stripe Payment Link
    STRIPE_LINK = "https://buy.stripe.com/your_unique_link_id" 
except Exception as e:
    st.error("🔑 Setup Incomplete: Please add API keys to Streamlit Secrets.")

st.set_page_config(page_title="ProScore AI Global", layout="wide", page_icon="🏟️")

# --- 2. SESSION STATE & STRIPE REDIRECT ---
if 'is_premium' not in st.session_state:
    st.session_state.is_premium = False

# HANDLE STRIPE REDIRECT (Unlocks Premium after payment)
query_params = st.query_params
if query_params.get("payment") == "success":
    st.session_state.is_premium = True
    st.balloons() 
    st.success("🎉 Welcome to ProScore Premium! All Global Markets Unlocked.")

# --- 3. GLOBAL STYLING (FOR VISIBILITY & CONVERSION) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-header {
        background: linear-gradient(135deg, #001f3f 0%, #003366 100%);
        color: white !important;
        padding: 45px;
        border-radius: 20px;
        text-align: center;
        border-bottom: 6px solid #FFD700;
        margin-bottom: 30px;
    }
    .main-header h1, .main-header p { color: white !important; }
    .arb-card {
        background-color: #fcfcfc !important;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        border-left: 10px solid #FFD700;
        margin-bottom: 25px;
    }
    [data-testid="stMetricValue"] { color: #001f3f !important; font-weight: bold; }
    .stButton>button {
        background-color: #FFD700 !important;
        color: #001f3f !important;
        font-weight: 800;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LEAD GEN LOGIC ---
def sync_lead(email):
    try:
        client = MailChimp(mc_api=MAILCHIMP_API, mc_user='admin')
        client.lists.members.create(MAILCHIMP_LIST_ID, {'email_address': email, 'status': 'subscribed'})
        return True
    except: return False

# --- 5. SIDEBAR: CONTROL CENTER ---
with st.sidebar:
    st.title("🛡️ CONTROL CENTER")
    if st.checkbox("Admin Preview Mode"):
        st.session_state.is_premium = True
        st.success("Premium View Active")
    
    st.divider()
    st.header("💰 RISK MANAGEMENT")
    bankroll = st.number_input("Total Capital ($)", value=10000.0)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 2.0)
    st.info(f"Safe Stake: **${(bankroll * (risk_pct/100)):,.2f}**")
    
    st.divider()
    st.caption("⚖️ Pro-Score AI is an analytics tool. We do not facilitate gambling. Verify all odds before execution.")

# --- 6. MAIN INTERFACE ---
st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI: GLOBAL TERMINAL</h1><p>Institutional Arbitrage Intelligence • US • UK • EU • AFRICA</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["🎯 ARB SCANNER", "🕒 LIVE PULSE", "📊 PERFORMANCE", "📖 QUICK START"])

# --- TAB 1: ARB SCANNER ---
with tabs[0]:
    if not st.session_state.is_premium:
        with st.container(border=True):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.subheader("🔓 Unlock Global Markets")
                st.write("Access FanDuel, Bet365, 1xBet, and 60+ global bookmakers.")
                email = st.text_input("Enter Email for Premium ROI Alerts")
                if st.button("Get Basic Access"):
                    if email:
                        sync_lead(email)
                        st.success("Subscribed! Check your inbox for the Quick Start Guide.")
            with col_b:
                st.markdown(f'<a href="{STRIPE_LINK}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding:20px; background:#001f3f; color:#FFD700; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">🔥 UPGRADE TO PREMIUM</button></a>', unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns(2)
    region = c1.multiselect("Select Market Regions", ["us", "uk", "eu", "au"], default=["us", "uk"])
    market = c2.selectbox("Sporting Market", ["soccer_epl", "soccer_uefa_champs_league", "basketball_nba", "americanfootball_nfl"])
    
    if st.button("🚀 INITIATE GLOBAL SCAN"):
        with st.spinner("Analyzing cross-continental discrepancies..."):
            region_str = ",".join(region)
            url = f"https://api.the-odds-api.com/v4/sports/{market}/odds/?apiKey={ODDS_API_KEY}&regions={region_str}&markets=h2h"
            data = requests.get(url).json()
            
            found = 0
            for event in data:
                best_h, bk_h = 0, ""; best_a, bk_a = 0, ""
                for b in event['bookmakers']:
                    for m in b['markets']:
                        for o in m['outcomes']:
                            if o['name'] == event['home_team'] and o['price'] > best_h:
                                best_h, bk_h = o['price'], b['title']
                            elif o['name'] == event['away_team'] and o['price'] > best_a:
                                best_a, bk_a = o['price'], b['title']
                
                if best_h > 0 and best_a > 0:
                    inv_p = (1/best_h) + (1/best_a)
                    if inv_p < 1.0:
                        found += 1
                        roi = (1/inv_p - 1) * 100
                        with st.container(border=True):
                            st.markdown(f"### ✅ {roi:.2f}% ROI GAP: {event['home_team']} vs {event['away_team']}")
                            m1, m2, m3 = st.columns(3)
                            if st.session_state.is_premium:
                                m1.metric(f"🏠 {bk_h}", f"{best_h}")
                                m2.metric(f"✈️ {bk_a}", f"{best_a}")
                                m3.metric("Profit on $1k", f"${(1000/inv_p - 1000):.2f}")
                            else:
                                m1.metric("🏠 [LOCKED]", "X.XX")
                                m2.metric("✈️ [LOCKED]", "X.XX")
                                st.info("🔒 Premium required for Bookmaker names.")
            if found == 0: st.info("Scanning complete. No windows found currently.")

# --- TAB 2: LIVE PULSE ---
with tabs[1]:
    st.subheader("🕒 Head-to-Head Live Intelligence")
    res = requests.get("https://api.football-data.org/v4/matches", headers=FB_HEADERS).json()
    for m in res.get('matches', [])[:12]:
        with st.expander(f"⚽ {m['homeTeam']['name']} vs {m['awayTeam']['name']}"):
            score_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else "-"
            score_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else "-"
            st.markdown(f"**Score:** {score_h} - {score_a} | **League:** {m['competition']['name']}")

# --- TAB 4: QUICK START ---
with tabs[3]:
    st.subheader("📖 User Guide")
    st.markdown("""
    1. **Double Check:** Always verify odds on the betting site before clicking 'Confirm'.
    2. **Avoid Rounding:** Bet $197 instead of $200 to look like a recreational player.
    3. **Speed:** Arbitrage windows usually last 2-5 minutes.
    """)
    
