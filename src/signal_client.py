"""Authorized Signal transport boundary.

No CAPTCHA solving, anti-bot bypass, UI automation, or fingerprint spoofing.
"""
import logging
log = logging.getLogger(__name__)

class SignalClient:
    def __init__(self, account: str | None = None):
        self.account = account

    def send_to_group(self, group_id: str, message: str) -> None:
        log.info("Prepared message for group %s: %s", group_id, message)

    def pause_on_verification(self) -> None:
        log.warning("Verification required; pause for manual handling.")
