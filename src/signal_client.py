from __future__ import annotations

import json
import os
import re
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

        cli = self.signal_cli.strip()
        if not cli:
            raise ValueError("signal-cli path is required.")

        if os.path.sep in cli or "/" in cli:
            if not os.path.exists(cli):
                raise FileNotFoundError(
                    f"signal-cli executable not found: {cli}"
                )

        command = [cli, "-a", self.account, *args]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                shell=cli.lower().endswith((".bat", ".cmd")),
                timeout=60,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "signal-cli timed out after 60 seconds. "
                "Check for another signal-cli instance or a locked Signal data directory."
            ) from exc
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Could not start signal-cli: {cli}. "
                f"Check Settings → signal-cli path."
            ) from exc

        if result.returncode:
            raise RuntimeError(
                result.stderr.strip()
                or result.stdout.strip()
                or "signal-cli failed"
            )

        return result.stdout

    def list_accounts(self) -> list[str]:
        """Return Signal accounts registered in this local signal-cli installation."""
        cli = self.signal_cli.strip()

        if not cli:
            raise ValueError("signal-cli path is required.")

        if os.path.sep in cli or "/" in cli:
            if not os.path.exists(cli):
                raise FileNotFoundError(
                    f"signal-cli executable not found: {cli}"
                )

        command = [cli, "listAccounts"]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                shell=cli.lower().endswith((".bat", ".cmd")),
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Could not start signal-cli: {cli}. "
                f"Check Settings → signal-cli path."
            ) from exc

        if result.returncode:
            raise RuntimeError(
                result.stderr.strip()
                or result.stdout.strip()
                or "signal-cli listAccounts failed"
            )

        accounts = re.findall(
            r"Number:s*(+d+)",
            result.stdout,
        )

        return list(dict.fromkeys(accounts))

    def link(self, device_name: str = "Signal Bot") -> subprocess.Popen:
        """Start signal-cli device linking without an account argument."""
        cli = self.signal_cli.strip()

        if not cli:
            raise ValueError("signal-cli path is required.")

        if os.path.sep in cli or "/" in cli:
            if not os.path.exists(cli):
                raise FileNotFoundError(
                    f"signal-cli executable not found: {cli}"
                )

        command = [cli, "link", "-n", device_name]

        try:
            return subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=cli.lower().endswith((".bat", ".cmd")),
                bufsize=1,
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Could not start signal-cli: {cli}. "
                f"Check Settings → signal-cli path."
            ) from exc

    @staticmethod
    def extract_link_uri(output: str) -> str | None:
        match = re.search(
            r"sgnl://linkdevice?[^s
]+",
            output,
        )
        return match.group(0).rstrip('"'') if match else None

    def refresh(self) -> None:
        """Process pending Signal events/storage sync before querying groups."""
        self._run("receive", "--timeout", "1")

    def list_groups(self) -> list[dict[str, Any]]:
        """Return groups available to the linked Signal account.

        Group discovery only needs listGroups. Do not run receive here:
        receive is a separate synchronization operation and can leave a Java
        process waiting on the local Signal data/config while the GUI is trying
        to refresh the group list.
        """
        raw = self._run(
            "--output",
            "json",
            "listGroups",
        )

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "signal-cli returned invalid JSON."
            ) from exc

        if not isinstance(data, list):
            raise RuntimeError(
                "Unexpected listGroups response."
            )

        groups = []

        for item in data:
            if not isinstance(item, dict):
                continue

            gid = str(item.get("id", "")).strip()
            name = str(item.get("name", "")).strip()

            if not name:
                name = "(Unnamed group)"

            if gid:
                groups.append(
                    {
                        "name": name,
                        "group_id": gid,
                    }
                )

        return groups

    def send_to_group(
        self,
        group_id: str,
        message: str = "",
        attachments: list[str] | None = None,
    ) -> None:
        """Send a message or image attachments to a Signal group."""
        group_id = group_id.strip()
        message = message.strip()
        attachments = [
            str(path).strip()
            for path in (attachments or [])
            if str(path).strip()
        ]

        if not group_id:
            raise ValueError("Signal group ID is required.")

        if not message and not attachments:
            raise ValueError("Message or at least one attachment is required.")

        for path in attachments:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Attachment not found: {path}")

        args = ["send", "-g", group_id]

        if message:
            args.extend(["-m", message])

        if attachments:
            args.extend(["-a", *attachments])

        self._run(*args)
