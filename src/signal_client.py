from __future__ import annotations

import json
import os
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
        cli=self.signal_cli.strip()
        if not cli:
            raise ValueError("signal-cli path is required.")
        if os.path.sep in cli or "/" in cli:
            if not os.path.exists(cli):
                raise FileNotFoundError(f"signal-cli executable not found: {cli}")
        command=[cli, "-a", self.account, *args]
        try:
            result=subprocess.run(
                command, capture_output=True, text=True, check=False,
                shell=cli.lower().endswith((".bat",".cmd")),
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Could not start signal-cli: {cli}. Check Settings → signal-cli path."
            ) from exc
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "signal-cli failed")
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

    def send_to_group(self, group_id: str, message: str) -> None:
        group_id = group_id.strip()
        message = message.strip()
        if not group_id:
            raise ValueError("Signal group ID is required.")
        if not message:
            raise ValueError("Message is required.")
        self._run("send", "-g", group_id, "-m", message)
