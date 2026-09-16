import subprocess
import sys

def test_cli_generates_24_variations():
    p = subprocess.run(
        [sys.executable, "-m", "src.cli"],
        input="Authorized security assessment\n",
        text=True,
        capture_output=True,
        check=True,
    )
    assert "24 review slots:" in p.stdout
    assert "No messages were sent." in p.stdout
    assert p.stdout.count("\n") >= 26
