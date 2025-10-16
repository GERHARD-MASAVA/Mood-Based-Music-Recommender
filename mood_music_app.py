import streamlit as st
from deepface import DeepFace
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import tempfile

# ------------------------------
# 🎧 APP TITLE
# ------------------------------
st.set_page_config(page_title="Mood Music Recommender", page_icon="🎵")
st.title("🎧 Mood-Based Music Recommender")

st.markdown("""
Upload your photo or take a selfie — and get a playlist that matches your mood!
""")

# ------------------------------
# 📸 IMAGE CAPTURE / UPLOAD
# ------------------------------
img_file = st.camera_input("Take a selfie or upload your image below 👇")

if img_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(img_file.getbuffer())
        img_path = temp_file.name

    # ------------------------------
    # 🧠 EMOTION ANALYSIS (DeepFace)
    # ------------------------------
    with st.spinner("Analyzing your mood... 🧠"):
        try:
            result = DeepFace.analyze(img_path=img_path, actions=['emotion'], enforce_detection=False)
            mood = result[0]['dominant_emotion'].capitalize()
            st.success(f"Detected mood: **{mood}** 😄")
        except Exception as e:
            st.error(f"Could not analyze emotion: {e}")
            st.stop()

    # ------------------------------
    # 🎵 SPOTIFY API SETUP
    # ------------------------------
    # 👉 Replace with your actual credentials from https://developer.spotify.com/dashboard/
    SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
    SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"

    if SPOTIFY_CLIENT_ID == "YOUR_SPOTIFY_CLIENT_ID":
        st.warning("⚠️ Please set your Spotify API credentials first to get playlists.")
    else:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))

        # ------------------------------
        # 🗺️ MOOD TO GENRE MAPPING
        # ------------------------------
        mood_to_genre = {
            "Happy": "pop",
            "Sad": "acoustic",
            "Angry": "rock",
            "Surprise": "dance",
            "Fear": "ambient",
            "Neutral": "chill",
            "Disgust": "metal"
        }

        genre = mood_to_genre.get(mood, "chill")

        # ------------------------------
        # 🔍 SEARCH SPOTIFY PLAYLISTS
        # ------------------------------
        with st.spinner(f"Fetching {genre} playlists from Spotify..."):
            results = sp.search(q=f"playlist {genre}", type="playlist", limit=5)

        st.subheader(f"Recommended {genre.capitalize()} Playlists 🎶")

        for playlist in results['playlists']['items']:
            st.markdown(f"**[{playlist['name']}]({playlist['external_urls']['spotify']})**")
            if playlist['images']:
                st.image(playlist['images'][0]['url'], width=250)
            st.write("---")
