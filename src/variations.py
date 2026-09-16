"""Message variation utilities."""

from __future__ import annotations

from .daily_content import generate_variations


def validate_variations(messages: list[str], expected: int = 24) -> list[str]:
    """Validate and normalize a list of approved message variations."""
    cleaned = [message.strip() for message in messages if message.strip()]

    if len(cleaned) != expected:
        raise ValueError(
            f"Expected {expected} non-empty variations, got {len(cleaned)}."
        )

    return cleaned


def load_variations(path: str, expected: int = 24) -> list[str]:
    """Load one variation per line from a UTF-8 text file."""
    with open(path, "r", encoding="utf-8") as file:
        messages = file.readlines()

    return validate_variations(messages, expected)


def save_variations(
    messages: list[str],
    path: str,
    expected: int = 24,
) -> None:
    """Save approved variations, one message per line."""
    messages = validate_variations(messages, expected)

    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(messages) + "\n")
