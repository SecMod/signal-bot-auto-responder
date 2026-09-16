"""Application entry point."""

from __future__ import annotations

import logging
import sys

from .config import Settings
from .scheduler import Scheduler
from .signal_client import SignalClient
from .storage import Storage


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def load_messages() -> list[str]:
    """Load the latest approved variations from SQLite."""
    storage = Storage()
    messages = storage.get_latest_approved_variations()

    if not messages:
        raise ValueError(
            "No approved message pack found. "
            "Create and save an approved pack in the GUI first."
        )

    return messages


def load_enabled_groups() -> list[dict]:
    """Load enabled Signal groups from SQLite."""
    storage = Storage()
    groups = storage.get_groups(enabled_only=True)

    if not groups:
        raise ValueError(
            "No enabled Signal groups found in the database."
        )

    return groups


def dry_run_send(message: str) -> None:
    """Print the message instead of sending it."""
    logger.info("DRY RUN → %s", message)


def build_sender(settings: Settings):
    """Build the configured message sender."""
    if not settings.signal_enabled:
        logger.info(
            "Signal sending is DISABLED; using dry-run mode."
        )
        return dry_run_send

    if not settings.signal_account:
        raise ValueError(
            "SIGNAL_ACCOUNT is required when SIGNAL_ENABLED=true."
        )

    groups = load_enabled_groups()

    client = SignalClient(account=settings.signal_account)

    def send(message: str) -> None:
        sent = 0

        for group in groups:
            client.send_to_group(
                group["group_id"],
                message,
            )
            sent += 1

        logger.info(
            "Signal message sent successfully to %d groups.",
            sent,
        )

    logger.info(
        "Signal sending is ENABLED for %d database groups.",
        len(groups),
    )

    return send


def main() -> None:
    settings = Settings.from_env()
    messages = load_messages()

    if len(messages) != settings.variation_count:
        raise ValueError(
            f"Expected {settings.variation_count} messages, "
            f"but found {len(messages)}."
        )

    scheduler = Scheduler(
        messages=messages,
        interval_minutes=settings.interval_minutes,
    )

    sender = build_sender(settings)

    logger.info(
        "Loaded %d approved message variations.",
        len(messages),
    )

    logger.info(
        "Cycle: %d hours | Interval: %d minutes",
        settings.cycle_hours,
        settings.interval_minutes,
    )

    scheduler.run_forever(sender)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application stopped by user.")
    except Exception:
        logger.exception("Application failed.")
        sys.exit(1)