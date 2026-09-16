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


def test_build_sender_is_preview_when_signal_enabled(tmp_path):
    storage = Storage(str(tmp_path / "test.db"))
    settings = Settings(signal_enabled=True, signal_account="+123")
    sender = build_sender(settings, storage)
    sender("Test")
    logs = storage.get_logs()
    assert any("preview-only" in row["message"].lower() for row in logs)
    assert any("PREVIEW: Test" in row["message"] for row in logs)


def test_preview_sender_uses_storage(tmp_path):
    storage = Storage(str(tmp_path / "test.db"))
    sender = build_preview_sender(storage)
    sender("Hello")
    assert storage.get_logs()[0]["message"] == "PREVIEW: Hello"

# CI verification marker
