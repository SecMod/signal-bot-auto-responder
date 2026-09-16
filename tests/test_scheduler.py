import time
import pytest
from src.scheduler import Scheduler


def test_rotation_wraps():
    s = Scheduler([f"M{i}" for i in range(24)], 15, 6)
    result = [s.next_message() for _ in range(26)]
    assert result[:24] == s.messages
    assert result[24:] == ["M0", "M1"]


def test_rejects_invalid():
    with pytest.raises(ValueError):
        Scheduler([], 15, 6)
    with pytest.raises(ValueError):
        Scheduler(["x"], 0, 6)
    with pytest.raises(ValueError):
        Scheduler(["x"], 15, 0)


def test_start_stop():
    seen = []
    s = Scheduler(["x"], 15, 6)
    assert s.start(seen.append) is True
    for _ in range(50):
        if seen:
            break
        time.sleep(0.01)
    s.stop()
    assert seen == ["x"]
    assert s.running is False


def test_update():
    s = Scheduler(["a"], 15, 6)
    s.update(["b", "c"], 5, 2)
    assert (s.messages, s.interval_minutes, s.cycle_hours) == (["b", "c"], 5, 2)


def test_cycle_limit():
    assert Scheduler(["x"], 15, 6).max_messages_per_cycle == 24
    assert Scheduler(["x"], 20, 1).max_messages_per_cycle == 3
    assert Scheduler(["x"], 90, 1).max_messages_per_cycle == 1
