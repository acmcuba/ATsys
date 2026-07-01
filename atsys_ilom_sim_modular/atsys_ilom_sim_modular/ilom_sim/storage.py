import json
import sqlite3
from typing import Any, Dict, List, Tuple

from .utils import ensure_parent_dir


class EventStorage:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self._init_sqlite()

    def _init_sqlite(self) -> None:
        ensure_parent_dir(self.sqlite_path)
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ilom_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    sequence_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    component TEXT NOT NULL,
                    location TEXT NOT NULL,
                    test_phase TEXT,
                    description TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    delivery_status TEXT NOT NULL DEFAULT 'pending'
                )
                """
            )
            conn.commit()

    def save_event(self, event: Dict[str, Any], delivery_status: str = "pending") -> None:
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                """
                INSERT INTO ilom_events (
                    event_id, sequence_id, timestamp, severity, component,
                    location, test_phase, description, payload_json, delivery_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["event_id"],
                    event["sequence_id"],
                    event["timestamp"],
                    event["severity"],
                    event["component"],
                    event["location"],
                    event.get("test_phase"),
                    event["description"],
                    json.dumps(event, ensure_ascii=False),
                    delivery_status,
                ),
            )
            conn.commit()

    def get_pending_events(self, limit: int = 100) -> List[Tuple[int, Dict[str, Any]]]:
        with sqlite3.connect(self.sqlite_path) as conn:
            rows = conn.execute(
                """
                SELECT id, payload_json
                FROM ilom_events
                WHERE delivery_status = 'pending'
                ORDER BY id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [(row_id, json.loads(payload_json)) for row_id, payload_json in rows]

    def update_delivery_status_by_row_id(self, row_id: int, status: str) -> None:
        with sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                "UPDATE ilom_events SET delivery_status = ? WHERE id = ?",
                (status, row_id),
            )
            conn.commit()
