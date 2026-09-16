from src.variations import generate_variations

def test_count():
    assert len(generate_variations("Hello",24)) == 24

def test_empty():
    import pytest
    with pytest.raises(ValueError):
        generate_variations("",24)
