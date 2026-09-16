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

    @classmethod
    def from_env(cls) -> "Settings":
        interval_minutes = int(
            os.getenv("MESSAGE_INTERVAL_MINUTES", "15")
        )
        variation_count = int(
            os.getenv("VARIATION_COUNT", "24")
        )
        cycle_hours = int(
            os.getenv("CYCLE_HOURS", "6")
        )

        if interval_minutes <= 0:
            raise ValueError(
                "MESSAGE_INTERVAL_MINUTES must be greater than zero."
            )

        if variation_count <= 0:
            raise ValueError(
                "VARIATION_COUNT must be greater than zero."
            )

        if cycle_hours <= 0:
            raise ValueError(
                "CYCLE_HOURS must be greater than zero."
            )

        signal_account = os.getenv(
            "SIGNAL_ACCOUNT", ""
        ).strip()

        signal_enabled = os.getenv(
            "SIGNAL_ENABLED", "false"
        ).strip().lower() == "true"

        return cls(
            interval_minutes=interval_minutes,
            variation_count=variation_count,
            cycle_hours=cycle_hours,
            signal_account=signal_account,
            signal_enabled=signal_enabled,
        )