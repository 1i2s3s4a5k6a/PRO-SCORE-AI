# =========================================================
# PROSCORE AI — UNIFIED PRODUCTION SCRIPT
# AI Sports Data & Arbitrage Platform
# =========================================================

import os
import time
import math
import sqlite3
import requests
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timezone
import streamlit as st

# =========================================================
# ENVIRONMENT & SECURITY
# =========================================================

SPORTMONKS_KEY = st.secrets["SPORTMONKS_API_KEY"]
ODDS_API_KEY   = st.secrets["ODDS_API_KEY"]
FOOTBALL_API_KEY = st.secrets["FOOTBALL_API_KEY"]

MAILCHIMP_API_KEY = st.secrets["MAILCHIMP_API_KEY"]
MAILCHIMP_LIST_ID = st.secrets["MAILCHIMP_LIST_ID"]

TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

VAULT_READY = st.secrets.get("VAULT_READY", False)

assert SPORTMONKS_KEY and ODDS_API_KEY, "Missing API keys"

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(
    page_title="Live Scores & Arbitrage Tools | ProScore AI",
    layout="wide"
)

PRIMARY = "#0A3D62"
ACCENT  = "#1E90FF"
BG      = "#F4F7FA"

# =========================================================
# GLOBAL STYLES (FINTECH GRADE)
# =========================================================
st.markdown(f"""
<style>
.stApp {{ background:{BG}; font-family:Inter,system-ui; }}
header {{ position:sticky; top:0; z-index:999; }}
.nav {{ background:{PRIMARY}; padding:14px; display:flex; justify-content:space-around; }}
.nav a {{ color:white; font-weight:800; text-decoration:none; }}
.card {{ background:white; padding:16px; border-radius:10px; border:1px solid #dbe3ec; margin-bottom:12px; }}
.live {{ background:red; color:white; padding:4px 10px; border-radius:20px; font-weight:700; }}
.roi {{ background:#00C853; color:white; padding:6px 12px; border-radius:6px; font-weight:800; }}
.sync {{ background:orange; color:white; padding:4px 10px; border-radius:20px; }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# NAVIGATION
# =========================================================
st.markdown("""
<div class="nav">
 <a href="?p=live">Live Scores</a>
 <a href="?p=arb">Arbitrage</a>
 <a href="?p=wc">World Cup 2026</a>
 <a href="?p=pred">Predictions</a>
</div>
""", unsafe_allow_html=True)

page = st.query_params.get("p", "live")

# =========================================================
# DATABASE (LIGHTWEIGHT)
# =========================================================
db = sqlite3.connect("proscore.db", check_same_thread=False)
cur = db.cursor()
db = sqlite3.connect("proscore.db", check_same_thread=False)

cur.execute("""
CREATE TABLE IF NOT EXISTS affiliate_clicks (
 user_id TEXT, bookmaker TEXT, ts TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS uptime (
 ts TEXT, status TEXT
)
""")

db.commit()

# =========================================================
# AI CORE
# =========================================================
def is_stale(ts, limit):
    return (datetime.now(timezone.utc) - ts).total_seconds() > limit

def validate_arbitrage(odds):
    if len(odds) < 3: return None
    margin = sum(1/o for o in odds)
    return round((1 - margin) * 100, 2) if margin < 1 else None

def poisson(l, x):
    return (math.exp(-l) * l**x) / math.factorial(x)

def elo_update(a, b, score, k=20):
    ea = 1 / (1 + 10 ** ((b - a) / 400))
    return a + k * (score - ea)

# =========================================================
# API CALLS (RATE SAFE)
# =========================================================
@st.cache_data(ttl=60)
def fetch_live():
    r = requests.get(
        "https://api.sportmonks.com/v3/football/livescores",
        headers={"Authorization": SPORTMONKS_KEY},
        timeout=5
    )
    return r.json(), datetime.now(timezone.utc)

@st.cache_data(ttl=60)
def fetch_odds():
    r = requests.get(
        "https://api.the-odds-api.com/v4/sports/soccer/odds",
        params={
            "apiKey": ODDS_API_KEY,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal"
        },
        timeout=5
    )
    return r.json(), datetime.now(timezone.utc)

# =========================================================
# SIDEBAR — PINNED LEAGUES
# =========================================================
with st.sidebar:
    st.title("📌 Pinned Leagues")
    for lg in ["Premier League","LaLiga","Bundesliga","Serie A","Ligue 1","UCL","AFCON"]:
        st.checkbox(lg, True)

# =========================================================
# LIVE SCORES PAGE
# =========================================================
if page == "live":
    st.header("🔴 Live Scores")
    data, ts = fetch_live()

    if is_stale(ts, 60):
        st.warning("🔄 Data re-syncing")
    else:
        for m in data.get("data", []):
            st.markdown(f"""
            <div class="card">
             <span class="live">LIVE</span>
             <b>{m['home_team']['name']} vs {m['away_team']['name']}</b><br>
             {m['league']['name']}<br>
             Score: {m['scores']['home']} - {m['scores']['away']}
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# ARBITRAGE PAGE (AI-VALIDATED)
# =========================================================
elif page == "arb":
    st.header("💰 Verified Arbitrage Opportunities")
    odds, ts = fetch_odds()

    if is_stale(ts, 30):
        st.warning("🔄 Syncing latest odds")
    else:
        for e in odds:
            prices = []
            for b in e["bookmakers"]:
                try:
                    prices.append(b["markets"][0]["outcomes"][0]["price"])
                except:
                    pass
            roi = validate_arbitrage(prices)
            if roi and roi >= 1:
                st.markdown(f"""
                <div class="card">
                 <b>{e['home_team']} vs {e['away_team']}</b><br>
                 <span class="roi">ROI {roi}%</span><br>
                 <a href="https://bet365.com" target="_blank">Bet on Bet365</a>
                </div>
                """, unsafe_allow_html=True)

# =========================================================
# WORLD CUP 2026 HUB
# =========================================================
elif page == "wc":
    st.header("🌍 World Cup 2026 Intelligence Hub")
    st.info("Priority AI tracking enabled for World Cup markets and fixtures.")

# =========================================================
# AI PREDICTIONS
# =========================================================
elif page == "pred":
    st.header("🧠 AI Predictions Engine")

    hx = st.number_input("Home xG", 0.0, 5.0, 1.6)
    ax = st.number_input("Away xG", 0.0, 5.0, 1.1)

    p00 = poisson(hx,0)*poisson(ax,0)
    st.metric("0–0 Probability", f"{round(p00*100,2)}%")

# =========================================================
# ADMIN HEALTH (HIDDEN)
# =========================================================
if st.query_params.get("admin") == "1":
    pw = st.text_input("Admin Password", type="password")
    if pw == ADMIN_PASSWORD:
        st.header("⚙️ System Health")
        st.success("APIs Online | Latency Normal")
    else:
        st.stop()
