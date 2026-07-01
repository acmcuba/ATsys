from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional

from .utils import ensure_parent_dir, iso_now_local


class SQLiteStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        ensure_parent_dir(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
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
                    delivery_status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS edge_heartbeats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    delivery_status TEXT NOT NULL DEFAULT 'pending'
                );

                CREATE TABLE IF NOT EXISTS edge_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id TEXT NOT NULL UNIQUE,
                    node_id TEXT NOT NULL,
                    command_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    executed_at TEXT,
                    status TEXT NOT NULL,
                    result_json TEXT
                );

                CREATE TABLE IF NOT EXISTS node_state (
                    node_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    current_mode TEXT NOT NULL,
                    active_profile TEXT,
                    last_heartbeat_at TEXT,
                    last_sync_at TEXT,
                    last_command_at TEXT,
                    atsys_link_status TEXT NOT NULL,
                    queue_depth INTEGER NOT NULL DEFAULT 0,
                    last_event_timestamp TEXT,
                    last_error TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT
                );
                """
            )
            conn.commit()

    def save_event(self, event: Dict[str, Any], delivery_status: str = "pending") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO ilom_events (event_id, sequence_id, timestamp, severity, component, location,
                test_phase, description, payload_json, delivery_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["event_id"], event["sequence_id"], event["timestamp"], event["severity"],
                    event["component"], event["location"], event.get("test_phase"), event["description"],
                    json.dumps(event, ensure_ascii=False), delivery_status,
                ),
            )
            conn.commit()

    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload_json FROM ilom_events ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    def save_heartbeat(self, node_id: str, payload: Dict[str, Any], delivery_status: str = "pending") -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO edge_heartbeats (node_id, timestamp, payload_json, delivery_status) VALUES (?, ?, ?, ?)",
                (node_id, payload["timestamp"], json.dumps(payload, ensure_ascii=False), delivery_status),
            )
            conn.commit()

    def save_command(self, command: Dict[str, Any], status: str = "received") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO edge_commands (command_id, node_id, command_type, payload_json, received_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    command["command_id"],
                    command["node_id"],
                    command["command_type"],
                    json.dumps(command, ensure_ascii=False),
                    command["timestamp"],
                    status,
                ),
            )
            conn.commit()

    def mark_command_result(self, command_id: str, status: str, result: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE edge_commands SET executed_at=?, status=?, result_json=? WHERE command_id=?",
                (iso_now_local(), status, json.dumps(result, ensure_ascii=False), command_id),
            )
            conn.commit()

    def upsert_node_state(self, state: Dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO node_state (
                    node_id, status, current_mode, active_profile, last_heartbeat_at, last_sync_at,
                    last_command_at, atsys_link_status, queue_depth, last_event_timestamp, last_error, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(node_id) DO UPDATE SET
                    status=excluded.status,
                    current_mode=excluded.current_mode,
                    active_profile=excluded.active_profile,
                    last_heartbeat_at=excluded.last_heartbeat_at,
                    last_sync_at=excluded.last_sync_at,
                    last_command_at=excluded.last_command_at,
                    atsys_link_status=excluded.atsys_link_status,
                    queue_depth=excluded.queue_depth,
                    last_event_timestamp=excluded.last_event_timestamp,
                    last_error=excluded.last_error,
                    updated_at=excluded.updated_at
                """,
                (
                    state["node_id"], state["status"], state["current_mode"], state.get("active_profile"),
                    state.get("last_heartbeat_at"), state.get("last_sync_at"), state.get("last_command_at"),
                    state["atsys_link_status"], state["queue_depth"], state.get("last_event_timestamp"),
                    state.get("last_error"), state["updated_at"],
                ),
            )
            conn.commit()

    def get_node_state(self, node_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM node_state WHERE node_id=?", (node_id,)).fetchone()
        return dict(row) if row else None

    def add_sync_queue(self, item_type: str, payload: Dict[str, Any], status: str = "pending") -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO sync_queue (item_type, payload_json, created_at, status) VALUES (?, ?, ?, ?)",
                (item_type, json.dumps(payload, ensure_ascii=False), iso_now_local(), status),
            )
            conn.commit()

    def queue_depth(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM sync_queue WHERE status='pending'").fetchone()
        return int(row[0])
