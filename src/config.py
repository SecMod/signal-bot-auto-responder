import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    interval_minutes: int = 15
    variation_count: int = 24
    cycle_hours: int = 6

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            interval_minutes=int(
                os.getenv("MESSAGE_INTERVAL_MINUTES", "15")
            ),
            variation_count=int(
                os.getenv("VARIATION_COUNT", "24")
            ),
            cycle_hours=int(
                os.getenv("CYCLE_HOURS", "6")
            ),
        )
