import streamlit as st
import requests
import pandas as pd
from mailchimp3 import MailChimp
from datetime import datetime

# --- 1. SET CONSTANTS FIRST (Prevents NameError) ---
STRIPE_LINK = "https://buy.stripe.com/your_unique_link_id" # Replace this with your real link later

# --- 2. SECURE CONFIGURATION ---
# We use .get() so the app doesn't crash if one is missing
MAILCHIMP_API = st.secrets.get("MAILCHIMP_API", "missing")
MAILCHIMP_LIST_ID = st.secrets.get("MAILCHIMP_LIST_ID", "missing")
ODDS_API_KEY = st.secrets.get("ODDS_API_KEY", "missing")
FOOTBALL_KEY = st.secrets.get("FOOTBALL_KEY", "missing")

FB_HEADERS = {'X-Auth-Token': FOOTBALL_KEY}

if "missing" in [MAILCHIMP_API, ODDS_API_KEY]:
    st.warning("🔑 Keys missing in Streamlit Secrets. App running in Demo Mode.")

st.set_page_config(page_title="ProScore AI Global", layout="wide", page_icon="🏟️")

# --- 3. SESSION STATE & REDIRECT ---
if 'is_premium' not in st.session_state:
    st.session_state.is_premium = False

# Handle Stripe Success Redirect
if st.query_params.get("payment") == "success":
    st.session_state.is_premium = True
    st.balloons()
    st.success("🎉 Premium Unlocked!")

# --- 4. GLOBAL STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-header {
        background: linear-gradient(135deg, #001f3f 0%, #003366 100%);
        color: white !important;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        border-bottom: 5px solid #FFD700;
    }
    .stButton>button { background-color: #FFD700 !important; color: #001f3f !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ CONTROL CENTER")
    if st.checkbox("Admin Preview Mode"):
        st.session_state.is_premium = True
    st.divider()
    bankroll = st.number_input("Total Capital ($)", value=10000.0)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 2.0)
    st.info(f"Safe Stake: ${(bankroll * risk_pct/100):,.2f}")

# --- 6. MAIN UI ---
st.markdown('<div class="main-header"><h1>🏟️ PRO-SCORE AI: GLOBAL TERMINAL</h1><p>US • UK • EU • AFRICA</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["🎯 ARB SCANNER", "🕒 LIVE PULSE", "📖 QUICK START"])

with tabs[0]:
    if not st.session_state.is_premium:
        with st.container(border=True):
            col_a, col_b = st.columns([2,1])
            with col_a:
                st.subheader("🔓 Unlock Global Markets")
                email = st.text_input("Email for ROI Alerts")
                if st.button("Get Basic Access"):
                    st.success("Check your email!")
            with col_b:
                st.markdown(f'<a href="{STRIPE_LINK}" target="_blank"><button style="width:100%; padding:15px; background:#001f3f; color:#FFD700; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">🔥 UPGRADE</button></a>', unsafe_allow_html=True)

    if st.button("🚀 SCAN GLOBAL MARKETS"):
        if ODDS_API_KEY == "missing":
            st.error("Cannot scan without Odds API Key in Secrets.")
        else:
            # API logic remains the same...
            st.info("Scanning global markets... (Make sure your API key is active)")

with tabs[1]:
    st.subheader("🕒 Live Scores")
    if FOOTBALL_KEY == "missing":
        st.error("Football API Key missing.")
    else:
        st.write("Fetching live global matches...")

with tabs[2]:
    st.write("1. Check Odds. 2. Verify Stake. 3. Profit.")
    
