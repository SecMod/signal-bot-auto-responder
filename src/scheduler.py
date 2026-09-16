from __future__ import annotations
import threading
import logging
from collections.abc import Callable, Sequence

logger=logging.getLogger(__name__)

class Scheduler:
    def __init__(self,messages:Sequence[str],interval_minutes:int=15,cycle_hours:int=6):
        if not messages: raise ValueError("At least one message is required.")
        if interval_minutes<=0 or cycle_hours<=0: raise ValueError("Interval and cycle must be greater than zero.")
        self.messages=list(messages); self.interval_minutes=interval_minutes; self.cycle_hours=cycle_hours
        self.index=0; self.running=False; self._stop=threading.Event()
    def next_message(self):
        m=self.messages[self.index%len(self.messages)]; self.index+=1; return m
    def start(self,process:Callable[[str],None]):
        if self.running:return False
        self.running=True; self._stop.clear()
        def worker():
            logger.info("Scheduler started: %d messages, %d min interval, %d h cycle",len(self.messages),self.interval_minutes,self.cycle_hours)
            while not self._stop.is_set():
                try: process(self.next_message())
                except Exception: logger.exception("Scheduled message processing failed")
                if self._stop.wait(self.interval_minutes*60): break
            self.running=False; logger.info("Scheduler stopped")
        threading.Thread(target=worker,daemon=True,name="scheduler").start(); return True
    def stop(self):
        self._stop.set(); self.running=False
    def update(self,messages,interval_minutes,cycle_hours):
        if self.running: raise RuntimeError("Stop the scheduler before changing scheduler settings.")
        if not messages: raise ValueError("At least one message is required.")
        self.messages=list(messages); self.interval_minutes=interval_minutes; self.cycle_hours=cycle_hours; self.index=0
