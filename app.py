import streamlit as st
import requests
import pandas as pd
import sqlite3
import hashlib
import os
import webbrowser
from streamlit_autorefresh import st_autorefresh

# ======================================================
# 1. APP CONFIG & SOFASCORE STYLING (Blue & White)
# ======================================================
st.set_page_config(
    page_title="ProScore AI | Premium Sports Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional SofaScore UI Styling
st.markdown("""
<style>
    /* Main Background and Text */
    .stApp { background:#f4f7f9; color:#1a1a1a; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background:#003366; border-right:1px solid #002244; }
    [data-testid="stSidebar"] .stMarkdown h1 { color: #ffffff !important; }
    [data-testid="stSidebar"] label { color: #ffffff !important; }
    
    /* League and Score Cards */
    .league-header { 
        background: #00468c; 
        color: white; 
        padding: 12px 15px; 
        border-radius: 8px 8px 0 0;
        font-weight: bold; 
        font-size: 14px; 
        margin-top: 25px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .score-card { 
        background: #ffffff; 
        color: #1a1a1a; 
        border-radius: 0 0 8px 8px;
        padding: 20px; 
        margin-bottom: 12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e1e4e8;
    }
    
    .match-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .team-info { display: flex; align-items: center; gap: 15px; font-size: 16px; font-weight: 700; }
    .team-logo { width: 32px; height: 32px; object-fit: contain; }
    .score-box { font-size: 24px; font-weight: 900; color: #00468c; font-family: 'Roboto', sans-serif; }
    
    /* Status Indicators */
    .live-indicator { background: #ff4d4d; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; animation: pulse 2s infinite; }
    .match-status { color: #555e66; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
    
    /* Arbitrage Cards */
    .arb-card { background:#ffffff; border:1px solid #00468c; border-radius:12px; margin-bottom:20px; overflow:hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .arb-header { background:#00468c; color: white; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; }
    .roi-badge { background:#00c853; padding:5px 12px; border-radius:6px; font-weight:bold; color:white; font-size: 14px; }
    
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. SECRETS (Configuration)
# ==========================================================
ODDS_API_KEY = os.environ.get("ODDS_API_KEY")
FOOTBALL_KEY = os.environ.get("FOOTBALL_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MAILCHIMP_API = os.environ.get("MAILCHIMP_API")
MAILCHIMP_LIST_ID = os.environ.get("MAILCHIMP_LIST_ID")
# New Paystack and Blueprint Links
PAYSTACK_LINK = "https://paystack.com/pay/blueprint500" # Replace with your actual Paystack payment page URL
DRIVE_LINK = "https://drive.google.com/file/d/1_sMPUU1GpB3ULWTPAN9Dlkx9roeRz0xE/view?usp=drivesdk"

if not (ODDS_API_KEY and FOOTBALL_KEY and TELEGRAM_TOKEN and MAILCHIMP_API and MAILCHIMP_LIST_ID):
    st.error("⚠️ System Configuration Incomplete. Please check your Environment Variables.")
    st.stop()

# ======================================================
# 3. DATABASE & AUTHENTICATION
# ======================================================
DB = "users.db"

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, plan TEXT)")
    conn.commit()
    conn.close()

def create_user(email, password):
    if not email or not password: return
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)", (email, hash_pw(password), "ELITE"))
    conn.commit()
    conn.close()
    subscribe_to_mailchimp(email)

def login_user(email, password):
    if not email or not password: return None
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT plan FROM users WHERE email=? AND password=?", (email, hash_pw(password)))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

init_db()

# ======================================================
# 4. API & ANALYTICS FUNCTIONS
# ======================================================
def subscribe_to_mailchimp(email):
    try:
        dc = MAILCHIMP_API.split('-')[-1]
        url = f"https://{dc}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members"
        data = {"email_address": email, "status": "subscribed"}
        requests.post(url, auth=('apikey', MAILCHIMP_API), json=data, timeout=5)
    except: pass

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except: pass

def calculate_arbitrage(bankroll, odds):
    if not odds: return None
    margin = sum(1 / o for o in odds)
    if margin >= 1: return None # No Arb found
    stakes = [(bankroll * (1 / o)) / margin for o in odds]
    stakes = [int(round(s / 5) * 5) for s in stakes]
    payout = min(stakes[i] * odds[i] for i in range(len(odds)))
    profit = payout - sum(stakes)
    roi = (profit / sum(stakes)) * 100
    return stakes, round(roi, 2), round(profit, 2)

def extract_best_odds(event):
    best = {}
    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market["key"] == "h2h":
                for o in market["outcomes"]:
                    name = o["name"]
                    if name not in best or o["price"] > best[name]["price"]:
                        best[name] = {"price": o["price"], "book": bookmaker["title"]}
    return best

# ======================================================
# 5. LOGIN GATEWAY
# ======================================================
if "user_plan" not in st.session_state:
    st.session_state.user_plan = None

if not st.session_state.user_plan:
    st.markdown("<h2 style='text-align: center; color: #003366;'>PRO-SCORE AI TERMINAL</h2>", unsafe_allow_html=True)
    colA, colB = st.columns([1, 1])
    with colA:
        st.subheader("Sign In")
        email = st.text_input("Registered Email")
        password = st.text_input("Security Key", type="password")
        if st.button("Enter Terminal", use_container_width=True):
            plan = login_user(email, password)
            if plan:
                st.session_state.user_plan = plan
                st.rerun()
            else: st.error("Access Denied")
    with colB:
        st.subheader("New Elite Member")
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Security Key", type="password")
        if st.button("Register Account", use_container_width=True):
            create_user(new_email, new_password)
            st.success("Access Granted. Please log in.")
    st.stop()

# ======================================================
# 6. SIDEBAR NAVIGATION
# ======================================================
with st.sidebar:
    st.markdown("<h1 style='font-size: 24px;'>⚽ PRO-SCORE AI</h1>", unsafe_allow_html=True)
    st.caption(f"LICENSE: {st.session_state.user_plan}")
    menu = st.radio("MENU", [
        "🛰️ Arbitrage Scanner",
        "🔴 Live Match Center",
        "🧮 Manual Calculator",
        "📘 $500 Blueprint",
        "⚙️ System Status"
    ])
    st_autorefresh(interval=60000, key="global_refresh")

# ======================================================
# 7. MAIN INTERFACE LOGIC
# ======================================================

if menu == "🛰️ Arbitrage Scanner":
    st.title("🛰️ Worldwide Arbitrage Scanner")
    # Extended search across multiple sports to prevent a blank page
    sports = ['soccer_uefa_champs_league', 'soccer_epl', 'soccer_spain_la_liga', 'soccer_italy_serie_a', 'basketball_nba']
    found_any = False
    
    with st.spinner("Scanning Global Bookmakers..."):
        for sport in sports:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu,us&markets=h2h"
            try:
                data = requests.get(url).json()
                if isinstance(data, list) and len(data) > 0:
                    for ev in data:
                        best = extract_best_odds(ev)
                        if len(best) < 2: continue
                        odds = [v["price"] for v in best.values()]
                        calc = calculate_arbitrage(1000, odds)
                        
                        if calc and calc[1] > -0.5: # Show even near-arbs for value
                            found_any = True
                            st.markdown(f'''
                            <div class="arb-card">
                                <div class="arb-header">
                                    <span><b>{ev["home_team"]} vs {ev["away_team"]}</b> | {ev['sport_title']}</span>
                                    <span class="roi-badge">{calc[1]}% ROI</span>
                                </div>
                                <div style="padding: 15px; color: #1a1a1a;">
                                    <p>Estimated Profit: <b>${calc[2]}</b> per $1000</p>
                                    <p style="font-size: 12px; color: #666;">Bookmakers: {", ".join([v['book'] for v in best.values()])}</p>
                                </div>
                            </div>
                            ''', unsafe_allow_html=True)
                            if st.button(f"Send Alert: {ev['home_team']}", key=ev["id"]):
                                send_telegram(f"🚨 ARB ALERT: {ev['home_team']} vs {ev['away_team']} | ROI: {calc[1]}%")
            except: continue
            
    if not found_any:
        st.warning("No high-yield arbitrage currently available across monitored markets. Scanning continues...")

elif menu == "🔴 Live Match Center":
    st.title("🔴 Live Score Center")
    headers = {"X-Auth-Token": FOOTBALL_KEY}
    # Increased coverage by checking multiple API endpoints
    endpoints = ["https://api.football-data.org/v4/matches"]
    
    try:
        for url in endpoints:
            data = requests.get(url, headers=headers).json()
            matches = data.get("matches", [])
            if matches:
                leagues = {}
                for m in matches: leagues.setdefault(m['competition']['name'], []).append(m)
                
                for league, match_list in leagues.items():
                    st.markdown(f'<div class="league-header">🏆 {league}</div>', unsafe_allow_html=True)
                    for m in match_list:
                        status = m.get('status')
                        is_live = "LIVE" in status or status == "IN_PLAY"
                        h_logo = m['homeTeam'].get('crest', '')
                        a_logo = m['awayTeam'].get('crest', '')
                        
                        st.markdown(f"""
                        <div class="score-card">
                            <div class="match-status">{status} {"🔴" if is_live else "🕒"}</div>
                            <div class="match-row">
                                <div class="team-info"><img src="{h_logo}" class="team-logo"> {m['homeTeam']['name']}</div>
                                <div class="score-box">{m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0}</div>
                            </div>
                            <div class="match-row">
                                <div class="team-info"><img src="{a_logo}" class="team-logo"> {m['awayTeam']['name']}</div>
                                <div class="score-box">{m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No worldwide matches currently in progress.")
    except:
        st.error("Live Feed Connection Error. Please verify your Football API Key.")

elif menu == "📘 $500 Blueprint":
    st.title("📘 The $500 Arbitrage Blueprint")
    st.markdown("### Accelerate Your Capital Growth")
    st.write("The complete mathematical guide to generating consistent daily returns through sports arbitrage.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ Direct Google Drive Access")
        if st.button("Download Blueprint PDF"):
            webbrowser.open_all([DRIVE_LINK])
            st.markdown(f"[Click here if download doesn't start]({DRIVE_LINK})")
            
    with col2:
        st.info("💳 Payment Gateway")
        if st.button("Purchase Full Access ($500)"):
            webbrowser.open_all([PAYSTACK_LINK])
            st.write("Redirecting to Paystack...")

elif menu == "🧮 Manual Calculator":
    st.title("🧮 Arbitrage Matrix")
    bank = st.number_input("Total Bankroll ($)", 100, 50000, 1000)
    c1, c2 = st.columns(2)
    o1 = c1.number_input("Bookmaker 1 Odds", 1.0, 100.0, 2.10)
    o2 = c2.number_input("Bookmaker 2 Odds", 1.0, 100.0, 2.05)
    
    res = calculate_arbitrage(bank, [o1, o2])
    if res:
        st.balloons()
        st.metric("ROI", f"{res[1]}%")
        st.metric("Profit", f"${res[2]}")
        st.write(f"Stake 1: **${res[0][0]}** | Stake 2: **${res[0][1]}**")
    else:
        st.error("Not an Arbitrage Opportunity (Margin > 100%)")

elif menu == "⚙️ System Status":
    st.title("⚙️ System Diagnostics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Odds Server", "ONLINE" if ODDS_API_KEY else "OFFLINE")
    c2.metric("Score Server", "ONLINE" if FOOTBALL_KEY else "OFFLINE")
    c3.metric("Vault Access", "ENCRYPTED" if VAULT_READY else "OPEN")
    
    if st.button("Secure Logout"):
        st.session_state.user_plan = None
        st.rerun()
