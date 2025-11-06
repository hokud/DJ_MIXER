from src.theory import to_camelot, camelot_score

def test_camelot_map_examples():
    assert to_camelot(9, 0) == "8A"   # A minor
    assert to_camelot(9, 1) == "11B"  # A major

def test_camelot_score():
    assert camelot_score("8A", "8A") == 1.0
    assert camelot_score("8A", "9A") == 0.8   # adjacent
    assert camelot_score("8A", "8B") == 0.6   # relative
    assert camelot_score("8A", "2B") == 0.0
