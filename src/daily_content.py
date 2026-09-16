"""Generate 24 deterministic, human-reviewable rewrites.

The templates are intentionally conservative: they preserve the supplied
message and do not add claims or manipulate platform anti-abuse systems.
Review every variant before posting.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

@dataclass(frozen=True)
class ContentPack:
    source: str
    variations: list[str]

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())

def generate_variations(source: str, count: int = 24) -> list[str]:
    source = _clean(source)
    if not source:
        raise ValueError("Daily message cannot be empty")
    if count != 24:
        raise ValueError("This workflow is configured for exactly 24 variations")

    # These are transparent editorial alternatives, not evasion mutations.
    templates = [
        source,
        f"Update: {source}",
        f"Quick update — {source}",
        f"Just a quick note: {source}",
        f"Sharing today's update: {source}",
        f"For today's update: {source}",
        f"Today's note: {source}",
        f"Please note: {source}",
        f"Here's the latest update: {source}",
        f"Latest update — {source}",
        f"Sharing the latest information: {source}",
        f"A quick message for today: {source}",
        f"Today's information is below: {source}",
        f"Please see today's update: {source}",
        f"Here's today's information: {source}",
        f"Today's update is as follows: {source}",
        f"One update for today: {source}",
        f"Sharing one item for today: {source}",
        f"Today's message: {source}",
        f"Latest note for today: {source}",
        f"Please take a look at this update: {source}",
        f"Here is the latest note: {source}",
        f"Sharing a quick note for today: {source}",
        f"One more update: {source}",
    ]
    return templates

def build_pack(source: str, count: int = 24) -> ContentPack:
    return ContentPack(source=_clean(source),
                       variations=generate_variations(source, count))
