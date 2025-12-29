import streamlit as st
import requests
import pandas as pd
from textblob import TextBlob
import nltk

# --- STABILITY FIX: Silent NLTK Download ---
@st.cache_resource
def load_ai_logic():
    try:
        # We only download the bare minimum needed for sentiment
        nltk.download('punkt', quiet=True)
        nltk.download('brown', quiet=True)
    except:
        pass

load_ai_logic()

# --- API CONFIG ---
API_KEY = "dac17517d43d471e94d2b2484ef5df96"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {'X-Auth-Token': API_KEY}

st.set_page_config(page_title="AI Betting HQ", layout="wide")

# --- DATA HELPERS ---
@st.cache_data(ttl=3600)
def get_league_teams(league_code):
    try:
        res = requests.get(f"{BASE_URL}competitions/{league_code}/teams", headers=HEADERS).json()
        return {t['name']: t['id'] for t in res['teams']}
    except: return {}

# --- APP LAYOUT ---
st.title("🛡️ AI Betting & Intelligence Suite")

# Use a selectbox for navigation if tabs are freezing
page = st.sidebar.selectbox("Navigate", ["Live Scores", "H2H Research", "News & Sentiment", "Arbitrage", "Bankroll", "Aviator"])

if page == "Live Scores":
    st.header("🕒 Live & Upcoming Matches")
    if st.button("Refresh Results"):
        res = requests.get(f"{BASE_URL}matches", headers=HEADERS).json()
        if 'matches' in res and res['matches']:
            data = [{"Status": m['status'], "Home": m['homeTeam']['name'], "Away": m['awayTeam']['name'], 
                     "Score": f"{m['score']['fullTime']['home']} - {m['score']['fullTime']['away']}", 
                     "League": m['competition']['name']} for m in res['matches']]
            st.table(pd.DataFrame(data))
        else: st.info("No matches today.")

elif page == "News & Sentiment":
    st.header("📰 News & AI Vibe Check")
    news_url = "https://api.rss2json.com/v1/api.json?rss_url=https://www.goal.com/en/feeds/news"
    try:
        news_res = requests.get(news_url).json()
        if news_res['status'] == 'ok':
            for item in news_res['items'][:8]:
                blob = TextBlob(item['title'])
                score = blob.sentiment.polarity
                sentiment = "🟢 POSITIVE" if score > 0.1 else "🔴 NEGATIVE" if score < -0.1 else "⚪ NEUTRAL"
                with st.expander(f"{sentiment} | {item['title']}"):
                    st.write(item['description'])
                    st.link_button("Read More", item['link'])
    except: st.error("News feed currently unavailable.")

# ... [Include your H2H, Arbitrage, Bankroll, and Aviator logic as separate 'elif' blocks] ...
