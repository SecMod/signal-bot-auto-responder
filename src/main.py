from __future__ import annotations

from .config import Settings
from .storage import Storage

def build_preview_sender(storage: Storage):
    def process(message: str):
        storage.log("INFO", f"PREVIEW: {message}")
    return process

def build_sender(settings: Settings, storage: Storage):
    # Safe application boundary: scheduler processing is preview-only.
    # Actual Signal delivery remains an explicit, separate operation.
    if settings.signal_enabled:
        storage.log("INFO", "Signal account configured; scheduler remains preview-only.")
    else:
        storage.log("INFO", "Signal disabled; scheduler is preview-only.")
    return build_preview_sender(storage)
