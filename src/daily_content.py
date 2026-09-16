"""Create a reviewable daily content pack.

This intentionally produces placeholders rather than attempting to disguise
automated traffic. Replace the rewrite provider with an approved editorial
workflow that a human reviews before posting.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class ContentPack:
    source: str
    variations: list[str]

def build_pack(source: str, count: int = 24) -> ContentPack:
    source = source.strip()
    if not source:
        raise ValueError("Daily message cannot be empty")
    if count < 1:
        raise ValueError("count must be positive")
    return ContentPack(source=source, variations=[source] * count)
