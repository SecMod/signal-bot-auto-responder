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
    signal_group_ids: tuple[str, ...] = ()
    signal_enabled: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        group_ids = tuple(
            group_id.strip()
            for group_id in os.getenv("SIGNAL_GROUP_IDS", "").split(",")
            if group_id.strip()
        )

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
            signal_account=os.getenv(
                "SIGNAL_ACCOUNT", ""
            ).strip(),
            signal_group_ids=group_ids,
            signal_enabled=os.getenv(
                "SIGNAL_ENABLED", "false"
            ).strip().lower() == "true",
        )