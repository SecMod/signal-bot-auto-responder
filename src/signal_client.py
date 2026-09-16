from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Any

@dataclass
class SignalClient:
    account: str
    signal_cli: str = "signal-cli"

    def _run(self, *args: str) -> str:
        if not self.account.strip():
            raise ValueError("Signal account is required.")
        result = subprocess.run(
            [self.signal_cli, "-a", self.account, *args],
            capture_output=True, text=True, check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "signal-cli failed")
        return result.stdout

    def list_groups(self) -> list[dict[str, Any]]:
        raw = self._run("--output", "json", "listGroups")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("signal-cli returned invalid JSON.") from exc
        if not isinstance(data, list):
            raise RuntimeError("Unexpected listGroups response.")
        groups = []
        for item in data:
            if not isinstance(item, dict):
                continue
            gid = str(item.get("id", "")).strip()
            name = str(item.get("name", "")).strip() or "(Unnamed group)"
            if gid:
                groups.append({"name": name, "group_id": gid})
        return groups
