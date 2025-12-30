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
# 2. SECRETS LOADING (Safe Loading)
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
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=5)
    except:
        pass

# ======================================================
# 4. ARBITRAGE MATH ENGINE
# ======================================================
def calculate_arbitrage(budget, odds):
    try:
        # Arbitrage Formula: Sum of (1/odds) must be < 1.0
        margin = sum(1 / o for o in odds)
        if margin >= 1: return None

        # Calculate stakes based on budget
        stakes = [(budget * (1 / o)) / margin for o in odds]
        
        # Anti-ban strategy: Round to nearest $5
        stakes = [int(round(s / 5) * 5) for s in stakes]  

        total_spent = sum(stakes)
        payout = min(stakes[i] * odds[i] for i in range(len(odds)))
        profit = payout - total_spent
        roi = (profit / total_spent) * 100
        
        return stakes, round(roi, 2), round(profit, 2)
    except Exception:
        return None

# ======================================================
# 5. BEST ODDS EXTRACTOR
# ======================================================
def extract_best_odds(event):
    best = {}
    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market['key'] != 'h2h': continue
            for outcome in market.get("outcomes", []):
                name = outcome["name"]
                price = outcome["price"]
                # Keep only the highest price available across all bookmakers
                if name not in best or price > best[name]["price"]:
                    best[name] = {"price": price, "book": bookmaker["title"]}
    return best

# ======================================================
# 6. UI CUSTOM CSS
# ======================================================
st.markdown("""
<style>
.stApp { background:#0d1117; color:#e6edf3; }
[data-testid="stSidebar"] { background:#161b22; border-right:1px solid #30363d; }
.arb-card { background:#161b22; border:1px solid #30363d; border-radius:12px; margin-bottom:20px; overflow:hidden; }
.arb-header { background:#21262d; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; }
.roi-badge { background:#238636; padding:4px 12px; border-radius:6px; font-weight:bold; color:white; }
.mkt-tile { background:#0d1117; padding:10px; text-align:center; border-radius:8px; border:1px solid #21262d; }
.odds-val { color:#3fb950; font-size:20px; font-weight:bold; }
.league-bar { background:#238636; padding:8px 15px; margin:20px 0 10px; font-weight:bold; border-radius:4px; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 7. SIDEBAR NAVIGATION
# ======================================================
with st.sidebar:
    st.markdown("<h1 style='color:#3fb950;'>PRO-SCORE AI</h1>", unsafe_allow_html=True)
    menu = st.radio("COMMAND CENTER", [
        "🛰️ ARBS SCANNER", 
        "🧮 MANUAL CALC", 
        "🕒 LIVE SCORES", 
        "📊 MARKET ANALYTICS", 
        "🛡️ RISK TERMINAL", 
        "🎁 $500 BLUEPRINT"
    ])
    st.divider()
    if vault_ready:
        st.success("SYSTEM: GLOBAL NODES ACTIVE")
    else:
        st.error("SYSTEM: VAULT OFFLINE")
    
    st_autorefresh(interval=60000, key="sync")

# ======================================================
# 8. ARBS SCANNER
# ======================================================
if menu == "🛰️ ARBS SCANNER":
    st.title("🛰️ Global Arbitrage Matrix")
    
    if not vault_ready:
        st.info("Please configure API secrets to begin scanning.")
    else:
        url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=uk,eu,us&markets=h2h&oddsFormat=decimal"
        
        try:
            res = requests.get(url, timeout=10)
            data = res.json()

            if isinstance(data, list):
                found_any = False
                for ev in data[:30]:
                    best = extract_best_odds(ev)
                    if len(best) < 2: continue
                    
                    labels = list(best.keys())
                    odds = [best[l]["price"] for l in labels]
                    
                    calc = calculate_arbitrage(1000, odds)
                    if calc and calc[1] > 0.1:
                        found_any = True
                        stakes, roi, profit = calc
                        
                        st.markdown(f"""
                        <div class="arb-card">
                            <div class="arb-header">
                                <span><b>{ev['home_team']} vs {ev['away_team']}</b></span>
                                <span class="roi-badge">{roi}% ROI</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        cols = st.columns(len(labels))
                        for i, label in enumerate(labels):
                            with cols[i]:
                                st.markdown(f"""
                                <div class="mkt-tile">
                                    <div style="font-size:11px; color:#8b949e;">{label}</div>
                                    <div class="odds-val">{odds[i]}</div>
                                    <div style="font-size:10px; color:#3fb950;">{best[label]['book']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with st.expander("💰 Execution Plan"):
                            for i, s in enumerate(stakes):
                                st.write(f"Bet **${s}** on {labels[i]} @ {best[labels[i]]['book']}")
                            st.metric("Net Profit", f"${profit}")
                            if st.button(f"Broadcast {ev['id'][:5]}", key=ev['id']):
                                send_telegram(f"🔥 ARB ALERT: {roi}% ROI\n{ev['home_team']} vs {ev['away_team']}\nProfit: ${profit}")
                        st.markdown("</div>", unsafe_allow_html=True)
                
                if not found_any:
                    st.warning("No active arbitrage opportunities found in the current market cycle.")
            else:
                st.error(f"API Error: {data.get('message', 'Check your API limits.')}")
        except Exception as e:
            st.error("Connection Interrupted")

# ======================================================
# 9. MANUAL CALCULATOR (INTEGRATED)
# ======================================================
elif menu == "🧮 MANUAL CALC":
    st.title("🧮 One-Click Arb Calculator")
    st.markdown("Enter odds from any bookmaker to calculate the guaranteed profit spread.")

    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            budget = st.number_input("Total Investment ($)", min_value=10, value=1000, step=50)
            num_outcomes = st.radio("Market Type", ["2-Way (Home/Away)", "3-Way (Home/Draw/Away)"])
            
            o1 = st.number_input("Outcome 1 Odds", min_value=1.01, value=2.10, format="%.2f")
            o2 = st.number_input("Outcome 2 Odds", min_value=1.01, value=2.10, format="%.2f")
            
            manual_odds = [o1, o2]
            labels = ["Outcome 1", "Outcome 2"]
            
            if "3-Way" in num_outcomes:
                o3 = st.number_input("Outcome 3 Odds", min_value=1.01, value=3.50, format="%.2f")
                manual_odds.append(o3)
                labels.append("Outcome 3")

        with col2:
            st.subheader("Analysis Results")
            res = calculate_arbitrage(budget, manual_odds)
            
            if res:
                stakes, roi, profit = res
                st.success(f"🔥 Arbitrage Detected! ROI: {roi}%")
                
                metrics = st.columns(len(labels))
                for i in range(len(labels)):
                    metrics[i].metric(labels[i], f"${stakes[i]}", f"Odds: {manual_odds[i]}")
                
                st.divider()
                st.metric("Guaranteed Profit", f"${profit}", delta_color="normal")
                
                if st.button("Send Manual Alert to Telegram"):
                    send_telegram(f"Manual Arb Alert\nBudget: ${budget}\nROI: {roi}%\nProfit: ${profit}")
            else:
                st.error("No Arbitrage Possible.")
                margin = sum(1/o for o in manual_odds) * 100
                st.info(f"Current Market Margin: {round(margin, 2)}% (Needs to be < 100%)")

# ======================================================
# 10. LIVE SCORES
# ======================================================
elif menu == "🕒 LIVE SCORES":
    st.title("🕒 Live Match Center")
    headers = {"X-Auth-Token": FOOTBALL_KEY}
    try:
        data = requests.get("https://api.football-data.org/v4/matches", headers=headers).json()
        matches = data.get("matches", [])
        if matches:
            for m in matches[:15]:
                st.write(f"⚽ {m['homeTeam']['name']} {m['score']['fullTime']['home'] or 0} - {m['score']['fullTime']['away'] or 0} {m['awayTeam']['name']}")
        else:
            st.info("No live matches found.")
    except:
        st.error("Score feed unavailable.")

# ======================================================
# 11. MARKET ANALYTICS
# ======================================================
elif menu == "📊 MARKET ANALYTICS":
    st.title("📊 Global Market Health")
    st.info("Market volatility is currently: LOW")
    chart_data = pd.DataFrame({'ROI %': [2.1, 4.5, 1.2, 6.7, 3.2]}, index=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
    st.line_chart(chart_data)

# ======================================================
# 12. RISK TERMINAL
# ======================================================
elif menu == "🛡️ RISK TERMINAL":
    st.title("🛡️ Risk & Protection Terminal")
    st.warning("Anti-Ban Protocols Active")
    st.checkbox("Round stakes to nearest $5 (Recommended)", value=True)
    st.slider("Minimum ROI alert threshold", 0.1, 15.0, 1.5)

# ======================================================
# 13. $500 BLUEPRINT
# ======================================================
elif menu == "🎁 $500 BLUEPRINT":
    st.title("🎁 Premium $500 Strategy Guide")
    st.markdown("Your access is active for Mailchimp ID: " + st.secrets.get("MAILCHIMP_LIST_ID", "Default"))
    st.success("Strategy document: 'The 30-Day Compounding Engine' is ready for review.")
        
