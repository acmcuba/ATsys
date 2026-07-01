import json
from typing import Any, Dict

try:
    import requests
except ImportError:
    requests = None

from .storage import EventStorage
from .utils import ensure_parent_dir


class EventPublisher:
    def __init__(self, config: Dict[str, Any]):
        runtime_cfg = config["runtime"]
        delivery_cfg = config.get("delivery", {})

        self.print_to_console = runtime_cfg.get("print_to_console", True)
        self.save_to_sqlite = runtime_cfg.get("save_to_sqlite", True)
        self.save_to_jsonl = runtime_cfg.get("save_to_jsonl", True)
        self.http_post_enabled = runtime_cfg.get("http_post_enabled", False)
        self.http_post_url = runtime_cfg.get("http_post_url")
        self.http_timeout_seconds = runtime_cfg.get("http_timeout_seconds", 5)
        self.sqlite_path = runtime_cfg.get("sqlite_path", "data/events.db")
        self.jsonl_path = runtime_cfg.get("jsonl_path", "data/logs/ilom_events.jsonl")
        self.pending_status_on_http_failure = delivery_cfg.get(
            "pending_status_on_http_failure", True
        )

        self.storage = EventStorage(self.sqlite_path) if self.save_to_sqlite else None

    def save_jsonl(self, event: Dict[str, Any]) -> None:
        ensure_parent_dir(self.jsonl_path)
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def try_http_post(self, event: Dict[str, Any]) -> bool:
        if not self.http_post_enabled:
            return False
        if requests is None:
            print("[WARN] requests no está instalado; no se puede hacer HTTP POST.")
            return False

        try:
            response = requests.post(
                self.http_post_url,
                json=event,
                timeout=self.http_timeout_seconds,
            )
            response.raise_for_status()
            return True
        except Exception as exc:
            print(f"[WARN] Error enviando evento por HTTP: {exc}")
            return False

    def publish(self, event: Dict[str, Any]) -> None:
        delivered = False

        if self.print_to_console:
            print(json.dumps(event, indent=2, ensure_ascii=False))

        if self.save_to_jsonl:
            self.save_jsonl(event)

        if self.http_post_enabled:
            delivered = self.try_http_post(event)

        if self.storage is not None:
            if delivered:
                status = "sent"
            elif self.http_post_enabled and self.pending_status_on_http_failure:
                status = "pending"
            elif self.http_post_enabled:
                status = "failed"
            else:
                status = "pending"
            self.storage.save_event(event, delivery_status=status)
