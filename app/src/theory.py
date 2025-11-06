from typing import Optional

# Spotify key: 0=C, 1=C#, 2=D, 3=Eb, 4=E, 5=F, 6=F#, 7=G, 8=Ab, 9=A, 10=Bb, 11=B
# mode: 0=minor, 1=major
_CAM_NOTATION = {
    (0,1): "8B", (0,0): "5A",
    (1,1): "3B", (1,0): "12A",
    (2,1): "10B", (2,0): "7A",
    (3,1): "5B", (3,0): "2A",
    (4,1): "12B", (4,0): "9A",
    (5,1): "7B", (5,0): "4A",
    (6,1): "2B", (6,0): "11A",
    (7,1): "9B", (7,0): "6A",
    (8,1): "4B", (8,0): "1A",
    (9,1): "11B", (9,0): "8A",
    (10,1): "6B", (10,0): "3A",
    (11,1): "1B", (11,0): "10A",
}

def to_camelot(key: Optional[int], mode: Optional[int]) -> str:
    if key is None or mode is None:
        return "?"
    return _CAM_NOTATION.get((int(key), int(mode)), "?")

def camelot_score(a: str, b: str) -> float:
    """Compatibility score in [0,1]: exact (1.0), adjacent ring (0.8), relative maj/min (0.6), else 0."""
    if a == "?" or b == "?":
        return 0.0
    if a == b:
        return 1.0
    try:
        n_a, L_a = int(a[:-1]), a[-1]
        n_b, L_b = int(b[:-1]), b[-1]
    except Exception:
        return 0.0
    # adjacent number same ring (with wrap 12 <-> 1)
    if L_a == L_b and (abs(n_a - n_b) == 1 or {n_a, n_b} == {1, 12}):
        return 0.8
    # relative major/minor
    if n_a == n_b and L_a != L_b:
        return 0.6
    return 0.0
