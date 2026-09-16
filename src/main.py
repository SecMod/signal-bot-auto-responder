"""Application entry point."""

from __future__ import annotations

import logging
import os

from .config import Settings
from .scheduler import Scheduler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def load_messages() -> list[str]:
    """Load today's approved variations from data/messages.txt."""
    path = os.getenv("MESSAGES_FILE", "data/messages.txt")

    with open(path, "r", encoding="utf-8") as file:
        messages = [
            line.strip()
            for line in file
            if line.strip()
        ]

    return messages


def dry_run_send(message: str) -> None:
    """Print the message instead of sending it."""
    logger.info("DRY RUN → %s", message)


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

    logger.info("Loaded %d message variations.", len(messages))
    logger.info(
        "Cycle: %d hours | Interval: %d minutes",
        settings.cycle_hours,
        settings.interval_minutes,
    )

    scheduler.run_forever(dry_run_send)


if __name__ == "__main__":
    main()
