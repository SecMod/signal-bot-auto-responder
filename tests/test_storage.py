from src.storage import Storage


def test_save_pack(tmp_path):
    db = Storage(str(tmp_path / "test.db"))

    pack_id = db.save_pack(
        "Hello",
        ["Hello", "Hi"],
    )

    assert pack_id > 0


def test_get_latest_approved_variations(tmp_path):
    db = Storage(str(tmp_path / "test.db"))

    db.save_pack(
        "Daily update",
        ["Message 1", "Message 2", "Message 3"],
    )

    result = db.get_latest_approved_variations()

    assert result == [
        "Message 1",
        "Message 2",
        "Message 3",
    ]