from src.daily_content import generate_variations
from src.storage import Storage
from src.scheduler import Scheduler

def test_variations():
    assert len(generate_variations("Hello", 24)) == 24

def test_pack_crud(tmp_path):
    s=Storage(str(tmp_path/"x.db"))
    p=s.save_pack("Hello",["a","b"])
    assert s.get_pack(p)["variations"][0]["text"]=="a"
    s.delete_pack(p)
    assert s.get_pack(p) is None

def test_groups(tmp_path):
    s=Storage(str(tmp_path/"x.db"))
    s.add_group("G","id")
    assert s.get_groups()[0]["group_id"]=="id"
    s.set_group_enabled("id",False)
    assert not s.get_groups(enabled_only=True)
    s.remove_group("id")
    assert not s.get_groups()

def test_settings_and_logs(tmp_path):
    s=Storage(str(tmp_path/"x.db"))
    s.set_settings({"interval_minutes":3})
    assert s.get_setting("interval_minutes")=="3"
    s.log("info","hello")
    assert s.get_logs()[0]["message"]=="hello"

def test_scheduler_rotation():
    s=Scheduler(["a","b"],1,1)
    assert [s.next_message() for _ in range(3)]==["a","b","a"]

def test_scheduler_rejects_invalid_values():
    import pytest
    with pytest.raises(ValueError): Scheduler(["a"],0,1)
    with pytest.raises(ValueError): Scheduler(["a"],1,0)
