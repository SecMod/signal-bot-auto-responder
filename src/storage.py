"""SQLite persistence for content packs and authorized group configuration."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class Storage:
    def __init__(self, path: str = "data/bot.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.db = sqlite3.connect(self.path)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS packs (
                id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                source TEXT NOT NULL
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS variations (
                id INTEGER PRIMARY KEY,
                pack_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                text TEXT NOT NULL,
                approved INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(pack_id) REFERENCES packs(id)
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                group_id TEXT NOT NULL UNIQUE,
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.db.commit()

    def save_pack(self, source: str, variations: list[str]) -> int:
        cur = self.db.execute(
            "INSERT INTO packs(source) VALUES (?)",
            (source,),
        )

        pack_id = cur.lastrowid

        self.db.executemany(
            """
            INSERT INTO variations(pack_id, position, text, approved)
            VALUES (?, ?, ?, 1)
            """,
            [
                (pack_id, position, text)
                for position, text in enumerate(variations, 1)
            ],
        )

        self.db.commit()
        return int(pack_id)

    def approve(self, variation_id: int, approved: bool) -> None:
        self.db.execute(
            "UPDATE variations SET approved=? WHERE id=?",
            (int(approved), variation_id),
        )
        self.db.commit()

    def add_group(self, name: str, group_id: str) -> None:
        name = name.strip()
        group_id = group_id.strip()

        if not name:
            raise ValueError("Group name cannot be empty.")

        if not group_id:
            raise ValueError("Group ID cannot be empty.")

        self.db.execute(
            """
            INSERT INTO groups(name, group_id, enabled)
            VALUES (?, ?, 1)
            """,
            (name, group_id),
        )

        self.db.commit()

    def remove_group(self, group_id: str) -> None:
        self.db.execute(
            "DELETE FROM groups WHERE group_id=?",
            (group_id,),
        )
        self.db.commit()

    def set_group_enabled(self, group_id: str, enabled: bool) -> None:
        self.db.execute(
            "UPDATE groups SET enabled=? WHERE group_id=?",
            (int(enabled), group_id),
        )
        self.db.commit()

    def get_groups(self, enabled_only: bool = False) -> list[dict]:
        if enabled_only:
            rows = self.db.execute(
                """
                SELECT id, name, group_id, enabled
                FROM groups
                WHERE enabled=1
                ORDER BY name
                """
            ).fetchall()
        else:
            rows = self.db.execute(
                """
                SELECT id, name, group_id, enabled
                FROM groups
                ORDER BY name
                """
            ).fetchall()

        return [
            {
                "id": row[0],
                "name": row[1],
                "group_id": row[2],
                "enabled": bool(row[3]),
            }
            for row in rows
        ]
