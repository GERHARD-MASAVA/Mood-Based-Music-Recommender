import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from textblob import TextBlob

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(page_title="Mood Music Recommender", page_icon="🎵", layout="centered")

# Function to set animated background
def set_animated_bg(colors, speed="10s"):
    gradient_css = f"""
    <style>
    @keyframes gradientAnimation {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .animated-bg {{
        background: linear-gradient(-45deg, {', '.join(colors)});
        background-size: 400% 400%;
        animation: gradientAnimation {speed} ease infinite;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        opacity: 0.85;
    }}
    </style>
    <div class="animated-bg"></div>
    """
    st.markdown(gradient_css, unsafe_allow_html=True)

# -----------------------------
# APP HEADER
# -----------------------------
st.title("🎧 Mood-Based Music Recommender")
st.markdown("Tell me how you feel — and I’ll match your vibe with Spotify playlists 🎶")

user_text = st.text_input("📝 How are you feeling today?")

if user_text:
    blob = TextBlob(user_text)
    polarity = blob.sentiment.polarity

    # Define mood colors & animation
    if polarity > 0.2:
        mood = "Happy"
        colors = ["#FFD54F", "#FF8A65", "#FFB300", "#F06292"]
        speed = "12s"
    elif polarity < -0.2:
        mood = "Sad"
        colors = ["#2196F3", "#3F51B5", "#1A237E", "#3949AB"]
        speed = "20s"
    else:
        mood = "Neutral"
        colors = ["#CFD8DC", "#ECEFF1", "#B0BEC5", "#90A4AE"]
        speed = "15s"

    # Apply background animation
    set_animated_bg(colors, speed)

    st.markdown(
        f"""
        <div style="padding:1rem; border-radius:1rem; background-color:rgba(255,255,255,0.7); text-align:center;">
            <h3>Detected Mood: <b>{mood}</b></h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------
    # SPOTIFY AUTH
    # -----------------------------
    client_id, client_secret = None, None
    try:
        creds = st.secrets["spotify"]
        client_id = creds.get("client_id")
        client_secret = creds.get("client_secret")
    except Exception:
        st.warning("Spotify credentials not found. Enter manually:")
        client_id = st.text_input("Spotify Client ID", type="password")
        client_secret = st.text_input("Spotify Client Secret", type="password")

    if not client_id or not client_secret:
        st.stop()

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

    mood_to_genre = {"Happy": "pop", "Sad": "acoustic", "Neutral": "chill"}
    genre = mood_to_genre.get(mood, "chill")

    st.info(f"🎧 Searching Spotify for '{genre}' playlists...")

    playlists = sp.search(q=f"playlist {genre}", type="playlist", limit=3)

    playlist_data = playlists.get("playlists", {}).get("items", [])
    if not playlist_data:
        st.warning("😕 No playlists found.")
        st.stop()

    for playlist in playlist_data:
        st.subheader(f"🎶 {playlist.get('name', 'Unnamed Playlist')}")
        if playlist.get("images"):
            st.image(playlist["images"][0]["url"], width=300)

        playlist_id = playlist.get("id")
        tracks = sp.playlist_tracks(playlist_id, limit=3)
        for item in tracks["items"]:
            track = item.get("track", {})
            name = track.get("name", "Unknown")
            artists = ", ".join([a["name"] for a in track.get("artists", [])])
            preview_url = track.get("preview_url")

            st.markdown(f"**{name}** — {artists}")
            if preview_url:
                st.audio(preview_url, format="audio/mp3")
            else:
                st.caption("🔇 No preview available.")
        st.write("---")
