import json
import subprocess
import pytest

from src.signal_client import SignalClient

def test_parse_groups(monkeypatch):
    raw=json.dumps([
        {"id":"gid1","name":"Alpha"},
        {"id":"gid2","name":"Beta"},
        {"name":"No ID"}
    ])
    monkeypatch.setattr(SignalClient,"_run",lambda self,*args: raw)
    assert SignalClient("+10000000000").list_groups() == [
        {"name":"Alpha","group_id":"gid1"},
        {"name":"Beta","group_id":"gid2"},
    ]

def test_bad_json(monkeypatch):
    monkeypatch.setattr(SignalClient,"_run",lambda self,*args: "nope")
    with pytest.raises(RuntimeError):
        SignalClient("+1").list_groups()

def test_send_command(monkeypatch):
    calls=[]
    class Result:
        returncode=0
        stdout=""
        stderr=""
    def fake_run(command, **kwargs):
        calls.append(command)
        return Result()
    monkeypatch.setattr(subprocess,"run",fake_run)
    SignalClient("+123","signal-cli")._run("send","-g","gid","-m","hello")
    assert calls == [["signal-cli","-a","+123","send","-g","gid","-m","hello"]]


def test_extract_link_uri():
    output = "Ready\n" + "sgnl://linkdevice?" + "uuid=abc12345&pub_key=xyz12345" + "\n"
    assert SignalClient.extract_link_uri(output).rstrip("\\n") == "sgnl://linkdevice?uuid=abc12345&pub_key=xyz12345"
