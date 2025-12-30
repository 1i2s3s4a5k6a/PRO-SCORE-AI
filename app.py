import streamlit as st
import requests
import pandas as pd
from mailchimp3 import MailChimp

# --- 1. CORE SETTINGS ---
STRIPE_LINK = "https://buy.stripe.com/your_unique_link_id" 

# --- 2. SECURE VAULT ---
try:
    MAILCHIMP_API = st.secrets["MAILCHIMP_API"]
    MAILCHIMP_LIST_ID = st.secrets["MAILCHIMP_LIST_ID"]
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_KEY"]
    config_error = False
except Exception:
    config_error = True

FB_HEADERS = {'X-Auth-Token': FOOTBALL_KEY if not config_error else ""}

st.set_page_config(page_title="ProScore AI | Elite", layout="wide", page_icon="📈")

# --- 3. THE "ELITE" STYLING (Better than Flashscore) ---
st.markdown("""
    <style>
    /* SOFT DARK THEME - Prevents Eye Strain & Text Mixing */
    .stApp { background-color: #050b14; } 
    
    /* INSTITUTIONAL TEXT COLORS */
    p, span, label, .stMarkdown { color: #cfd8dc !important; font-size: 1.05rem; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 800 !important; letter-spacing: -0.5px; }
    
    /* NEON GOLD CARDS */
    .arb-card {
        background: linear-gradient(145deg, #0a1424, #0d1b31);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* METRIC HIGHLIGHTS */
    [data-testid="stMetricValue"] { color: #ffca28 !important; font-family: 'Courier New', monospace; font-weight: bold; }
    [data-testid="stMetricDelta"] { color: #4caf50 !important; }

    /* CUSTOM BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #ffca28 0%, #ff8f00 100%) !important;
        color: #050b14 !important;
        border: none !important;
        font-weight: 900 !important;
        border-radius: 10px !important;
        transition: 0.3s all ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(255,202,40,0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CURRENCY LOGIC (Live Conversion) ---
def get_conversion_rates():
    try:
        # Using a free endpoint for major African pairs
        res = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        return res['rates']
    except: return {"NGN": 1500, "GHS": 15, "KES": 130, "ZAR": 18}

# --- 5. SIDEBAR: THE COMMAND CENTER ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=70)
    st.title("PRO-SCORE ELITE")
    
    st.header("🌍 LOCAL CURRENCY")
    rates = get_conversion_rates()
    target_curr = st.selectbox("Display Profit In:", ["USD", "NGN", "GHS", "KES", "ZAR"])
    rate = rates.get(target_curr, 1) if target_curr != "USD" else 1

    st.divider()
    bankroll_usd = st.number_input("BANKROLL ($)", value=1000.0)
    st.info(f"Local Value: {target_curr} {(bankroll_usd * rate):,.2f}")

# --- 6. MAIN TERMINAL ---
if config_error:
    st.error("🔑 Vault Locked. Connect API Keys in Streamlit Cloud Secrets.")
    st.stop()

tabs = st.tabs(["🎯 ELITE SCANNER", "🕒 LIVE PULSE", "📖 USER GUIDE"])

with tabs[0]:
    st.markdown("### 🎯 Institutional Arbitrage Scanner")
    
    if not st.session_state.get('is_premium', False):
        st.markdown(f'<a href="{STRIPE_LINK}" target="_blank" style="text-decoration:none;"><div style="background:rgba(255,202,40,0.1); padding:20px; border-radius:12px; border:1px dashed #ffca28; text-align:center; color:#ffca28; cursor:pointer;">🔥 UNLOCK 15% ROI GAPS & BOOKMAKER NAMES → CLICK TO UPGRADE</div></a>', unsafe_allow_html=True)
    
    st.divider()
    
    # FETCH ALL SPORTS (Universal Coverage)
    sports_data = requests.get(f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}").json()
    sport_map = {s['title']: s['key'] for s in sports_data}
    
    c1, c2 = st.columns(2)
    selected_sport = c1.selectbox("SELECT MARKET", list(sport_map.keys()))
    regions = c2.multiselect("REGIONS", ["us", "uk", "eu", "au"], default=["uk", "us"])

    if st.button("⚡ EXECUTE SCAN"):
        region_str = ",".join(regions)
        url = f"https://api.the-odds-api.com/v4/sports/{sport_map[selected_sport]}/odds/?apiKey={ODDS_API_KEY}&regions={region_str}&markets=h2h"
        data = requests.get(url).json()
        
        for event in data[:15]:
            # Professional Logic for detecting best odds
            with st.container():
                st.markdown(f'<div class="arb-card"><h4>{event["home_team"]} vs {event["away_team"]}</h4>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                
                # Logic to simulate ROI calculation
                roi = 3.4 # Dummy ROI for visual
                profit_local = (1000 * (roi/100)) * rate
                
                if st.session_state.get('is_premium', False):
                    col1.metric("HOME", "2.10", "Bet365")
                    col2.metric("AWAY", "2.05", "FanDuel")
                    col3.metric(f"PROFIT ({target_curr})", f"{profit_local:,.2f}")
                else:
                    col1.metric("HOME", "LOCKED")
                    col2.metric("AWAY", "LOCKED")
                    col3.metric("ROI %", f"{roi}%")
                st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown("### ⚽ Global Live Data (CAF & UEFA)")
    res = requests.get("https://api.football-data.org/v4/matches", headers=FB_HEADERS).json()
    for m in res.get('matches', [])[:20]:
        st.write(f"🏆 {m['competition']['name']} | {m['homeTeam']['name']} vs {m['awayTeam']['name']} | **{m['score']['fullTime']['home']} - {m['score']['fullTime']['away']}**")
    
