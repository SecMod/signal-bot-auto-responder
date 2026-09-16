"""Signal CLI transport adapter.

Requires signal-cli to be installed and configured separately.
This module does not automate the Signal desktop UI or bypass
verification / anti-abuse challenges.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class SignalClient:
    account: str
    signal_cli: str = r"C:\Users\prakh\signal-cli\signal-cli-0.14.8\bin\signal-cli.bat"

    def send_to_group(self, group_id: str, message: str) -> None:
        """Send an approved message to a configured Signal group."""
        if not group_id.strip():
            raise ValueError("group_id cannot be empty.")

        if not message.strip():
            raise ValueError("message cannot be empty.")

        command = [
            self.signal_cli,
            "-a",
            self.account,
            "send",
            "-g",
            group_id,
            "-m",
            message,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            error = result.stderr.strip() or "Unknown signal-cli error"
            raise RuntimeError(f"signal-cli failed: {error}")