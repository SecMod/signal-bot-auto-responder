from __future__ import annotations
import logging
from .config import Settings
from .signal_client import SignalClient
from .storage import Storage

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")

def build_sender(settings: Settings, storage: Storage):
    if not settings.signal_enabled:
        return lambda message: storage.log("INFO",f"DRY RUN: {message}")
    if not settings.signal_account:
        raise ValueError("SIGNAL_ACCOUNT is required when Signal is enabled.")
    SignalClient(settings.signal_account, settings.signal_cli_path or "signal-cli")
    def send(message):
        storage.log("INFO",f"Signal transport configured; explicit delivery required for message ({len(message)} chars).")
    return send
