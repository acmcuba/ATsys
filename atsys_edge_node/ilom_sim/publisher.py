from __future__ import annotations

import json
from typing import Any, Dict

import requests

from .storage import SQLiteStore
from .utils import ensure_parent_dir


class EventPublisher:
    def __init__(self, config: Dict[str, Any], store: SQLiteStore):
        runtime_cfg = config["runtime"]
        self.store = store
        self.print_to_console = runtime_cfg.get("print_to_console", True)
        self.save_to_jsonl = runtime_cfg.get("save_to_jsonl", True)
        self.http_post_enabled = runtime_cfg.get("http_post_enabled", False)
        self.http_post_url = runtime_cfg.get("http_post_url")
        self.http_timeout_seconds = runtime_cfg.get("http_timeout_seconds", 5)
        self.jsonl_path = runtime_cfg.get("jsonl_path", "data/logs/ilom_events.jsonl")

    def _save_jsonl(self, event: Dict[str, Any]) -> None:
        ensure_parent_dir(self.jsonl_path)
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _post_http(self, event: Dict[str, Any]) -> bool:
        if not self.http_post_enabled or not self.http_post_url:
            return False
        try:
            response = requests.post(self.http_post_url, json=event, timeout=self.http_timeout_seconds)
            response.raise_for_status()
            return True
        except Exception:
            return False

    def publish(self, event: Dict[str, Any]) -> bool:
        delivered = False
        if self.print_to_console:
            print(json.dumps(event, indent=2, ensure_ascii=False))
        if self.save_to_jsonl:
            self._save_jsonl(event)
        if self.http_post_enabled:
            delivered = self._post_http(event)
        self.store.save_event(event, delivery_status="sent" if delivered else "pending")
        self.store.add_sync_queue("event", event, status="pending" if not delivered else "sent")
        return delivered
