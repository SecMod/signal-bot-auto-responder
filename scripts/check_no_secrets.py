from __future__ import annotations

"""Fail CI/local checks if sensitive local Signal data is tracked.

This checks Git-tracked files only. It does not inspect untracked local files.
"""

import re
import subprocess
from pathlib import Path

FORBIDDEN_NAMES = {
    "bot.db",
    "bot.sqlite",
    "bot.sqlite3",
}

FORBIDDEN_PARTS = (
    "signal-data/",
    "signal-cli-data/",
)

SENSITIVE_PATTERNS = (
    re.compile(r"sgnl://linkdevice\?[^\s"']+"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PRIVATE )?PRIVATE KEY-----"),
)

def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        capture_output=True,
        check=True,
    )
    return [p for p in result.stdout.decode("utf-8").split("\0") if p]

def main() -> int:
    violations: list[str] = []

    for name in tracked_files():
        normalized = name.replace("\\", "/")
        base = Path(name).name.lower()

        if base in FORBIDDEN_NAMES or normalized.startswith("data/"):
            violations.append(f"forbidden local-data file: {name}")
            continue
        if any(part in normalized.lower() for part in FORBIDDEN_PARTS):
            violations.append(f"forbidden Signal data path: {name}")
            continue

        path = Path(name)
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                violations.append(f"sensitive Signal/credential material detected: {name}")
                break

    if violations:
        print("SECURITY CHECK FAILED")
        for violation in violations:
            print(f"- {violation}")
        print("Remove the sensitive/local data from Git before committing.")
        return 1

    print("Security check passed: no tracked local Signal data or detected secrets.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
