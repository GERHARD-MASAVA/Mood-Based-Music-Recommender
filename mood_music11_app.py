import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from textblob import TextBlob
import base64
import time

# ---------------------------------
# 🎨 PAGE CONFIGURATION
# ---------------------------------
st.set_page_config(page_title="Mood Music Recommender", page_icon="🎵", layout="centered")

st.markdown(
    """
    <style>
    @keyframes pulse-bg {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .mood-box {
        color: white;
        border-radius: 1rem;
        padding: 1.2rem;
        text-align: center;
        animation: pulse-bg 8s ease infinite;
        background-size: 300% 300%;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎧 Mood-Based Music Recommender")
st.markdown("Tell me how you feel — and I’ll find playlists to match your vibe 🎶")

# ---------------------------------
# 💬 USER INPUT
# ---------------------------------
user_text = st.text_input("📝 How are you feeling today?")

if user_text:
    # 🧠 MOOD DETECTION
    blob = TextBlob(user_text)
    polarity = blob.sentiment.polarity

    if polarity > 0.2:
        mood = "Happy"
        gradient = "linear-gradient(270deg, #fce38a, #f38181, #fce38a)"
    elif polarity < -0.2:
        mood = "Sad"
        gradient = "linear-gradient(270deg, #89f7fe, #66a6ff, #89f7fe)"
    else:
        mood = "Neutral"
        gradient = "linear-gradient(270deg, #d3cce3, #e9e4f0, #d3cce3)"

    st.markdown(
        f"""
        <div class="mood-box" style="background:{gradient};">
            <h3>Detected mood: <b>{mood}</b></h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------
    # 🔐 LOAD SPOTIFY CREDENTIALS
    # ---------------------------------
    client_id = None
    client_secret = None

    try:
        if "spotify" in st.secrets:
            creds = st.secrets["spotify"]
            if creds:
                client_id = creds.get("client_id")
                client_secret = creds.get("client_secret")
    except Exception as e:
        st.warning(f"⚠️ Could not load secrets: {e}")

    if not client_id or not client_secret:
        with st.expander("🔑 Enter Spotify Credentials (for testing only)"):
            client_id = st.text_input("Spotify Client ID", type="password")
            client_secret = st.text_input("Spotify Client Secret", type="password")

    if not client_id or not client_secret:
        st.stop()

    # ---------------------------------
    # 🎵 FETCH PLAYLISTS
    # ---------------------------------
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )

        mood_to_genre = {"Happy": "pop", "Sad": "acoustic", "Neutral": "chill"}
        genre = mood_to_genre.get(mood, "chill")

        st.info(f"🎧 Searching Spotify for *{genre}* playlists...")

        playlists = sp.search(q=f"playlist {genre}", type="playlist", limit=3)

        if not playlists or "playlists" not in playlists:
            st.error("❌ Spotify returned an invalid response. Check credentials.")
            st.stop()

        playlist_data = playlists.get("playlists", {}).get("items", [])
        if not playlist_data:
            st.warning("😕 No playlists found for this genre.")
            st.stop()

        # ---------------------------------
        # 🎼 DISPLAY PLAYLISTS
        # ---------------------------------
        for playlist in playlist_data:
            playlist_name = playlist.get("name", "Unnamed Playlist")
            playlist_url = playlist.get("external_urls", {}).get("spotify", "#")
            st.subheader(f"🎶 [{playlist_name}]({playlist_url})")

            image_url = playlist.get("images", [{}])[0].get("url", None)
            if image_url:
                st.image(image_url, width=280)

            playlist_id = playlist.get("id")
            if not playlist_id:
                continue

            tracks = sp.playlist_tracks(playlist_id, limit=3)
            if not tracks or "items" not in tracks:
                continue

            for item in tracks["items"]:
                track = item.get("track")
                if not track:
                    continue

                track_name = track.get("name", "Unknown Track")
                artists = ", ".join([a["name"] for a in track.get("artists", [])])
                preview_url = track.get("preview_url")

                st.markdown(f"**{track_name}** — {artists}")
                if preview_url:
                    st.audio(preview_url, format="audio/mp3")
                else:
                    st.caption("🔇 No preview available.")
            st.write("---")

    except spotipy.SpotifyException as e:
        st.error("🚨 Spotify authentication failed.")
        st.code(str(e))
    except Exception as e:
        st.error("❌ Unexpected error occurred.")
        st.code(str(e))
