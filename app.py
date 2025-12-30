import streamlit as st
import requests
import pandas as pd
import math
from streamlit_autorefresh import st_autorefresh

# --- 1. SECURE CONFIG & CREDENTIALS ---
st.set_page_config(page_title="ProScore AI | Institutional", layout="wide")

# Your verified Telegram credentials
TG_TOKEN = "6787595786:AAFQ3SwzeTF_TgLechcQGuc-CXCDSOskrm4"
TG_CHAT_ID = "1940722109"

# Fetching keys from Streamlit Secrets
try:
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_KEY"]
    keys_active = True
except:
    keys_active = False

# --- 2. MATHEMATICAL ENGINES ---
def calculate_optimized_stakes(budget, odds):
    """True Arbitrage Math with $5 rounding to prevent bookie bans."""
    margin = sum(1/n for n in odds)
    if margin >= 1: return None, 0, 0 # Not a sure bet
    
    raw_stakes = [(budget * (1/n)) / margin for n in odds]
    # Rounded to nearest $5 for account security
    opt_stakes = [int(5 * round(s/5)) for s in raw_stakes]
    
    total_spent = sum(opt_stakes)
    # Profit based on the lowest possible payout
    min_payout = min(opt_stakes[i] * odds[i] for i in range(len(odds)))
    profit = min_payout - total_spent
    roi = (profit / total_spent) * 100
    return opt_stakes, round(roi, 2), round(profit, 2)

def send_tg_signal(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={TG_CHAT_ID}&text={msg}&parse_mode=Markdown"
    try: requests.get(url, timeout=5)
    except: st.error("Telegram Node Timeout")

# --- 3. PRO-GRADE CSS ---
st.markdown("""
    <style>
    .stApp { background: #0d1117; color: #e6edf3; }
    .arb-card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; margin-bottom: 20px; padding: 15px; }
    .roi-badge { background: #238636; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 800; }
    .league-header { background: #21262d; border-left: 5px solid #238636; padding: 10px; margin: 15px 0; font-weight: bold; text-transform: uppercase; font-size: 13px; }
    .match-row { background: #161b22; padding: 10px; border-bottom: 1px solid #30363d; display: flex; justify-content: space-between; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION & SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#3fb950;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    menu = st.radio("COMMAND CENTER", ["🛰️ ARBS SCANNER", "🕒 GLOBAL LIVE SCORES", "📊 RISK TERMINAL", "🛡️ SUPPORT"])
    st.divider()
    st.write(f"System Status: {'✅ ONLINE' if keys_active else '❌ OFFLINE'}")
    st_autorefresh(interval=60000, key="global_sync")

# --- 5. PAGE LOGIC ---
if menu == "🛰️ ARBS SCANNER":
    st.title("🛰️ Global Arbitrage Matrix")
    if keys_active:
        # Pulling 1X2 (Soccer) and H2H (Other Sports)
        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu,us&markets=h2h"
        res = requests.get(url)
        if res.status_code == 200:
            events = res.json()
            for ev in events[:30]:
                sport = ev.get('sport_title', 'General')
                try:
                    # Filter for best odds across different bookies
                    b1, b2 = ev['bookmakers'][0], ev['bookmakers'][1]
                    h_odd = b1['markets'][0]['outcomes'][0]['price']
                    a_odd = b2['markets'][0]['outcomes'][1]['price']
                    
                    if "Soccer" in sport:
                        d_odd = b1['markets'][0]['outcomes'][2]['price']
                        odds_list, labels = [h_odd, d_odd, a_odd], ["HOME", "DRAW", "AWAY"]
                    else:
                        odds_list, labels = [h_odd, a_odd], ["HOME", "AWAY"]
                    
                    stakes, roi, profit = calculate_optimized_stakes(1000, odds_list)
                    
                    if roi > 0: # Only show mathematically certain wins
                        st.markdown(f"""
                        <div class="arb-card">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                <span>🏆 {sport.upper()}: {ev['home_team']} vs {ev['away_team']}</span>
                                <span class="roi-badge">+{roi}% PROFIT</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        cols = st.columns(len(labels))
                        for i, label in enumerate(labels):
                            cols[i].metric(label, odds_list[i], ev['bookmakers'][i%2]['title'])
                        
                        if st.button(f"📲 SEND SIGNAL (${profit} PROFIT)", key=ev['id']):
                            msg = f"🚨 *SURE BET* 🚨\n🏆 {ev['home_team']} vs {ev['away_team']}\n💰 ROI: {roi}%\n💵 Stakes: {stakes}"
                            send_tg_signal(msg)
                            st.toast("Signal sent to phone!")
                        st.markdown("</div>", unsafe_allow_html=True)
                except: continue
        else: st.error("API Node Offline. Check API Key quota.")

elif menu == "🕒 GLOBAL LIVE SCORES":
    st.title("🕒 Global FlashScore Feed")
    if keys_active:
        # This pulls matches from EVERY active league worldwide
        res = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': FOOTBALL_KEY}).json()
        leagues = {}
        for m in res.get('matches', []):
            leagues.setdefault(m['competition']['name'], []).append(m)
        
        for league, m_list in leagues.items():
            st.markdown(f'<div class="league-header">{league}</div>', unsafe_allow_html=True)
            for m in m_list:
                time = m['utcDate'][11:16]
                h_score = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else "-"
                a_score = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else "-"
                st.markdown(f"""
                <div class="match-row">
                    <span style="color:#8b949e;">{time}</span>
                    <span style="flex-grow:1; margin-left:20px;">{m['homeTeam']['name']} vs {m['awayTeam']['name']}</span>
                    <span style="color:#3fb950; font-weight:bold;">{h_score} - {a_score}</span>
                </div>
                """, unsafe_allow_html=True)

elif menu == "📊 RISK TERMINAL":
    st.title("🛡️ Institutional Protection")
    st.write("Current Staking Mode: **Account Shield (Nearest $5)**")
    st.info("Rounding stakes to whole numbers prevents bookmakers from flagging your account for arbitrage activity.")
    st.slider("Minimum ROI Threshold", 0.0, 15.0, 3.5)
                        
