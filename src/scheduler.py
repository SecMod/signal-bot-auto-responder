from __future__ import annotations

import math
import threading
from datetime import datetime
from collections.abc import Callable, Sequence


class Scheduler:
    def __init__(
        self,
        messages: Sequence[str],
        interval_minutes: int = 15,
        cycle_hours: int = 6,
        on_state_change: Callable[[str], None] | None = None,
        on_post: Callable[[bool, str | None], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ):
        if not messages:
            raise ValueError("At least one message is required.")
        if interval_minutes <= 0 or cycle_hours <= 0:
            raise ValueError("Interval and cycle must be greater than zero.")
        self.messages = list(messages)
        self.interval_minutes = interval_minutes
        self.cycle_hours = cycle_hours
        self.index = 0
        self.running = False
        self.started_at: datetime | None = None
        self.last_post_at: datetime | None = None
        self.next_post_at: datetime | None = None
        self.posts_today = 0
        self.skipped = 0
        self.last_error: str | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()
        self.on_state_change = on_state_change
        self.on_post = on_post
        self.on_error = on_error

    @property
    def max_messages_per_cycle(self) -> int:
        """Legacy capacity calculation retained for compatibility.

        The 24/7 scheduler no longer stops at this value; it runs until STOP.
        """
        return max(1, math.ceil((self.cycle_hours * 60) / self.interval_minutes))

    def next_message(self) -> str:
        with self._lock:
            message = self.messages[self.index % len(self.messages)]
            self.index += 1
            return message

    def _notify_state(self, state: str) -> None:
        callback = self.on_state_change
        if callback:
            try:
                callback(state)
            except Exception:
                pass

    def start(self, process: Callable[[str], None]) -> bool:
        with self._lock:
            if self.running:
                return False
            self.running = True
            self.started_at = datetime.now()
            self.last_error = None
            self.next_post_at = datetime.now()
            self._stop.clear()

        def worker():
            self._notify_state("online")
            try:
                while not self._stop.is_set():
                    message = self.next_message()
                    try:
                        process(message)
                        with self._lock:
                            self.posts_today += 1
                            self.last_post_at = datetime.now()
                            self.last_error = None
                    except Exception as exc:
                        with self._lock:
                            self.last_error = str(exc)
                        if self.on_error:
                            try:
                                self.on_error(exc)
                            except Exception:
                                pass
                    if self.on_post:
                        try:
                            self.on_post(self.last_error is None, self.last_error)
                        except Exception:
                            pass

                    if self._stop.is_set():
                        break

                    with self._lock:
                        self.next_post_at = datetime.now()
                    self.next_post_at = datetime.now()
                    if self._stop.wait(self.interval_minutes * 60):
                        break
            finally:
                with self._lock:
                    self.running = False
                    self.next_post_at = None
                self._notify_state("offline")

        self._thread = threading.Thread(
            target=worker,
            daemon=True,
            name="scheduler",
        )
        self._thread.start()
        return True

    def stop(self):
        self._stop.set()
        with self._lock:
            self.running = False
            self.next_post_at = None
        self._notify_state("offline")

    def update(
        self,
        messages: Sequence[str],
        interval_minutes: int,
        cycle_hours: int,
    ):
        if self.running:
            raise RuntimeError("Stop the scheduler before changing scheduler settings.")
        if not messages:
            raise ValueError("At least one message is required.")
        if interval_minutes <= 0 or cycle_hours <= 0:
            raise ValueError("Interval and cycle must be greater than zero.")
        self.messages = list(messages)
        self.interval_minutes = interval_minutes
        self.cycle_hours = cycle_hours
        self.index = 0
