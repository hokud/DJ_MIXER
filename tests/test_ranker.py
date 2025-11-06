import pandas as pd
from src.ranker import rank_candidates

def test_rank_sorting_basic():
    seed = dict(tempo=120.0, camelot="8A", energy=0.5, danceability=0.7)
    df = pd.DataFrame([
        dict(id="1", title="A", artist="X", tempo=120.0, camelot="8A", energy=0.5, danceability=0.7),
        dict(id="2", title="B", artist="Y", tempo=128.0, camelot="2B", energy=0.9, danceability=0.5),
    ])
    out = rank_candidates(seed, df)
    assert out.iloc[0]["id"] == "1"
