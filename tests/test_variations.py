from src.variations import generate_variations

def test_count():
    assert len(generate_variations("Hello", 24)) == 24

def test_empty():
    try:
        generate_variations("", 24)
    except ValueError:
        return
    assert False
