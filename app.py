import streamlit as st
import requests
import pandas as pd
from textblob import TextBlob
import os

# --- CRITICAL FIX FOR STREAMLIT CLOUD ---
# This downloads the necessary data for sentiment analysis automatically
try:
    import nltk
    nltk.download('punkt_tab') # Lightweight version of the data needed
except:
    os.system("python -m textblob.download_corpora lite")
# ----------------------------------------

# --- CONFIG ---
API_KEY = "dac17517d43d471e94d2b2484ef5df96"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_KEY}

st.set_page_config(page_title="AI Betting HQ", layout="wide")

# ... [Previous data helpers for teams and scores] ...

st.title("🛡️ AI Betting & Sentiment Suite")

tabs = st.tabs(["Scores", "Research", "News & Sentiment", "Arbitrage", "Bankroll", "Aviator"])

# --- TAB 3: NEWS & AI SENTIMENT ---
with tabs[2]:
    st.header("📰 News Sentiment Analysis")
    st.write("AI scans headlines to see if the 'vibe' around a team is positive or negative.")
    
    news_url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.goal.com/en/feeds/news"
    try:
        news_res = requests.get(news_url).json()
        if news_res['status'] == 'ok':
            for item in news_res['items'][:10]:
                headline = item['title']
                
                # --- AI SENTIMENT CALCULATION ---
                analysis = TextBlob(headline)
                score = analysis.sentiment.polarity # Returns -1.0 to 1.0
                
                if score > 0.1:
                    sentiment_label = "🟢 POSITIVE"
                    color = "green"
                elif score < -0.1:
                    sentiment_label = "🔴 NEGATIVE"
                    color = "red"
                else:
                    sentiment_label = "⚪ NEUTRAL"
                    color = "gray"
                
                with st.expander(f"{sentiment_label} | {headline}"):
                    st.write(f"**AI Confidence Score:** {score:.2f}")
                    st.write(item['description'])
                    st.link_button("View Source", item['link'])
    except:
        st.error("Unable to reach news servers.")

# [Rest of your previous Arbitrage, Bankroll, and Aviator tabs]
