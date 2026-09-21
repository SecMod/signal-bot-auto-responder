"""Generate 24 deterministic, human-reviewable Norwegian rewrites."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ContentPack:
    source: str
    variations: list[str]


def _clean(text: str) -> str:
    """Clean spaces while preserving line breaks and blank lines."""
    lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in text.splitlines()
    ]
    return "\n".join(lines).strip()


def generate_variations(source: str, count: int = 24) -> list[str]:
    source = _clean(source)

    if not source:
        raise ValueError("Daily message cannot be empty")

    if count != 24:
        raise ValueError(
            "This workflow is configured for exactly 24 variations"
        )

    templates = [
        f"🔥📢 Dagens oppdatering ✨\n\n{source} 🚀😊",
        f"📣✨ En rask oppdatering 🔥\n\n{source} 💡🙌",
        f"👋😊 Bare en liten oppdatering 🌟\n\n{source} ✨🚀",
        f"📢🔥 Her kommer dagens oppdatering ✨\n\n{source} 😊💫",
        f"🆕🚀 Her er siste nytt 💡\n\n{source} 🔥✨",
        f"🌟📌 Dagens informasjon ✨\n\n{source} 😊🔥",
        f"💬👋 En liten beskjed for i dag ✨\n\n{source} 😊🙌",
        f"🚀🔥 Her er den siste oppdateringen 📢\n\n{source} ✨💡",
        f"📌✨ Siste oppdatering 🔔\n\n{source} 🔥😊",
        f"🔔🙌 Vi deler den siste informasjonen 📢\n\n{source} ✨🚀",
        f"💡🚀 En kort melding for i dag ✨\n\n{source} 😊🔥",
        f"📝📢 Dagens melding finner du nedenfor 👇\n\n{source} ✨😊",
        f"📣✨ Vennligst se dagens oppdatering 👀\n\n{source} 🔥🙌",
        f"🌟🔥 Her er informasjonen for i dag 📌\n\n{source} ✨😊",
        f"📢💫 Dagens oppdatering er som følger 🔥\n\n{source} 🚀✨",
        f"☀️😊 En oppdatering for i dag 📢\n\n{source} ✨🙌",
        f"🔥📌 Vi deler en viktig oppdatering 💡\n\n{source} ✨🚀",
        f"💬✨ Her er dagens melding 📢\n\n{source} 😊🔥",
        f"🆕💡 Den siste informasjonen er 🚀\n\n{source} ✨🙌",
        f"👀📢 Ta gjerne en titt på denne oppdateringen ✨\n\n{source} 💡😊",
        f"🔔✨ Her er den nyeste beskjeden 📌\n\n{source} 🔥🙌",
        f"✨📢 Vi deler en kort oppdatering for i dag 😊\n\n{source} 🚀💫",
        f"🚨🔥 En siste oppdatering 📣\n\n{source} ✨😊",
        f"🎉🌟 Dagens oppdatering er her 🚀\n\n{source} 🔥🙌",
    ]

    return templates


def build_pack(source: str, count: int = 24) -> ContentPack:
    return ContentPack(
        source=_clean(source),
        variations=generate_variations(source, count),
    )
