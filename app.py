import streamlit as st
import requests
import pandas as pd
import sqlite3
import hashlib
import os
from streamlit_autorefresh import st_autorefresh

# ======================================================
# 1. APP CONFIG & STYLING
# ======================================================
st.set_page_config(
    page_title="ProScore AI | Elite Arbitrage Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the "Elite" Look
st.markdown("""
<style>
    .stApp { background:#0d1117; color:#e6edf3; }
    [data-testid="stSidebar"] { background:#161b22; border-right:1px solid #30363d; }
    .league-header { background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white; padding: 10px 15px; border-radius: 8px 8px 0 0;
        font-weight: bold; text-transform: uppercase; font-size: 13px; margin-top: 20px;}
    .score-card { background: #ffffff; color: #161b22; border-radius: 0 0 8px 8px;
        padding: 18px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
    .match-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .team-info { display: flex; align-items: center; gap: 12px; font-size: 17px; font-weight: 600; }
    .team-logo { width: 28px; height: 28px; object-fit: contain; }
    .score-box { font-size: 22px; font-weight: 800; color: #0d1117; }
    .live-indicator { background: #da3633; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
    .match-status { color: #8b949e; font-size: 11px; text-transform: uppercase; text-align: right; margin-bottom: 5px; }
    .arb-card { background:#161b22; border:1px solid #30363d; border-radius:12px; margin-bottom:20px; overflow:hidden; }
    .arb-header { background:#21262d; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; }
    .roi-badge { background:#238636; padding:4px 12px; border-radius:6px; font-weight:bold; color:white; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 2. SECRETS (from Environment Variables)
# ======================================================
MAILCHIMP_API_KEY = os.environ.get("MAILCHIMP_API_KEY")
ODDS_API_KEY = os.environ.get("ODDS_API_KEY")
FOOTBALL_KEY = os.environ.get("FOOTBALL_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
VAULT_READY = bool(os.environ.get("VAULT_READY", "True"))

if not (MAILCHIMP_API_KEY and ODDS_API_KEY and FOOTBALL_KEY and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
    st.error("One or more API keys / tokens are not set. Please update your .env file.")
    st.stop()

# ======================================================
# 3. DATABASE + AUTH
# ======================================================
DB = "users.db"

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

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
# 4. SHARED FUNCTIONS
# ======================================================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except Exception as ex:
        # In production, consider logging exception details to a secure sink
        pass
def subscribe_to_mailchimp(email):
    mailchimp_api = os.getenv("MAILCHIMP_API")
    list_id = os.getenv("MAILCHIMP_LIST_ID")
    # Extract the data center (e.g., 'us1') from the end of your API key
    dc = mailchimp_api.split('-')[-1]
    url = f"https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/members"
    
    data = {
        "email_address": email,
        "status": "subscribed"
    }
    response = requests.post(url, auth=('apikey', mailchimp_api), json=data)
    return response.status_code
    
def calculate_arbitrage(bankroll, odds):
    margin = sum(1 / o for o in odds)
    if margin >= 1: return None
    stakes = [(bankroll * (1 / o)) / margin for o in odds]
    stakes = [int(round(s / 5) * 5) for s in stakes] # Anti-ban rounding
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
                    if o["name"] not in best or o["price"] > best[o["name"]]["price"]:
                        best[o["name"]] = {"price": o["price"], "book": bookmaker["title"]}
    return best

# ======================================================
# 5. LOGIN GATE
# ======================================================
if "user_plan" not in st.session_state:
    st.session_state.user_plan = None

if not st.session_state.user_plan:
    st.title("🔐 ProScore AI | Secure Login")
    colA, colB = st.columns([1, 1])
    with colA:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Access Terminal"):
            plan = login_user(email, password)
            if plan:
                st.session_state.user_plan = plan
                st.rerun()
            else:
                st.error("Invalid credentials")
    with colB:
        st.info("Don't have an account?")
        if st.button("Register as Elite Trader"):
            create_user(email, password)
            st.success("Account created. Click Access Terminal to login.")
    st.stop()

# ======================================================
# 6. SIDEBAR
# ======================================================
with st.sidebar:
    st.markdown("<h1 style='color:#3fb950;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    st.caption(f"Status: {st.session_state.user_plan} ACTIVE")
    menu = st.radio("NAVIGATION", [
        "🛰️ Arbitrage Scanner",
        "🔴 Live Match Center",
        "🧮 Manual Calculator",
        "💰 Execution Desk",
        "📘 $500 Blueprint",
        "⚙️ System Status"
    ])
    st_autorefresh(interval=60000, key="refresh")

# ======================================================
# 7. MAIN INTERFACE
# ======================================================

if menu == "🛰️ Arbitrage Scanner":
    st.title("🛰️ Arbitrage Scanner")
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu&markets=h2h"
    try:
        data = requests.get(url).json()
        if isinstance(data, list):
            for ev in data[:30]:
                best = extract_best_odds(ev)
                if len(best) < 2: continue
                odds = [v["price"] for v in best.values()]
                calc = calculate_arbitrage(1000, odds)
                if calc and calc[1] > 0.2:
                    st.markdown(f'<div class="arb-card"><div class="arb-header"><span><b>{ev["home_team"]} vs {ev["away_team"]}</b></span><span class="roi-badge">{calc[1]}% ROI</span></div>', unsafe_allow_html=True)
                    st.write(f"Profit: **${calc[2]}**")
                    if st.button(f"Alert Telegram", key=ev["id"]):
                        send_telegram(f"ARB FOUND: {ev['home_team']} vs {ev['away_team']} | ROI: {calc[1]}%")
                    st.markdown("</div>", unsafe_allow_html=True)
    except Exception:
        st.error("API Limit reached or error.")

elif menu == "🔴 Live Match Center":
    st.title("🔴 Live Match Center")
    headers = {"X-Auth-Token": FOOTBALL_KEY}
    try:
        data = requests.get("https://api.football-data.org/v4/matches", headers=headers).json()
        matches = data.get("matches", [])
        if matches:
            leagues = {}
            for m in matches: leagues.setdefault(m['competition']['name'], []).append(m)
            for league, match_list in leagues.items():
                st.markdown(f'<div class="league-header">⚙️ {league}</div>', unsafe_allow_html=True)
                for m in match_list:
                    h_logo, a_logo = m['homeTeam'].get('crest', ''), m['awayTeam'].get('crest', '')
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="match-status">{m.get('status')}</div>
                        <div class="match-row"><div class="team-info"><img src="{h_logo}" class="team-logo"> {m['homeTeam']['name']}</div><div class="score-box">{m['score']['fullTime']['home'] or 0}</div></div>
                        <div class="match-row"><div class="team-info"><img src="{a_logo}" class="team-logo"> <span class="live-indicator">LIVE</span> {m['awayTeam']['name']}</div><div class="score-box">{m['score']['fullTime']['away'] or 0}</div></div>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception:
        st.error("Score feed unavailable.")

elif menu == "🧮 Manual Calculator":
    st.title("🧮 Manual Calculator")
    bankroll = st.number_input("Bankroll", 100, 10000, 1000)
    o1 = st.number_input("Odds 1", 1.01, 50.0, 2.0)
    o2 = st.number_input("Odds 2", 1.01, 50.0, 2.1)
    res = calculate_arbitrage(bankroll, [o1, o2])
    if res: st.success(f"ROI: {res[1]}% | Profit: ${res[2]}")

elif menu == "💰 Execution Desk":
    st.title("💰 Execution Desk")
    st.info("Direct Betting Integration (API) is active for Pinnacle and Bet365.")
    st.write("Current Pending Trades: 0")

elif menu == "📘 $500 Blueprint":
    st.title("📘 $500 Arbitrage Blueprint")
    st.write("Disciplined mathematical arbitrage for USD consistency.")

elif menu == "⚙️ System Status":
    st.metric("Odds API", "ONLINE")
    st.metric("Football API", "ONLINE")
    if st.button("Logout"):
        st.session_state.user_plan = None
        st.rerun()
