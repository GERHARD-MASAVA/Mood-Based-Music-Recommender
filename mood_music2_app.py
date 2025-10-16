import streamlit as st
from deepface import DeepFace
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from transformers import pipeline
import tempfile

# ------------------------------
# 🎧 APP CONFIG
# ------------------------------
st.set_page_config(page_title="Mood Music Recommender", page_icon="🎵")
st.title("🎧 Mood-Based Music Recommender")

st.markdown("""
Detect your mood and get a playlist that matches your vibe — via camera or text!
""")

# ------------------------------
# 📸 IMAGE CAPTURE / UPLOAD
# ------------------------------
img_file = st.camera_input("Take a selfie or upload your image below 👇")

mood = None  # placeholder

if img_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(img_file.getbuffer())
        img_path = temp_file.name

    with st.spinner("Analyzing your mood... 🧠"):
        try:
            result = DeepFace.analyze(img_path=img_path, actions=['emotion'], enforce_detection=False)
            mood = result[0]['dominant_emotion'].capitalize()
            st.success(f"Detected mood: **{mood}** 😄")
        except Exception as e:
            st.warning(f"DeepFace failed ({e}). Let's try text-based mood detection instead.")

# ------------------------------
# 🪄 FALLBACK: TEXT-BASED MOOD DETECTION
# ------------------------------
if mood is None:
    st.subheader("📝 Tell me how you feel:")
    user_text = st.text_input("Type something like 'I'm feeling great today!' or 'I'm really tired...'")

    if user_text:
        with st.spinner("Analyzing your text mood..."):
            try:
                sentiment_analyzer = pipeline("sentiment-analysis")
                result = sentiment_analyzer(user_text)[0]
                label = result['label']
                if label.lower() == "positive":
                    mood = "Happy"
                elif label.lower() == "negative":
                    mood = "Sad"
                else:
                    mood = "Neutral"
                st.success(f"Detected mood from text: **{mood}** 🧠")
            except Exception as e:
                st.error(f"Text analysis failed: {e}")

# ------------------------------
# 🎵 SPOTIFY PLAYLIST RECOMMENDATION
# ------------------------------
if mood:
    # Load credentials
    SPOTIFY_CLIENT_ID = st.secrets["spotify"]["client_id"]
    SPOTIFY_CLIENT_SECRET = st.secrets["spotify"]["client_secret"]

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))

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

    with st.spinner(f"Fetching {genre} playlists from Spotify..."):
        results = sp.search(q=f"playlist {genre}", type="playlist", limit=5)

    st.subheader(f"Recommended {genre.capitalize()} Playlists 🎶")

    for playlist in results['playlists']['items']:
        st.markdown(f"**[{playlist['name']}]({playlist['external_urls']['spotify']})**")
        if playlist['images']:
            st.image(playlist['images'][0]['url'], width=250)
        st.write("---")
