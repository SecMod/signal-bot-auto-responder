from src.scheduler import Scheduler


def test_rotation_wraps_after_24_messages():
    messages = [f"Message {i:02d}" for i in range(1, 25)]

    scheduler = Scheduler(
        messages=messages,
        interval_minutes=15,
    )

    result = [scheduler.next_message() for _ in range(26)]

    assert result[:24] == messages
    assert result[24] == messages[0]
    assert result[25] == messages[1]


def test_scheduler_starts_at_first_message():
    messages = ["First", "Second", "Third"]

    scheduler = Scheduler(
        messages=messages,
        interval_minutes=15,
    )

    assert scheduler.next_message() == "First"


def test_scheduler_rejects_empty_messages():
    try:
        Scheduler(messages=[], interval_minutes=15)
    except ValueError:
        return

    assert False


def test_scheduler_rejects_invalid_interval():
    try:
        Scheduler(messages=["Message"], interval_minutes=0)
    except ValueError:
        return

    assert False