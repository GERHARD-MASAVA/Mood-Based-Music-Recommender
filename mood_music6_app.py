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
    client_id = None
    client_secret = None

    if "spotify" in st.secrets:
        client_id = st.secrets["spotify"].get("client_id")
        client_secret = st.secrets["spotify"].get("client_secret")

    if not client_id or not client_secret:
        st.warning("⚠️ Spotify credentials not found. Please enter them manually for now.")
        client_id = st.text_input("Spotify Client ID", type="password")
        client_secret = st.text_input("Spotify Client Secret", type="password")

    if not client_id or not client_secret:
        st.stop()

    # -------------------------------
    # 🎵 FETCH PLAYLISTS
    # -------------------------------
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        ))

        mood_to_genre = {
            "Happy": "pop",
            "Sad": "acoustic",
            "Neutral": "chill"
        }

        genre = mood_to_genre.get(mood, "chill")
        st.info(f"🎵 Searching Spotify for {genre} playlists...")

        results = sp.search(q=f"playlist {genre}", type="playlist", limit=5)

        # -------------------------------
        # 🧠 SAFE HANDLING OF API RESULTS
        # -------------------------------
        if not results or "playlists" not in results or not results["playlists"]["items"]:
            st.error("❌ No playlists found or Spotify API returned nothing. Check your credentials or try again later.")
            st.stop()

        st.subheader(f"Recommended {genre.capitalize()} Playlists 🎶")

        for playlist in results["playlists"]["items"]:
            name = playlist.get("name", "Unnamed Playlist")
            url = playlist["external_urls"].get("spotify", "#")
            st.markdown(f"**[{name}]({url})**")
            if playlist.get("images"):
                st.image(playlist["images"][0]["url"], width=250)
            st.write("---")

    except Exception as e:
        st.error(f"❌ Spotify API Error: {str(e)}")
        st.info("➡️ Double-check your Spotify Client ID and Secret in Streamlit Secrets or enter them manually above.")
