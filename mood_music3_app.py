import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from transformers import pipeline

st.set_page_config(page_title="Mood Music Recommender", page_icon="🎵")
st.title("🎧 Mood-Based Music Recommender")

st.markdown("""
Type how you feel — and get a Spotify playlist that fits your vibe!
""")

# Text-based mood detection
user_text = st.text_input("📝 How are you feeling today?")

if user_text:
    with st.spinner("Analyzing your mood... 🧠"):
        sentiment_analyzer = pipeline("sentiment-analysis")
        result = sentiment_analyzer(user_text)[0]
        label = result['label']
        mood = "Happy" if label.lower() == "positive" else "Sad" if label.lower() == "negative" else "Neutral"
        st.success(f"Detected mood: **{mood}**")

    # Spotify setup
    SPOTIFY_CLIENT_ID = st.secrets["spotify"]["client_id"]
    SPOTIFY_CLIENT_SECRET = st.secrets["spotify"]["client_secret"]

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
