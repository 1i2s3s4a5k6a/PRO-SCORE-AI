import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pro AI Betting Partner", layout="centered")

st.title("📱 AI Betting Dashboard")
st.markdown("---")

# --- SESSION STATE FOR TRACKING ---
if 'history' not in st.session_state:
    st.session_state.history = [0]

# --- SIDEBAR ---
st.sidebar.header("Bankroll & Strategy")
initial_bankroll = st.sidebar.number_input("Total Bankroll ($)", value=1000.0)
kelly_multiplier = st.sidebar.slider("Kelly Fraction", 0.1, 1.0, 0.5)

# --- TABBED INTERFACE ---
tab1, tab2, tab3, tab4 = st.tabs(["Value Detector", "Parlay/Hedge", "Unit Tracker", "Stress Test"])

with tab1:
    st.header("Find Your Edge")
    odds = st.number_input("Decimal Odds", value=2.00)
    win_prob = st.slider("Win Probability (%)", 1, 100, 52) / 100
    
    b = odds - 1
    f_star = ((b * win_prob) - (1 - win_prob)) / b
    
    if f_star > 0:
        amount = initial_bankroll * f_star * kelly_multiplier
        st.success(f"✅ Edge Found! Recommended Bet: ${amount:.2f}")
    else:
        st.error("❌ No Edge. The house algorithm wins here.")

with tab2:
    st.header("Hedge & Parlay Tools")
    mode = st.radio("Tool Type", ["Hedge Calculator", "Parlay Probability"])
    
    if mode == "Hedge Calculator":
        potential_payout = st.number_input("Parlay Payout ($)", value=500.0)
        hedge_odds = st.number_input("Hedge (Opponent) Odds", value=2.00)
        hedge_bet = potential_payout / hedge_odds
        st.info(f"💰 Hedge Bet: ${hedge_bet:.2f} | Guaranteed Profit: ${potential_payout - hedge_bet:.2f}")
    else:
        legs = st.number_input("Legs", 1, 10, 3)
        p_leg = st.slider("Avg Leg Win %", 1, 100, 52) / 100
        st.metric("Win Probability", f"{(p_leg**legs)*100:.2f}%")

with tab3:
    st.header("Performance Tracker")
    st.write("Log your daily profit or loss to see your curve.")
    
    with st.form("log_form"):
        daily_result = st.number_input("Today's Profit/Loss ($)", value=0.0)
        submit = st.form_submit_button("Add to History")
        
        if submit:
            new_total = st.session_state.history[-1] + daily_result
            st.session_state.history.append(new_total)
    
    if len(st.session_state.history) > 1:
        st.line_chart(st.session_state.history)
        st.write(f"Total Session P/L: ${st.session_state.history[-1]:.2f}")

with tab4:
    st.header("Risk Simulation")
    if st.button("Simulate 1,000 Bets"):
        all_runs = []
        for _ in range(3):
            current_br = initial_bankroll
            history = [current_br]
            for _ in range(1000):
                if f_star > 0:
                    wager = current_br * f_star * kelly_multiplier
                    current_br += (wager * (odds-1)) if random.random() < win_prob else -wager
                history.append(max(0, current_br))
            all_runs.append(history)
        
        fig, ax = plt.subplots()
        for run in all_runs: ax.plot(run)
        st.pyplot(fig)
