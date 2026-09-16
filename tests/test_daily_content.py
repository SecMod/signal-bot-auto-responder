from src.daily_content import build_pack

def test_pack():
    p = build_pack("Daily update", 24)
    assert p.source == "Daily update"
    assert len(p.variations) == 24
