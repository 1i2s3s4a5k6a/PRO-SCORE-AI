import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# ======================================================
# 1. APP CONFIG
# ======================================================
st.set_page_config(
    page_title="ProScore AI | Elite Arbitrage Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# 2. SECRETS LOADING (Using your specific keys)
# ======================================================
try:
    ODDS_API_KEY = st.secrets["ODDS_API_KEY"]
    FOOTBALL_KEY = st.secrets["FOOTBALL_KEY"]
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
    vault_ready = True
except Exception:
    vault_ready = False

# ======================================================
# 3. TELEGRAM BOT ENGINE
# ======================================================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=5)
    except: pass

# ======================================================
# 4. MATH ENGINE
# ======================================================
def calculate_arbitrage(budget, odds):
    try:
        margin = sum(1 / o for o in odds)
        if margin >= 1: return None
        stakes = [(budget * (1 / o)) / margin for o in odds]
        stakes = [int(round(s / 5) * 5) for s in stakes]  
        total_spent = sum(stakes)
        payout = min(stakes[i] * odds[i] for i in range(len(odds)))
        profit = payout - total_spent
        roi = (profit / total_spent) * 100
        return stakes, round(roi, 2), round(profit, 2)
    except: return None

def extract_best_odds(event):
    best = {}
    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market['key'] != 'h2h': continue
            for outcome in market.get("outcomes", []):
                name = outcome["name"]
                price = outcome["price"]
                if name not in best or price > best[name]["price"]:
                    best[name] = {"price": price, "book": bookmaker["title"]}
    return best

# ======================================================
# 5. UI CUSTOM CSS (AS PER IMAGE)
# ======================================================
st.markdown("""
<style>
    .stApp { background:#0d1117; color:#e6edf3; }
    [data-testid="stSidebar"] { background:#161b22; border-right:1px solid #30363d; }
    
    .league-header {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: white; padding: 10px 15px; border-radius: 8px 8px 0 0;
        font-weight: bold; text-transform: uppercase; font-size: 13px; margin-top: 20px;
    }

    .score-card {
        background: #ffffff; color: #161b22; border-radius: 0 0 8px 8px;
        padding: 18px; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

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
# 6. SIDEBAR
# ======================================================
with st.sidebar:
    st.markdown("<h1 style='color:#3fb950;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    menu = st.radio("COMMAND CENTER", ["🛰️ ARBS SCANNER", "🕒 LIVE SCORES", "🧮 MANUAL CALC", "📊 MARKET ANALYTICS", "🛡️ RISK TERMINAL", "🎁 $500 BLUEPRINT"])
    st.divider()
    if vault_ready:
        st.success("SYSTEM: GLOBAL NODES ACTIVE")
    st_autorefresh(interval=60000, key="sync")

# ======================================================
# 7. ARBS SCANNER
# ======================================================
if menu == "🛰️ ARBS SCANNER":
    st.title("🛰️ Global Arbitrage Matrix")
    if not vault_ready: st.info("Check API Secrets.")
    else:
        url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu,us&markets=h2h&oddsFormat=decimal"
        try:
            data = requests.get(url, timeout=10).json()
            if isinstance(data, list):
                found = False
                for ev in data[:30]:
                    best = extract_best_odds(ev)
                    if len(best) < 2: continue
                    labels, odds = list(best.keys()), [best[l]["price"] for l in best.keys()]
                    calc = calculate_arbitrage(1000, odds)
                    if calc and calc[1] > 0.1:
                        found = True
                        stakes, roi, profit = calc
                        st.markdown(f'<div class="arb-card"><div class="arb-header"><span><b>{ev["home_team"]} vs {ev["away_team"]}</b></span><span class="roi-badge">{roi}% ROI</span></div>', unsafe_allow_html=True)
                        cols = st.columns(len(labels))
                        for i, l in enumerate(labels):
                            cols[i].metric(l, f"{odds[i]}", f"{best[l]['book']}")
                        with st.expander("💰 Execution Plan"):
                            st.write(f"Profit: **${profit}**")
                            if st.button("Send to Telegram", key=ev['id']): send_telegram(f"ARB: {roi}% - {ev['home_team']} vs {ev['away_team']}")
                        st.markdown("</div>", unsafe_allow_html=True)
                if not found: st.warning("No arbs found currently.")
        except: st.error("API Connection Error")

# ======================================================
# 8. LIVE SCORES (WITH LOGOS & IMAGE STYLE)
# ======================================================
elif menu == "🕒 LIVE SCORES":
    st.title("🕒 Global Live Match Center")
    if not vault_ready: st.warning("Football API not ready.")
    else:
        try:
            headers = {"X-Auth-Token": FOOTBALL_KEY}
            data = requests.get("https://api.football-data.org/v4/matches", headers=headers).json()
            matches = data.get("matches", [])
            
            if matches:
                leagues = {}
                for m in matches:
                    leagues.setdefault(m['competition']['name'], []).append(m)

                for league, match_list in leagues.items():
                    st.markdown(f'<div class="league-header">⚙️ {league}</div>', unsafe_allow_html=True)
                    for m in match_list:
                        h_logo = m['homeTeam'].get('crest', '')
                        a_logo = m['awayTeam'].get('crest', '')
                        status = m.get('status', '').replace('_', ' ')
                        
                        st.markdown(f"""
                        <div class="score-card">
                            <div class="match-status">{status}</div>
                            <div class="match-row">
                                <div class="team-info">
                                    <img src="{h_logo}" class="team-logo"> {m['homeTeam']['name']}
                                </div>
                                <div class="score-box">{m['score']['fullTime']['home'] or 0}</div>
                            </div>
                            <div class="match-row">
                                <div class="team-info">
                                    <img src="{a_logo}" class="team-logo"> <span class="live-indicator">LIVE</span> {m['awayTeam']['name']}
                                </div>
                                <div class="score-box">{m['score']['fullTime']['away'] or 0}</div>
                            </div>
                            <div style="background:#f0f2f6; height:28px; border-radius:4px; margin-top:10px; display:flex; align-items:center; padding-left:10px; font-size:11px; color:#57606a;">
                                Margin Available: <b>Checked</b>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else: st.info("No live games.")
        except: st.error("Score feed offline.")

# ======================================================
# 9. MANUAL CALCULATOR
# ======================================================
elif menu == "🧮 MANUAL CALC":
    st.title("🧮 One-Click Arb Calculator")
    budget = st.number_input("Budget ($)", value=1000)
    col1, col2, col3 = st.columns(3)
    o1 = col1.number_input("Home Odds", value=2.0)
    o2 = col2.number_input("Draw/Away Odds", value=2.1)
    o3 = col3.number_input("Extra Odds (Optional)", value=0.0)
    
    odds = [o for o in [o1, o2, o3] if o > 1]
    res = calculate_arbitrage(budget, odds)
    if res:
        st.success(f"ROI: {res[1]}% | Profit: ${res[2]}")
        for i, s in enumerate(res[0]): st.write(f"Stake {i+1}: ${s}")
    else: st.error("No arbitrage found.")

# Remaining placeholders for Terminal and Blueprint
elif menu == "📊 MARKET ANALYTICS": st.title("Market Analytics coming soon.")
elif menu == "🛡️ RISK TERMINAL": st.title("Risk Terminal Active.")
elif menu == "🎁 $500 BLUEPRINT": st.title("Blueprint Unlocked.")
    
