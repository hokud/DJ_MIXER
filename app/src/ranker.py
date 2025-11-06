from typing import Dict
import pandas as pd
from .theory import camelot_score

def _tempo_match_score(seed_tempo: float, cand_tempo: float, window_pct: float) -> float:
    if seed_tempo <= 0 or cand_tempo <= 0:
        return 0.0
    diff = abs(seed_tempo - cand_tempo)
    limit = seed_tempo * window_pct
    if diff >= limit:
        return 0.0
    return max(0.0, 1.0 - (diff / limit))

def rank_candidates(seed_feat: Dict, df: pd.DataFrame, tempo_window_pct: float = 0.06, weights: Dict[str, int] = None) -> pd.DataFrame:
    weights = weights or dict(tempo=30, key=30, energy=20, dance=10, vibe=10)
    w_sum = sum(weights.values()) or 1

    df = df.copy()
    df["tempo_score"] = df["tempo"].apply(lambda t: _tempo_match_score(seed_feat["tempo"], t, tempo_window_pct))
    df["key_score"] = df["camelot"].apply(lambda c: camelot_score(seed_feat["camelot"], c))
    df["delta_energy"] = df["energy"] - float(seed_feat["energy"])
    df["delta_dance"] = df["danceability"] - float(seed_feat["danceability"])

    df["energy_score"] = 1.0 - (df["delta_energy"].abs())
    df["dance_score"] = 1.0 - (df["delta_dance"].abs())

    for col in ["energy_score", "dance_score"]:
        df[col] = df[col].clip(0, 1)

    df["score"] = (
        weights["tempo"] * df["tempo_score"] +
        weights["key"]   * df["key_score"]   +
        weights["energy"]* df["energy_score"]+
        weights["dance"] * df["dance_score"]
    ) / w_sum

    return df.sort_values("score", ascending=False).reset_index(drop=True)
