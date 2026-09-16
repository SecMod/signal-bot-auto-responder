from __future__ import annotations

from .config import Settings
from .storage import Storage


def dry_run_send(message: str) -> None:
    """Process a message without transmitting it."""
    print(f"DRY RUN: {message}")


def build_preview_sender(storage: Storage | None = None):
    """Return the scheduler callback used by the safe preview mode."""
    storage = storage or Storage()

    def process(message: str) -> None:
        storage.log("INFO", f"PREVIEW: {message}")

    return process


def build_sender(settings: Settings, storage: Storage | None = None):
    """Build preview or explicitly enabled delivery to configured authorized groups."""
    storage = storage or Storage()
    if not settings.signal_enabled:
        return build_preview_sender(storage)
    if not settings.signal_account:
        raise ValueError("Signal account is required when Signal is enabled.")
    from .signal_client import SignalClient
    client = SignalClient(account=settings.signal_account, signal_cli=settings.signal_cli_path or "signal-cli")

    def process(message: str) -> None:
        groups = storage.get_groups(enabled_only=True)
        if not groups:
            raise ValueError("No enabled authorized Signal groups configured.")
        sent = 0
        for group in groups:
            client.send_to_group(group["group_id"], message)
            sent += 1
        storage.log("INFO", f"REAL: sent approved message to {sent} authorized group(s).")

    storage.log("INFO", "Signal real delivery enabled for configured authorized groups.")
    return process


def main() -> None:
    """Start the local scheduler from persisted settings."""
    from .scheduler import Scheduler

    storage = Storage()
    settings = Settings(
        interval_minutes=int(storage.get_setting("interval_minutes", 15)),
        variation_count=int(storage.get_setting("variation_count", 24)),
        cycle_hours=int(storage.get_setting("cycle_hours", 6)),
        signal_account=str(storage.get_setting("signal_account", "")),
        signal_enabled=str(storage.get_setting("signal_enabled", "False")).lower() == "true",
        signal_cli_path=str(storage.get_setting("signal_cli_path", "")),
    )
    messages = storage.get_latest_approved_variations()
    if len(messages) != settings.variation_count:
        raise ValueError(
            f"Expected {settings.variation_count} approved variations, got {len(messages)}."
        )
    scheduler = Scheduler(messages, settings.interval_minutes, settings.cycle_hours)
    scheduler.start(build_sender(settings, storage))
    return None


if __name__ == "__main__":
    main()
