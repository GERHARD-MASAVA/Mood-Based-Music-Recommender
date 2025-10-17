import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from textblob import TextBlob
import json

# ---------------------------------
# 🎨 PAGE CONFIGURATION
# ---------------------------------
st.set_page_config(page_title="Mood Music Recommender", page_icon="🎵", layout="centered")

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
        bg_color = "#FFF4B2"
    elif polarity < -0.2:
        mood = "Sad"
        bg_color = "#B2D0FF"
    else:
        mood = "Neutral"
        bg_color = "#E0E0E0"

    st.markdown(
        f"""
        <div style="background-color:{bg_color}; padding:1rem; border-radius:1rem;">
            <h4>Detected mood: <b>{mood}</b></h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------
    # 🔐 LOAD SPOTIFY CREDENTIALS SAFELY
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
        st.warning("⚠️ Spotify credentials not found in secrets. Enter them manually for testing:")
        client_id = st.text_input("Spotify Client ID", type="password")
        client_secret = st.text_input("Spotify Client Secret", type="password")

    if not client_id or not client_secret:
        st.stop()

    # ---------------------------------
    # 🎵 FETCH PLAYLISTS (DEBUG-SAFE)
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

        st.info(f"🎧 Searching Spotify for '{genre}' playlists...")

        playlists = sp.search(q=f"playlist {genre}", type="playlist", limit=3)

        # ✅ DEBUG PRINT if playlists is None
        if playlists is None:
            st.error("❌ Spotify returned None — check credentials or API access.")
            st.stop()

        if not isinstance(playlists, dict):
            st.error("⚠️ Unexpected response from Spotify API:")
            st.json(playlists)
            st.stop()

        playlist_data = playlists.get("playlists", {}).get("items", [])
        if not playlist_data:
            st.warning("😕 No playlists found for this genre.")
            st.json(playlists)
            st.stop()

        # ---------------------------------
        # 🎼 DISPLAY PLAYLISTS AND TRACKS
        # ---------------------------------
        for playlist in playlist_data:
            if not playlist:
                continue

            playlist_name = playlist.get("name", "Unnamed Playlist")
            st.subheader(f"🎶 {playlist_name}")

            images = playlist.get("images", [])
            if images and len(images) > 0 and images[0].get("url"):
                st.image(images[0]["url"], width=300)

            playlist_id = playlist.get("id")
            if not playlist_id:
                st.caption("⚠️ Missing playlist ID — skipping.")
                continue

            tracks = sp.playlist_tracks(playlist_id, limit=3)
            if not tracks or "items" not in tracks:
                st.caption("No tracks found in this playlist.")
                continue

            for item in tracks["items"]:
                track = item.get("track") if item else None
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
