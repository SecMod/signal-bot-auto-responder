from src.config import Settings
from src.main import build_sender, build_preview_sender, dry_run_send
from src.storage import Storage


def test_dry_run_send(capsys):
    dry_run_send("Test message")
    assert "DRY RUN: Test message" in capsys.readouterr().out


def test_build_sender_is_preview_when_signal_disabled(tmp_path):
    storage = Storage(str(tmp_path / "test.db"))
    sender = build_sender(Settings(signal_enabled=False), storage)
    assert callable(sender)
    sender("Test")
    assert "PREVIEW: Test" in storage.get_logs()[0]["message"]


def test_build_sender_real_send(monkeypatch, tmp_path):
    storage = Storage(str(tmp_path / "test.db"))
    storage.add_group("Authorized", "gid-1", enabled=True)
    settings = Settings(signal_enabled=True, signal_account="+123")
    sent = []

    class FakeClient:
        def __init__(self, account, signal_cli="signal-cli"):
            assert account == "+123"
            self.signal_cli = signal_cli

        def send_to_group(self, group_id, message):
            sent.append((group_id, message))

    import src.signal_client
    monkeypatch.setattr(src.signal_client, "SignalClient", FakeClient)
    sender = build_sender(settings, storage)
    sender("Test")
    assert sent == [("gid-1", "Test")]
    assert "REAL: sent approved message to 1 authorized group(s)." in storage.get_logs()[0]["message"]


def test_build_sender_rejects_real_without_groups(tmp_path):
    storage = Storage(str(tmp_path / "test.db"))
    settings = Settings(signal_enabled=True, signal_account="+123")
    sender = build_sender(settings, storage)
    import pytest
    with pytest.raises(ValueError, match="No enabled authorized Signal groups"):
        sender("Test")


def test_preview_sender_uses_storage(tmp_path):
    storage = Storage(str(tmp_path / "test.db"))
    sender = build_preview_sender(storage)
    sender("Hello")
    assert storage.get_logs()[0]["message"] == "PREVIEW: Hello"
