from typing import Dict, Any, Optional, List
import pandas as pd
from spotipy import Spotify
from .spotify_client import get_audio_features, get_playlist_tracks
from .theory import to_camelot

def _pack_track_row(track: Dict[str, Any], feat: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": track["id"],
        "title": track["name"],
        "artist": ", ".join(a["name"] for a in track["artists"]),
        "tempo": feat.get("tempo"),
        "key": feat.get("key"),
        "mode": feat.get("mode"),
        "camelot": to_camelot(feat.get("key"), feat.get("mode")),
        "energy": feat.get("energy"),
        "danceability": feat.get("danceability"),
        "valence": feat.get("valence"),
        "loudness": feat.get("loudness"),
        "time_signature": feat.get("time_signature"),
    }

def get_seed_features(sp: Spotify, track_id: str):
    seed = sp.track(track_id)
    feat = sp.audio_features([track_id])[0]
    row = _pack_track_row(seed, feat)
    return seed, row

def _fetch_related_tracks(sp: Spotify, seed_track_id: str) -> List[Dict[str, Any]]:
    seed = sp.track(seed_track_id)
    artist_id = seed["artists"][0]["id"]
    related = sp.artist_related_artists(artist_id)["artists"][:5]
    tracks: List[Dict[str, Any]] = []
    for a in related:
        tracks += sp.artist_top_tracks(a["id"])["tracks"]
    return tracks

def get_candidate_pool_with_features(sp: Spotify, seed_track_id: str, playlist_obj: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    rows = []
    if playlist_obj:
        tracks = get_playlist_tracks(sp, playlist_obj["id"])
    else:
        tracks = _fetch_related_tracks(sp, seed_track_id)

    batch_ids = [t["id"] for t in tracks if t.get("id")]
    for i in range(0, len(batch_ids), 100):
        ids = batch_ids[i:i+100]
        feats = get_audio_features(sp, ids)
        for t, f in zip(tracks[i:i+100], feats):
            if not f:
                continue
            rows.append(_pack_track_row(t, f))

    df = pd.DataFrame(rows).dropna(subset=["tempo", "key", "mode", "energy", "danceability"]).reset_index(drop=True)
    return df
