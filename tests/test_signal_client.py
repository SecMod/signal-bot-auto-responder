import json
from src.signal_client import SignalClient

def test_parse_groups(monkeypatch):
    raw=json.dumps([
        {"id":"gid1","name":"Alpha"},
        {"id":"gid2","name":"Beta"},
        {"name":"No ID"}
    ])
    monkeypatch.setattr(SignalClient,"_run",lambda self,*args: raw)
    groups=SignalClient("+10000000000").list_groups()
    assert groups == [{"name":"Alpha","group_id":"gid1"},{"name":"Beta","group_id":"gid2"}]

def test_bad_json(monkeypatch):
    monkeypatch.setattr(SignalClient,"_run",lambda self,*args: "nope")
    import pytest
    with pytest.raises(RuntimeError):
        SignalClient("+1").list_groups()
