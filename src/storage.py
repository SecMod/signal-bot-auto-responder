from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any

class Storage:
    def __init__(self, path: str = "data/bot.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self._init()
    def _init(self):
        self.db.executescript("""
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS packs(id INTEGER PRIMARY KEY, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, source TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS variations(id INTEGER PRIMARY KEY, pack_id INTEGER NOT NULL REFERENCES packs(id) ON DELETE CASCADE, position INTEGER NOT NULL, text TEXT NOT NULL, approved INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS groups(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, group_id TEXT NOT NULL UNIQUE, enabled INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, level TEXT NOT NULL, message TEXT NOT NULL);
        """)
        self.db.commit()
    def close(self): self.db.close()
    def save_pack(self, source: str, variations: list[str]) -> int:
        source = source.strip()
        variations = [v.strip() for v in variations if v.strip()]
        if not source or not variations: raise ValueError("Pack source and at least one variation are required.")
        cur = self.db.execute("INSERT INTO packs(source) VALUES(?)", (source,))
        pid = int(cur.lastrowid)
        self.db.executemany("INSERT INTO variations(pack_id,position,text,approved) VALUES(?,?,?,1)", [(pid,i,v) for i,v in enumerate(variations,1)])
        self.db.commit()
        return pid
    def list_packs(self) -> list[dict[str,Any]]:
        return [dict(r) for r in self.db.execute("SELECT p.id,p.created_at,p.source,COUNT(v.id) variation_count,SUM(v.approved) approved_count FROM packs p LEFT JOIN variations v ON v.pack_id=p.id GROUP BY p.id ORDER BY p.id DESC").fetchall()]
    def get_pack(self, pid: int) -> dict[str,Any] | None:
        p = self.db.execute("SELECT id,created_at,source FROM packs WHERE id=?", (pid,)).fetchone()
        if not p: return None
        return {"id":p[0],"created_at":p[1],"source":p[2],"variations":[dict(r) for r in self.db.execute("SELECT id,position,text,approved FROM variations WHERE pack_id=? ORDER BY position",(pid,)).fetchall()]}
    def delete_pack(self, pid: int): self.db.execute("DELETE FROM packs WHERE id=?", (pid,)); self.db.commit()
    def set_variation(self, vid: int, text: str, approved: bool): self.db.execute("UPDATE variations SET text=?,approved=? WHERE id=?", (text.strip(),int(approved),vid)); self.db.commit()
    def add_group(self, name: str, group_id: str, enabled=True):
        if not name.strip() or not group_id.strip(): raise ValueError("Group name and ID are required.")
        self.db.execute("INSERT INTO groups(name,group_id,enabled) VALUES(?,?,?)",(name.strip(),group_id.strip(),int(enabled))); self.db.commit()
    def remove_group(self, group_id: str): self.db.execute("DELETE FROM groups WHERE group_id=?", (group_id,)); self.db.commit()
    def set_group_enabled(self, group_id: str, enabled: bool): self.db.execute("UPDATE groups SET enabled=? WHERE group_id=?",(int(enabled),group_id)); self.db.commit()
    def get_groups(self, enabled_only=False):
        q = "SELECT id,name,group_id,enabled FROM groups" + (" WHERE enabled=1" if enabled_only else "") + " ORDER BY name"
        return [dict(r) for r in self.db.execute(q).fetchall()]
    def get_setting(self, key, default=None):
        r=self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return r[0] if r else default
    def set_settings(self, values: dict[str,Any]):
        self.db.executemany("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", [(k,str(v)) for k,v in values.items()]); self.db.commit()
    def log(self, level, message):
        self.db.execute("INSERT INTO logs(level,message) VALUES(?,?)",(level.upper(),message)); self.db.commit()
    def get_logs(self, limit=500):
        return [dict(r) for r in self.db.execute("SELECT created_at,level,message FROM logs ORDER BY id DESC LIMIT ?",(limit,)).fetchall()]
