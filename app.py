import streamlit as st
import requests
from mailchimp3 import MailChimp

# --- 1. GLOBAL SETTINGS ---
# Replace with your real Stripe link
STRIPE_LINK = "https://buy.stripe.com/your_actual_link_here" 

# --- 2. SECURE GATEWAY (Pulls from Streamlit Cloud Secrets) ---
try:
    MAILCHIMP_API = st.secrets["MAILCHIMP_API"]
    MAILCHIMP_LIST_ID = st.secrets["MAILCHIMP_LIST_ID"]
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_KEY"]
    config_error = False
except Exception:
    config_error = True

# --- 3. PAGE SETUP & THEME ---
st.set_page_config(page_title="ProScore AI Global", layout="wide", page_icon="🏟️")

if 'is_premium' not in st.session_state:
    st.session_state.is_premium = False

# Handle Stripe Redirect
if st.query_params.get("payment") == "success":
    st.session_state.is_premium = True
    st.balloons()

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-header {
        background: linear-gradient(135deg, #001f3f 0%, #003366 100%);
        color: white !important; padding: 40px; border-radius: 20px;
        text-align: center; border-bottom: 6px solid #FFD700; margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #FFD700 !important; color: #001f3f !important;
        font-weight: 800; border-radius: 8px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI: GLOBAL TERMINAL</h1><p>US • UK • EU • AFRICA</p></div>', unsafe_allow_html=True)

# --- 5. CRASH PROTECTION ---
if config_error:
    st.error("🔑 Setup Incomplete: Please add your API keys to the Streamlit Cloud Dashboard Secrets.")
    st.stop() # Stops the red-box error from appearing

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ CONTROL CENTER")
    if st.checkbox("Admin Preview Mode"):
        st.session_state.is_premium = True
    st.divider()
    bankroll = st.number_input("Total Capital ($)", value=10000.0)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 2.0)
    st.info(f"Safe Stake: **${(bankroll * risk_pct/100):,.2f}**")

# --- 7. TABS ---
tabs = st.tabs(["🎯 ARB SCANNER", "🕒 LIVE PULSE", "📖 QUICK START"])

with tabs[0]:
    if not st.session_state.is_premium:
        with st.container(border=True):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.subheader("🔓 Unlock Global Markets")
                email = st.text_input("Email for Alerts")
                if st.button("Join Pro-List"):
                    try:
                        client = MailChimp(mc_api=MAILCHIMP_API, mc_user='admin')
                        client.lists.members.create(MAILCHIMP_LIST_ID, {'email_address': email, 'status': 'subscribed'})
                        st.success("Subscribed!")
                    except: st.warning("Subscription failed. Please check Mailchimp settings.")
            with col_b:
                st.markdown(f'<a href="{STRIPE_LINK}" target="_blank"><button style="width:100%; padding:20px; background:#001f3f; color:#FFD700; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">🔥 UPGRADE NOW</button></a>', unsafe_allow_html=True)

    st.divider()
    if st.button("🚀 INITIATE GLOBAL SCAN"):
        url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu,us,au&markets=h2h"
        data = requests.get(url).json()
        for event in data[:5]:
            with st.container(border=True):
                st.write(f"**Match:** {event['home_team']} vs {event['away_team']}")
                if st.session_state.is_premium:
                    st.write("🟢 Arbitrage Window Detected (Premium View)")
                else:
                    st.info("🔒 Premium required to see specific Bookmakers.")
                
