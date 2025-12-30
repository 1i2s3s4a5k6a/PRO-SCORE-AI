import streamlit as st
import requests
import pandas as pd

# --- 1. GLOBAL LINK ---
# Your new Paystack Shop link is now active here
PAYMENT_LINK = "https://paystack.shop/pay/arbitrage-betting-scanner" 

# --- 2. SECURE KEY CHECK ---
try:
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_KEY"]
    vault_ready = True
except Exception:
    vault_ready = False

st.set_page_config(page_title="ProScore Elite | Ghana", layout="wide")

# --- 3. PREMIUM "SUCCESS" LOGIC ---
# This looks for the link you set in Paystack: .../?payment=success
if st.query_params.get("payment") == "success":
    st.session_state.is_premium = True
    st.balloons()
    st.success("🎉 Access Granted! All Markets Unlocked.")

# --- 4. THEME (Dark & Gold) ---
st.markdown("""
    <style>
    .stApp { background-color: #050b14; }
    p, span, label { color: #cfd8dc !important; }
    h1, h2, h3 { color: #ffffff !important; }
    [data-testid="stMetricValue"] { color: #ffca28 !important; }
    .stButton>button { 
        background: linear-gradient(90deg, #ffca28, #ff8f00) !important; 
        color: #050b14 !important; font-weight: 900 !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. MAIN INTERFACE ---
st.title("🏟️ PRO-SCORE GLOBAL TERMINAL")

if not st.session_state.get('is_premium', False):
    st.markdown(f'<a href="{PAYMENT_LINK}" target="_blank" style="text-decoration:none;"><button style="width:100%; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold; background:#ffca28; border:none;">🔥 UPGRADE TO PREMIUM (GHS)</button></a>', unsafe_allow_html=True)

# --- 6. CRASH PROTECTION ---
if not vault_ready:
    st.warning("⚠️ Terminal Offline: Please add your API keys to the Streamlit Cloud Secrets tab to begin scanning.")
    st.stop()

# --- 7. SCANNER ENGINE ---
try:
    s_url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
    sports_data = requests.get(s_url).json()
    
    if isinstance(sports_data, list):
        sport_map = {s['title']: s['key'] for s in sports_data}
        selected = st.selectbox("Select Sports Market", list(sport_map.keys()))
        
        if st.button("🚀 EXECUTE SCAN"):
            st.info(f"Scanning {selected} for arbitrage opportunities...")
            # Results logic here
    else:
        st.error("Invalid API Key or Limit Reached. Check your Odds API dashboard.")
except:
    st.error("Connection Error: Unable to reach the Global Odds Server.")
    
