from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    interval_minutes: int = 15
    variation_count: int = 24
    cycle_hours: int = 6
    signal_account: str = ""
    signal_enabled: bool = False
    signal_cli_path: str = ""

    @classmethod
    def from_env(cls) -> "Settings":
        def positive(name: str, default: str) -> int:
            raw = os.getenv(name, default)
            try:
                value = int(raw)
            except ValueError as exc:
                raise ValueError(f"{name} must be an integer.") from exc
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero.")
            return value
        return cls(
            positive("MESSAGE_INTERVAL_MINUTES", "15"),
            positive("VARIATION_COUNT", "24"),
            positive("CYCLE_HOURS", "6"),
            os.getenv("SIGNAL_ACCOUNT", "").strip(),
            os.getenv("SIGNAL_ENABLED", "false").strip().lower() == "true",
            os.getenv("SIGNAL_CLI_PATH", "").strip(),
        )
