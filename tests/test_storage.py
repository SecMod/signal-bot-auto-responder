from src.storage import Storage

def test_pack_crud(tmp_path):
    db = Storage(str(tmp_path / "test.db"))
    pid = db.save_pack("Hello", ["A", "B"])
    assert db.get_pack(pid)["source"] == "Hello"
    assert len(db.list_packs()) == 1
    vid = db.get_pack(pid)["variations"][0]["id"]
    db.set_variation(vid, "Edited", False)
    assert db.get_pack(pid)["variations"][0]["text"] == "Edited"
    db.delete_pack(pid)
    assert db.get_pack(pid) is None

def test_group_crud(tmp_path):
    db = Storage(str(tmp_path / "test.db"))
    db.add_group("Test", "abc")
    assert db.get_groups() == [{"id":1,"name":"Test","group_id":"abc","enabled":True}]
    db.set_group_enabled("abc", False)
    assert db.get_groups(enabled_only=True) == []
    db.remove_group("abc")
    assert db.get_groups() == []

def test_settings_and_logs(tmp_path):
    db = Storage(str(tmp_path / "test.db"))
    db.set_settings({"interval_minutes": 5, "signal_enabled": True})
    assert db.get_setting("interval_minutes") == "5"
    assert db.get_setting("signal_enabled") == "True"
    db.log("info", "hello")
    assert db.get_logs(1)[0]["message"] == "hello"

def test_latest_approved(tmp_path):
    db = Storage(str(tmp_path / "test.db"))
    db.save_pack("Daily", ["A", "B"])
    assert db.get_latest_approved_variations() == ["A", "B"]
