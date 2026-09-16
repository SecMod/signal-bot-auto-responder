from __future__ import annotations

import threading
from collections.abc import Callable, Sequence

class Scheduler:
    def __init__(self, messages: Sequence[str], interval_minutes: int = 15, cycle_hours: int = 6):
        if not messages:
            raise ValueError("At least one message is required.")
        if interval_minutes <= 0 or cycle_hours <= 0:
            raise ValueError("Interval and cycle must be greater than zero.")
        self.messages = list(messages)
        self.interval_minutes = interval_minutes
        self.cycle_hours = cycle_hours
        self.index = 0
        self.running = False
        self._stop = threading.Event()

    def next_message(self) -> str:
        message = self.messages[self.index % len(self.messages)]
        self.index += 1
        return message

    def start(self, process: Callable[[str], None]) -> bool:
        if self.running:
            return False
        self.running = True
        self._stop.clear()

        def worker():
            try:
                while not self._stop.is_set():
                    process(self.next_message())
                    if self._stop.wait(self.interval_minutes * 60):
                        break
            finally:
                self.running = False

        threading.Thread(target=worker, daemon=True, name="scheduler").start()
        return True

    def stop(self):
        self._stop.set()
        self.running = False

    def update(self, messages: Sequence[str], interval_minutes: int, cycle_hours: int):
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
