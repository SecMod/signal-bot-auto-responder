"""Message scheduler."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Sequence

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(
        self,
        messages: Sequence[str],
        interval_minutes: int = 15,
    ) -> None:
        if not messages:
            raise ValueError("At least one message is required.")

        if interval_minutes <= 0:
            raise ValueError("Interval must be greater than zero.")

        self.messages = list(messages)
        self.interval_seconds = interval_minutes * 60
        self.index = 0
        self.running = False

    def next_message(self) -> str:
        """Return the next message and advance the rotation."""
        message = self.messages[self.index % len(self.messages)]
        self.index += 1
        return message

    def run_forever(self, send: Callable[[str], None]) -> None:
        """Send messages sequentially until the process is stopped."""
        self.running = True

        logger.info(
            "Scheduler started: %d messages, %d-minute interval",
            len(self.messages),
            self.interval_seconds // 60,
        )

        while self.running:
            message = self.next_message()

            try:
                send(message)
                logger.info(
                    "Message processed"
                )
            except Exception:
                logger.exception("Message delivery failed.")

            time.sleep(self.interval_seconds)

    def stop(self) -> None:
        """Request the scheduler to stop."""
        self.running = False
        logger.info("Scheduler stopped.")
