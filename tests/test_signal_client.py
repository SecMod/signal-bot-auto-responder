from unittest.mock import patch

import pytest

from src.signal_client import SignalClient


def test_send_to_group_builds_expected_command():
    client = SignalClient(
        account="+10000000000",
        signal_cli="signal-cli",
    )

    with patch("src.signal_client.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stderr = ""

        client.send_to_group(
            "TEST-GROUP-ID",
            "Hello from test",
        )

        run.assert_called_once_with(
            [
                "signal-cli",
                "-a",
                "+10000000000",
                "send",
                "-g",
                "TEST-GROUP-ID",
                "-m",
                "Hello from test",
            ],
            capture_output=True,
            text=True,
            check=False,
        )


def test_send_to_group_rejects_empty_group():
    client = SignalClient(account="+10000000000")

    with pytest.raises(ValueError, match="group_id"):
        client.send_to_group("", "Hello")


def test_send_to_group_rejects_empty_message():
    client = SignalClient(account="+10000000000")

    with pytest.raises(ValueError, match="message"):
        client.send_to_group("TEST-GROUP-ID", "")


def test_send_to_group_raises_on_signal_cli_failure():
    client = SignalClient(
        account="+10000000000",
        signal_cli="signal-cli",
    )

    with patch("src.signal_client.subprocess.run") as run:
        run.return_value.returncode = 1
        run.return_value.stderr = "test failure"

        with pytest.raises(RuntimeError, match="signal-cli failed"):
            client.send_to_group(
                "TEST-GROUP-ID",
                "Hello from test",
            )