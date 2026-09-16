from src.config import Settings
from src.main import build_sender, dry_run_send


def test_build_sender_uses_dry_run_when_signal_disabled():
    settings = Settings(
        signal_enabled=False,
    )

    sender = build_sender(settings)

    assert sender is dry_run_send


def test_build_sender_requires_account_when_enabled():
    settings = Settings(
        signal_enabled=True,
        signal_account="",
    )

    try:
        build_sender(settings)
    except ValueError as exc:
        assert "SIGNAL_ACCOUNT" in str(exc)
        return

    assert False


def test_build_sender_uses_enabled_database_groups_when_enabled(
    monkeypatch,
):
    class FakeStorage:
        def get_groups(self, enabled_only=False):
            assert enabled_only is True
            return [
                {
                    "id": 1,
                    "name": "Test Group",
                    "group_id": "group-test-001",
                    "enabled": True,
                }
            ]

    monkeypatch.setattr(
        "src.main.Storage",
        FakeStorage,
    )

    class FakeSignalClient:
        def __init__(self, account):
            self.account = account
            self.sent = []

        def send_to_group(self, group_id, message):
            self.sent.append((group_id, message))

    fake_client = FakeSignalClient("+123456789")

    monkeypatch.setattr(
        "src.main.SignalClient",
        lambda account: fake_client,
    )

    settings = Settings(
        signal_enabled=True,
        signal_account="+123456789",
    )

    sender = build_sender(settings)
    sender("Test message")

    assert fake_client.sent == [
        ("group-test-001", "Test message"),
    ]


def test_build_sender_fails_when_no_enabled_database_groups(
    monkeypatch,
):
    class FakeStorage:
        def get_groups(self, enabled_only=False):
            assert enabled_only is True
            return []

    monkeypatch.setattr(
        "src.main.Storage",
        FakeStorage,
    )

    settings = Settings(
        signal_enabled=True,
        signal_account="+123456789",
    )

    sender = build_sender(settings)

    try:
        sender("Test message")
    except ValueError as exc:
        assert "No enabled Signal groups" in str(exc)
        return

    assert False