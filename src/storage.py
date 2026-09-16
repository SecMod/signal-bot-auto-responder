"""SQLite persistence for daily content packs and review state."""
from __future__ import annotations
import sqlite3
from pathlib import Path

class Storage:
    def __init__(self, path: str = "data/bot.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS packs (
            id INTEGER PRIMARY KEY, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            source TEXT NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS variations (
            id INTEGER PRIMARY KEY, pack_id INTEGER NOT NULL, position INTEGER NOT NULL,
            text TEXT NOT NULL, approved INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(pack_id) REFERENCES packs(id))""")
        self.db.commit()

    def save_pack(self, source: str, variations: list[str]) -> int:
        cur = self.db.execute("INSERT INTO packs(source) VALUES (?)", (source,))
        pack_id = cur.lastrowid
        self.db.executemany(
            "INSERT INTO variations(pack_id,position,text) VALUES (?,?,?)",
            [(pack_id, i, text) for i, text in enumerate(variations, 1)],
        )
        self.db.commit()
        return int(pack_id)

    def approve(self, variation_id: int, approved: bool) -> None:
        self.db.execute("UPDATE variations SET approved=? WHERE id=?",
                        (int(approved), variation_id))
        self.db.commit()
