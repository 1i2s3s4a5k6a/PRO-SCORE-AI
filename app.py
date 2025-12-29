import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pro Bet AI Partner", layout="centered")

st.title("📱 Pro Bet AI Partner")
st.write("Use math to beat the house edge.")

# --- SIDEBAR: BANKROLL SETTINGS ---
st.sidebar.header("Bankroll Settings")
initial_bankroll = st.sidebar.number_input("Starting Bankroll ($)", value=1000.0, step=10.0)
kelly_multiplier = st.sidebar.slider("Kelly Fraction (0.5 is recommended)", 0.1, 1.0, 0.5)

# --- MAIN INTERFACE: BET CALCULATOR ---
st.header("Calculate Your Edge")
col1, col2 = st.columns(2)

with col1:
    odds = st.number_input("Decimal Odds (e.g., 2.10)", value=2.00, step=0.01)
with col2:
    win_prob = st.slider("Your Win Probability (%)", 0, 100, 52) / 100

# Kelly Calculation
b = odds - 1
f_star = ((b * win_prob) - (1 - win_prob)) / b
suggested_bet = initial_bankroll * f_star * kelly_multiplier

if f_star > 0:
    st.success(f"✅ VALUE DETECTED: Suggested Bet is ${suggested_bet:.2f}")
    st.info(f"Bet {round(f_star * kelly_multiplier * 100, 2)}% of your total bankroll.")
else:
    st.error("❌ NO VALUE: The math favors the house. Do not bet.")

# --- MONTE CARLO SIMULATION ---
st.header("1,000-Bet Stress Test")
st.write("What happens if you play this 'edge' 1,000 times?")

if st.button("Run Simulation"):
    all_runs = []
    for _ in range(5):
        current_br = initial_bankroll
        history = [current_br]
        for _ in range(1000):
            if f_star > 0:
                wager = current_br * f_star * kelly_multiplier
                if random.random() < win_prob:
                    current_br += (wager * b)
                else:
                    current_br -= wager
            current_br = max(0, current_br)
            history.append(current_br)
        all_runs.append(history)

    # Plotting
    fig, ax = plt.subplots()
    for run in all_runs:
        ax.plot(run)
    ax.axhline(y=initial_bankroll, color='r', linestyle='--')
    ax.set_ylabel("Bankroll ($)")
    ax.set_xlabel("Number of Bets")
    st.pyplot(fig)


  
