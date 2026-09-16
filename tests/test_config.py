import pytest
from src.config import Settings

def test_defaults(monkeypatch):
    for k in ("MESSAGE_INTERVAL_MINUTES","VARIATION_COUNT","CYCLE_HOURS","SIGNAL_ACCOUNT","SIGNAL_ENABLED","SIGNAL_CLI_PATH"):
        monkeypatch.delenv(k, raising=False)
    s = Settings.from_env()
    assert (s.interval_minutes,s.variation_count,s.cycle_hours) == (15,24,6)

def test_invalid_integer(monkeypatch):
    monkeypatch.setenv("MESSAGE_INTERVAL_MINUTES","abc")
    with pytest.raises(ValueError):
        Settings.from_env()

def test_invalid_non_positive(monkeypatch):
    monkeypatch.setenv("CYCLE_HOURS","0")
    with pytest.raises(ValueError):
        Settings.from_env()
