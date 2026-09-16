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
        signal_group_ids=("group-test",),
    )

    try:
        build_sender(settings)
    except ValueError as exc:
        assert "SIGNAL_ACCOUNT" in str(exc)
        return

    assert False


def test_build_sender_requires_group_when_enabled():
    settings = Settings(
        signal_enabled=True,
        signal_account="+123456789",
        signal_group_ids=(),
    )

    try:
        build_sender(settings)
    except ValueError as exc:
        assert "SIGNAL_GROUP_IDS" in str(exc)
        return

    assert False