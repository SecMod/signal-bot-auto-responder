from __future__ import annotations
import logging
import time
from collections.abc import Callable, Sequence

log = logging.getLogger(__name__)

def run_forever(messages: Sequence[str], interval_seconds: int,
                send: Callable[[str], None]) -> None:
    if not messages:
        raise ValueError("No messages configured")
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")
    i = 0
    while True:
        try:
            send(messages[i % len(messages)])
        except Exception:
            log.exception("Delivery failed")
        i += 1
        time.sleep(interval_seconds)
