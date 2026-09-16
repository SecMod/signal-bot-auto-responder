from src.storage import Storage

def test_save_pack(tmp_path):
    db = Storage(str(tmp_path / "test.db"))
    pack_id = db.save_pack("Hello", ["Hello", "Hi"])
    assert pack_id > 0
