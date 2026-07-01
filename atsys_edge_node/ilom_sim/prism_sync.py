from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

import requests

from .node_state import NodeState
from .storage import SQLiteStore
from .utils import iso_now_local


class PrismSyncClient:
    def __init__(self, config: Dict[str, Any], store: SQLiteStore, state: NodeState):
        self.config = config
        self.store = store
        self.state = state
        self.enabled = config.get("prism_sync", {}).get("enabled", False)
        self.interval_seconds = config.get("prism_sync", {}).get("interval_seconds", 20)
        prism = config.get("prism_sync", {})
        self.status_endpoint = prism.get("status_endpoint")
        self.commands_pull_endpoint = prism.get("commands_pull_endpoint")
        self.command_results_endpoint = prism.get("command_results_endpoint")
        self.auth_token = prism.get("auth_token", "")
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}

    def push_status(self) -> bool:
        if not self.status_endpoint:
            return False
        payload = {
            "node_id": self.state.node_id,
            "status": self.state.status,
            "current_mode": self.state.current_mode,
            "active_profile": self.state.active_profile,
            "last_heartbeat_at": self.state.last_heartbeat_at,
            "last_sync_at": iso_now_local(),
            "atsys_link_status": self.state.atsys_link_status,
            "queue_depth": self.store.queue_depth(),
            "last_event_timestamp": self.state.last_event_timestamp,
        }
        try:
            resp = requests.post(self.status_endpoint, json=payload, headers=self._headers(), timeout=5)
            resp.raise_for_status()
            self.state.last_sync_at = payload["last_sync_at"]
            self.state.atsys_link_status = "connected"
            return True
        except Exception as exc:
            self.state.last_error = f"prism_status_error: {exc}"
            self.state.atsys_link_status = "degraded"
            return False

    def pull_commands(self) -> List[Dict[str, Any]]:
        if not self.commands_pull_endpoint:
            return []
        try:
            resp = requests.post(self.commands_pull_endpoint, json={"node_id": self.state.node_id}, headers=self._headers(), timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return data.get("commands", []) if isinstance(data, dict) else []
        except Exception as exc:
            self.state.last_error = f"prism_commands_error: {exc}"
            return []

    def post_command_result(self, result: Dict[str, Any]) -> bool:
        if not self.command_results_endpoint:
            return False
        try:
            resp = requests.post(self.command_results_endpoint, json=result, headers=self._headers(), timeout=5)
            resp.raise_for_status()
            return True
        except Exception as exc:
            self.state.last_error = f"prism_command_result_error: {exc}"
            return False

    def _run(self) -> None:
        from .command_queue import CommandExecutor
        executor = CommandExecutor.shared()
        while not self._stop.is_set():
            self.push_status()
            for command in self.pull_commands():
                result = executor.execute(command)
                self.post_command_result(result)
            self._stop.wait(self.interval_seconds)

    def start(self) -> None:
        if not self.enabled or self._thread:
            return
        self._thread = threading.Thread(target=self._run, name="prism-sync", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
