import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from textblob import TextBlob

# -------------------------------
# 🎧 APP CONFIG
# -------------------------------
st.set_page_config(page_title="Mood Music Recommender", page_icon="🎵")
st.title("🎧 Mood-Based Music Recommender")

st.markdown("""
Type how you feel — and get a Spotify playlist that matches your vibe!
""")

# -------------------------------
# 💬 TEXT INPUT
# -------------------------------
user_text = st.text_input("📝 How are you feeling today?")

if user_text:
    with st.spinner("Analyzing your mood... 🧠"):
        blob = TextBlob(user_text)
        polarity = blob.sentiment.polarity

        if polarity > 0.2:
            mood = "Happy"
        elif polarity < -0.2:
            mood = "Sad"
        else:
            mood = "Neutral"

        st.success(f"Detected mood: **{mood}** 😄")

    # -------------------------------
    # 🔐 LOAD SPOTIFY CREDENTIALS SAFELY
    # -------------------------------
    SPOTIFY_CLIENT_ID = None
    SPOTIFY_CLIENT_SECRET = None

    # Try to read from secrets
    if "spotify" in st.secrets:
        SPOTIFY_CLIENT_ID = st.secrets["spotify"].get("client_id")
        SPOTIFY_CLIENT_SECRET = st.secrets["spotify"].get("client_secret")

    # Optional fallback for local testing (no secrets.toml)
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        SPOTIFY_CLIENT_ID = st.text_input("Enter Spotify Client ID:", type="password")
        SPOTIFY_CLIENT_SECRET = st.text_input("Enter Spotify Client Secret:", type="password")

    # If still missing — stop gracefully
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        st.error("⚠️ Spotify credentials not found. Please set them in Streamlit secrets or enter manually.")
        st.stop()

    # -------------------------------
    # 🎵 SPOTIFY PLAYLISTS
    # -------------------------------
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))

        mood_to_genre = {
            "Happy": "pop",
            "Sad": "acoustic",
            "Neutral": "chill"
        }

        genre = mood_to_genre.get(mood, "chill")

        with st.spinner(f"Fetching {genre} playlists from Spotify..."):
            results = sp.search(q=f"playlist {genre}", type="playlist", limit=5)

        st.subheader(f"Recommended {genre.capitalize()} Playlists 🎶")

        for playlist in results['playlists']['items']:
            st.markdown(f"**[{playlist['name']}]({playlist['external_urls']['spotify']})**")
            if playlist['images']:
                st.image(playlist['images'][0]['url'], width=250)
            st.write("---")

    except Exception as e:
        st.error(f"❌ Spotify API Error: {e}")
