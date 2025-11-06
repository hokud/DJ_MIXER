import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from src.spotify_client import (
    get_spotify_oauth, get_spotify,
    fetch_user_playlists, search_track, get_track_id_from_url
)
from src.features import get_seed_features, get_candidate_pool_with_features
from src.ranker import rank_candidates
from src.explain import explain_transition

load_dotenv()
st.set_page_config(page_title="DJ Next Track Assistant", page_icon="🎧", layout="wide")
st.title("DJ Next Track Assistant 🎧")
st.caption("BPM + key + energy + dance → next-track suggestions with explainable reasons")

# --- OAuth ---
oauth = get_spotify_oauth()
params = st.query_params     
code = params.get("code")

if "token_info" not in st.session_state:
    st.session_state.token_info = None

if st.session_state.token_info is None:
    auth_url = oauth.get_authorize_url()
    with st.expander("Connect your Spotify account", expanded=True):
        st.write("Click the button below to login with Spotify. After login, you'll return here.")
        st.link_button("Login with Spotify", auth_url, type="primary")

    if code:
        token_info = oauth.get_access_token(code, check_cache=False)
        st.session_state.token_info = token_info
        st.query_params # clear code from URL
        st.rerun()

if st.session_state.token_info:
    sp = get_spotify(st.session_state.token_info)

    # Sidebar controls
    st.sidebar.header("Source & Settings")
    playlists = fetch_user_playlists(sp)
    playlist_names = [f"{p['name']} ({p['tracks']['total']})" for p in playlists]
    playlist_choice = st.sidebar.selectbox(
        "Candidate pool (playlist)",
        options=["— search only —"] + playlist_names,
        index=0
    )

    default_tempo_pct = int(float(os.getenv("TEMPO_WINDOW_PCT", 0.06)) * 100)
    tempo_window = st.sidebar.slider("Tempo window (%)", 1, 15, default_tempo_pct)
    w1 = st.sidebar.slider("Weight: Tempo", 0, 100, 30)
    w2 = st.sidebar.slider("Weight: Key", 0, 100, 30)
    w3 = st.sidebar.slider("Weight: Energy", 0, 100, 20)
    w4 = st.sidebar.slider("Weight: Danceability", 0, 100, 10)
    w5 = st.sidebar.slider("Weight: Vibe (reserved)", 0, 100, 10)

    st.divider()
    st.subheader("Choose a seed track")
    seed_query = st.text_input("Search a track or paste a Spotify track URL")
    results = []
    seed_track_id = None

    if seed_query:
        if seed_query.startswith("https://open.spotify.com/track/"):
            seed_track_id = get_track_id_from_url(seed_query)
        else:
            results = search_track(sp, seed_query)

    if results:
        labels = [f"{r['name']} – {', '.join(a['name'] for a in r['artists'])}" for r in results]
        pick_idx = st.selectbox("Pick one", list(range(len(results))), format_func=lambda i: labels[i])
        seed_track_id = results[pick_idx]["id"]

    go = st.button("Suggest next tracks", type="primary")

    if go and seed_track_id:
        seed_meta, seed_feat = get_seed_features(sp, seed_track_id)

        with st.expander("Seed track features", expanded=True):
            st.write({
                "track": f"{seed_meta['name']} – {', '.join(a['name'] for a in seed_meta['artists'])}",
                "bpm": round(seed_feat["tempo"], 1),
                "key": seed_feat["camelot"],
                "energy": round(seed_feat["energy"], 2),
                "danceability": round(seed_feat["danceability"], 2),
            })

        playlist_obj = None
        if playlist_choice != "— search only —":
            playlist_obj = playlists[playlist_names.index(playlist_choice)]

        df = get_candidate_pool_with_features(sp, seed_track_id, playlist_obj)

        if df.empty:
            st.warning("No candidates found. Try a different playlist or search.")
        else:
            ranked = rank_candidates(
                seed_feat, df,
                tempo_window_pct=tempo_window / 100.0,
                weights=dict(tempo=w1, key=w2, energy=w3, dance=w4, vibe=w5)
            )
            top3 = ranked.head(3).copy()

            for _, row in top3.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['title']} – {row['artist']}**")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.write(f"BPM: {round(row['tempo'],1)}")
                    c2.write(f"Key: {row['camelot']}")
                    c3.write(f"Δenergy: {row['delta_energy']:+.2f}")
                    c4.write(f"Δdance: {row['delta_dance']:+.2f}")

                    if st.toggle("Show AI rationale", value=True, key=row["id"]):
                        text = explain_transition(seed_meta, seed_feat, row.to_dict())
                        st.caption(text)
else:
    st.info("Add your Spotify keys in .env, set the redirect URI in Spotify Dashboard, then run the app.")
