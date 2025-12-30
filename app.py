import streamlit as st
import requests
import sqlite3
import hashlib
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ======================================================
# 1. APP CONFIG
# ======================================================
st.set_page_config(
    page_title="ProScore AI | Arbitrage Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# 2. SECRETS
# ======================================================
try:
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_KEY"]
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
    VAULT_READY = True
except:
    VAULT_READY = False

# ======================================================
# 3. DATABASE + AUTH
# ======================================================
DB = "users.db"

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT,
        plan TEXT
    )
    """)
    conn.commit()
    conn.close()

def create_user(email, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?)",
              (email, hash_pw(password), "FREE"))
    conn.commit()
    conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT plan FROM users WHERE email=? AND password=?",
              (email, hash_pw(password)))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

init_db()

# ======================================================
# 4. TELEGRAM
# ======================================================
def send_telegram(msg):
    if not VAULT_READY:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg
        }, timeout=5)
    except:
        pass

# ======================================================
# 5. ARBITRAGE ENGINE
# ======================================================
def calculate_arbitrage(bankroll, odds):
    margin = sum(1 / o for o in odds)
    if margin >= 1:
        return None
    stakes = [(bankroll * (1 / o)) / margin for o in odds]
    payout = min(stakes[i] * odds[i] for i in range(len(odds)))
    profit = payout - sum(stakes)
    roi = (profit / sum(stakes)) * 100
    return stakes, round(roi, 2), round(profit, 2)

def extract_best_odds(event):
    best = {}
    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market["key"] != "h2h":
                continue
            for o in market["outcomes"]:
                if o["name"] not in best or o["price"] > best[o["name"]]["price"]:
                    best[o["name"]] = {
                        "price": o["price"],
                        "book": bookmaker["title"]
                    }
    return best

def execution_plan(stakes, books):
    return [{"bookmaker": books[i], "stake": round(stakes[i],2), "status":"READY"}
            for i in range(len(stakes))]

# ======================================================
# 6. LOGIN GATE
# ======================================================
if "user_plan" not in st.session_state:
    st.session_state.user_plan = None

if not st.session_state.user_plan:
    st.title("🔐 ProScore AI Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    if col1.button("Login"):
        plan = login_user(email, password)
        if plan:
            st.session_state.user_plan = plan
            st.rerun()
        else:
            st.error("Invalid credentials")

    if col2.button("Register"):
        create_user(email, password)
        st.success("Account created. Please login.")
    st.stop()

# ======================================================
# 7. SIDEBAR
# ======================================================
with st.sidebar:
    st.markdown("## 🚀 PROSCORE AI")
    st.caption(f"Plan: {st.session_state.user_plan}")

    menu = st.radio("NAVIGATION", [
        "🛰️ Arbitrage Scanner",
        "🔴 Live Events",
        "📅 Upcoming Events",
        "🧮 Manual Calculator",
        "💰 Execution Desk",
        "📘 $500 Blueprint",
        "⚙️ System Status"
    ])
    st_autorefresh(interval=60000, key="refresh")

# ======================================================
# 8. ARBITRAGE SCANNER (PRO)
# ======================================================
if menu == "🛰️ Arbitrage Scanner":
    if st.session_state.user_plan == "FREE":
        st.warning("Upgrade to PRO to access arbitrage scanner.")
    else:
        st.title("🛰️ Arbitrage Scanner")
        url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu&markets=h2h"
        data = requests.get(url).json()

        for ev in data[:30]:
            best = extract_best_odds(ev)
            if len(best) < 2:
                continue
            odds = [v["price"] for v in best.values()]
            calc = calculate_arbitrage(1000, odds)
            if calc and calc[1] > 0.2:
                st.subheader(f"{ev['home_team']} vs {ev['away_team']}")
                st.success(f"ROI: {calc[1]}% | Profit: ${calc[2]}")
                if st.button("Send to Telegram", key=ev["id"]):
                    send_telegram(f"ARB FOUND: {ev['home_team']} vs {ev['away_team']}")

# ======================================================
# 9. EXECUTION DESK (ELITE)
# ======================================================
elif menu == "💰 Execution Desk":
    if st.session_state.user_plan != "ELITE":
        st.warning("Elite access only.")
    else:
        st.title("💰 Execution Desk")
        stakes = [200, 180]
        books = ["Bet365", "Pinnacle"]
        plan = execution_plan(stakes, books)
        for p in plan:
            st.write(p)

# ======================================================
# 10. LIVE / UPCOMING
# ======================================================
elif menu == "🔴 Live Events":
    headers = {"X-Auth-Token": FOOTBALL_KEY}
    matches = requests.get("https://api.football-data.org/v4/matches", headers=headers).json().get("matches", [])
    live = [m for m in matches if m["status"] == "LIVE"]
    for m in live:
        st.write(m["homeTeam"]["name"], "vs", m["awayTeam"]["name"])

elif menu == "📅 Upcoming Events":
    headers = {"X-Auth-Token": FOOTBALL_KEY}
    matches = requests.get("https://api.football-data.org/v4/matches", headers=headers).json().get("matches", [])
    upcoming = [m for m in matches if m["status"] == "SCHEDULED"]
    for m in upcoming[:20]:
        st.write(m["homeTeam"]["name"], "vs", m["awayTeam"]["name"], m["utcDate"])

# ======================================================
# 11. MANUAL CALC
# ======================================================
elif menu == "🧮 Manual Calculator":
    bankroll = st.number_input("Bankroll", 100, 10000, 1000)
    o1 = st.number_input("Odds 1", 1.01, 50.0, 2.0)
    o2 = st.number_input("Odds 2", 1.01, 50.0, 2.1)
    res = calculate_arbitrage(bankroll, [o1, o2])
    if res:
        st.success(f"ROI: {res[1]}% | Profit: ${res[2]}")

# ======================================================
# 12. BLUEPRINT
# ======================================================
elif menu == "📘 $500 Blueprint":
    st.title("📘 $500 Arbitrage Blueprint")
    st.write("""
    This blueprint teaches disciplined, mathematical arbitrage.
    Built for traders who want **USD consistency**, not gambling.
    """)

# ======================================================
# 13. SYSTEM STATUS
# ======================================================
elif menu == "⚙️ System Status":
    st.metric("Odds API", "ONLINE" if VAULT_READY else "OFFLINE")
    st.metric("User Plan", st.session_state.user_plan)
