import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from textblob import TextBlob

st.set_page_config(page_title="Mood Music Recommender", page_icon="🎵", layout="centered")
st.title("🎧 Mood-Based Music Recommender")

st.markdown("Tell me how you feel — and I’ll match your vibe with Spotify playlists 🎶")

# -------------------------------------------
# 💬 USER INPUT
# -------------------------------------------
user_text = st.text_input("📝 How are you feeling today?")

if user_text:
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

    # -------------------------------------------
    # 🔐 LOAD SPOTIFY CREDENTIALS
    # -------------------------------------------
    client_id = None
    client_secret = None

    if "spotify" in st.secrets:
        client_id = st.secrets["spotify"].get("client_id")
        client_secret = st.secrets["spotify"].get("client_secret")

    if not client_id or not client_secret:
        st.warning("⚠️ Spotify credentials not found in secrets. Enter them manually for testing:")
        client_id = st.text_input("Spotify Client ID", type="password")
        client_secret = st.text_input("Spotify Client Secret", type="password")

    if not client_id or not client_secret:
        st.stop()

    # -------------------------------------------
    # 🎵 FETCH PLAYLISTS SAFELY
    # -------------------------------------------
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id, client_secret=client_secret
            )
        )

        mood_to_genre = {"Happy": "pop", "Sad": "acoustic", "Neutral": "chill"}
        genre = mood_to_genre.get(mood, "chill")

        st.info(f"🎧 Searching Spotify for **{genre}** playlists...")

        playlists = sp.search(q=f"playlist {genre}", type="playlist", limit=3)

        # ✅ Safe dictionary checking
        if not playlists or not isinstance(playlists, dict):
            st.error("❌ Spotify API returned no data.")
            st.json(playlists)
            st.stop()

        if "playlists" not in playlists or "items" not in playlists["playlists"]:
            st.error("⚠️ Unexpected Spotify API format.")
            st.json(playlists)
            st.stop()

        # ✅ Display playlists
        for playlist in playlists["playlists"]["items"]:
            st.subheader(f"🎶 {playlist.get('name', 'Unnamed Playlist')}")
            if playlist.get("images"):
                st.image(playlist["images"][0]["url"], width=300)

            playlist_id = playlist.get("id")
            if not playlist_id:
                continue

            tracks = sp.playlist_tracks(playlist_id, limit=3)
            if not tracks or "items" not in tracks:
                st.caption("No tracks found in this playlist.")
                continue

            for item in tracks["items"]:
                track = item.get("track", {})
                name = track.get("name", "Unknown Track")
                artists = ", ".join([a["name"] for a in track.get("artists", [])])
                preview_url = track.get("preview_url")

                st.markdown(f"**{name}** — {artists}")
                if preview_url:
                    st.audio(preview_url, format="audio/mp3")
                else:
                    st.caption("🔇 No audio preview available.")
            st.write("---")

    except spotipy.SpotifyException as e:
        st.error("🚨 Spotify authentication failed.")
        st.code(str(e))
        st.info("➡️ Double-check your client ID and secret in Streamlit Secrets.")
    except Exception as e:
        st.error("❌ Unexpected error.")
        st.code(str(e))
