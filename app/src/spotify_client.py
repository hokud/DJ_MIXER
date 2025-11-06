import os
import re
from typing import List, Dict, Any, Optional
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

SCOPES = [
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-library-read",
]

def get_spotify_oauth() -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope=" ".join(SCOPES),
        cache_path=".cache",
        open_browser=True,
        show_dialog=False,
    )

def get_spotify(token_info: Dict[str, Any]) -> Spotify:
    return Spotify(auth=token_info["access_token"])

def fetch_user_playlists(sp: Spotify) -> List[Dict[str, Any]]:
    playlists = []
    results = sp.current_user_playlists(limit=50)
    while results:
        playlists.extend(results["items"])
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return playlists

def search_track(sp: Spotify, query: str) -> List[Dict[str, Any]]:
    res = sp.search(q=query, type="track", limit=10)
    return res["tracks"]["items"]

def get_track_id_from_url(url: str) -> Optional[str]:
    m = re.search(r"open\.spotify\.com/track/([a-zA-Z0-9]+)", url)
    return m.group(1) if m else None

def get_audio_features(sp: Spotify, track_ids: List[str]):
    return sp.audio_features(tracks=track_ids)

def get_playlist_tracks(sp: Spotify, playlist_id: str) -> List[Dict[str, Any]]:
    items = []
    results = sp.playlist_items(playlist_id, additional_types=("track",), limit=100)
    while results:
        items.extend(results["items"])
        if results["next"]:
            results = sp.next(results)
        else:
            break
    tracks = [it["track"] for it in items if it.get("track") and it["track"].get("id")]
    return tracks
