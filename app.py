import streamlit as st
import requests
import pandas as pd
import math

# --- CONFIG ---
API_KEY = "dac17517d43d471e94d2b2484ef5df96"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_KEY}

st.set_page_config(page_title="AI Football Scout", layout="wide")

# --- SIDEBAR: TEAM ID LOOK-UP ---
st.sidebar.header("🔍 Team ID Look-up")
look_league = st.sidebar.selectbox("Select League for IDs", ["PL", "BL1", "SA", "PD", "FL1"])

@st.cache_data(ttl=86400)
def get_team_ids(league_code):
    try:
        response = requests.get(f"{BASE_URL}competitions/{league_code}/teams", headers=HEADERS)
        data = response.json()
        return pd.DataFrame([{"ID": t['id'], "Name": t['name']} for t in data['teams']])
    except:
        return pd.DataFrame(columns=["ID", "Name"])

st.sidebar.dataframe(get_team_ids(look_league), hide_index=True)

# --- MAIN INTERFACE ---
st.title("⚽ AI Football Scout & Professional Betting Suite")

tabs = st.tabs(["Research & H2H", "Arbitrage Scanner", "Kelly & Risk", "Goal Path", "Glossary"])

with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.header("League Standings")
        league = st.selectbox("League", ["PL", "BL1", "SA", "PD", "FL1"])
        if st.button("Fetch Table"):
            data = requests.get(f"{BASE_URL}competitions/{league}/standings", headers=HEADERS).json()
            if 'standings' in data:
                table = data['standings'][0]['table']
                st.table(pd.DataFrame([{"Pos": t['position'], "Team": t['team']['name'], "Form": t['form'], "Pts": t['points']} for t in table]).set_index("Pos"))
    with col2:
        st.header("H2H History")
        id_a = st.number_input("Team A ID", value=64)
        id_b = st.number_input("Team B ID", value=65)
        if st.button("Analyze Matchup"):
            res = requests.get(f"{BASE_URL}teams/{id_a}/matches?competitors={id_b}", headers=HEADERS).json()
            if 'matches' in res and len(res['matches']) > 0:
                matches = res['matches']
                st.dataframe(pd.DataFrame([{"Date": m['utcDate'][:10], "Score": f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}", "Winner": m['score']['winner']} for m in matches]))

with tabs[1]:
    st.header("⚖️ Arbitrage (Guaranteed Profit) Calculator")
    st.write("Find odds for the same game at two different bookies. If the Arbitrage % is < 100, you win regardless of the outcome.")
    
    col_a, col_b = st.columns(2)
    odds_1 = col_a.number_input("Bookie A Odds (Team 1)", value=2.10)
    odds_2 = col_b.number_input("Bookie B Odds (Team 2/Draw)", value=2.10)
    total_investment = st.number_input("Total Amount to Invest ($)", value=100.0)
    
    arb_pct = (1/odds_1) + (1/odds_2)
    st.metric("Arbitrage Percentage", f"{arb_pct*100:.2f}%")
    
    if arb_pct < 1.0:
        st.success("✅ ARBITRAGE OPPORTUNITY FOUND!")
        stake_1 = (total_investment / (odds_1 * arb_pct))
        stake_2 = (total_investment / (odds_2 * arb_pct))
        profit = total_investment / arb_pct - total_investment
        st.write(f"Bet **${stake_1:.2f}** on Bookie A")
        st.write(f"Bet **${stake_2:.2f}** on Bookie B")
        st.write(f"**Guaranteed Profit: ${profit:.2f}**")
    else:
        st.error("No Arbitrage here. The house has the edge.")

with tabs[2]:
    st.header("Kelly Wager & Risk of Ruin")
    br = st.number_input("Bankroll ($)", value=1000.0)
    o = st.number_input("Odds", value=2.0, key="k_odds")
    p = st.slider("Win Prob (%)", 1, 100, 52) / 100
    
    b_val = o - 1
    f_star = ((b_val * p) - (1 - p)) / b_val
    if f_star > 0:
        st.success(f"Suggested Bet: ${br * f_star * 0.5:.2f}")
        # Risk of Ruin
        ror = ((1-p)/p) ** (br / (br * f_star * 0.5))
        st.metric("Risk of Ruin", f"{ror*100:.4f}%")
    else:
        st.error("Negative Expectancy. Skip this bet.")

with tabs[3]:
    st.header("🚀 Goal Path")
    target = st.number_input("Profit Goal ($)", value=5000.0)
    if f_star > 0:
        ev = (p * (br * f_star * 0.5 * (o - 1))) - ((1 - p) * br * f_star * 0.5)
        bets = math.ceil((target - br) / ev) if ev > 0 else 0
        st.title(f"{bets} Bets to reach goal")

with tabs[4]:
    st.header("📚 Pro Betting Glossary")
    st.write("**Kelly Criterion:** A formula used to determine the optimal size of a bet to maximize long-term wealth.")
    st.write("**Arbitrage (Arb):** Placing bets on all possible outcomes of an event across different bookmakers to guarantee a profit.")
    st.write("**Expected Value (EV):** The average amount a player can expect to win or lose per bet placed on the same odds many times.")
    st.write("**Risk of Ruin (RoR):** The mathematical probability that you will lose your entire bankroll.")
    st.write("**H2H:** Head-to-Head. The historical record of matches between two specific teams.")
