from __future__ import annotations

import shutil
import threading
import time
from typing import Any, Dict, Optional

import psutil
import requests

from .node_state import NodeState
from .storage import SQLiteStore
from .utils import get_ip_address, iso_now_local, monotonic_seconds


class HeartbeatManager:
    def __init__(self, config: Dict[str, Any], store: SQLiteStore, state: NodeState):
        self.config = config
        self.store = store
        self.state = state
        self.enabled = config.get("heartbeat", {}).get("enabled", False)
        self.interval_seconds = config.get("heartbeat", {}).get("interval_seconds", 30)
        self.endpoint = config.get("heartbeat", {}).get("endpoint")
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._start_monotonic = monotonic_seconds()

    def build_payload(self) -> Dict[str, Any]:
        disk = shutil.disk_usage("/")
        return {
            "message_type": "heartbeat",
            "timestamp": iso_now_local(),
            "node_id": self.state.node_id,
            "rack_id": self.config["edge_node"]["rack_id"],
            "station": self.config["edge_node"]["station"],
            "status": self.state.status,
            "uptime_seconds": monotonic_seconds() - self._start_monotonic,
            "ip_address": get_ip_address(),
            "last_event_timestamp": self.state.last_event_timestamp,
            "queue_depth": self.store.queue_depth(),
            "disk_free_mb": int(disk.free / (1024 * 1024)),
            "cpu_load": psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else 0.0,
            "memory_used_mb": int(psutil.virtual_memory().used / (1024 * 1024)),
            "temperature_c": None,
            "mode": self.state.current_mode,
            "active_profile": self.state.active_profile,
            "atsys_link": self.state.atsys_link_status,
        }

    def _send(self, payload: Dict[str, Any]) -> bool:
        if not self.endpoint:
            return False
        try:
            resp = requests.post(self.endpoint, json=payload, timeout=5)
            resp.raise_for_status()
            return True
        except Exception:
            return False

    def tick(self) -> None:
        payload = self.build_payload()
        ok = self._send(payload) if self.enabled else False
        self.store.save_heartbeat(self.state.node_id, payload, delivery_status="sent" if ok else "pending")
        self.store.add_sync_queue("heartbeat", payload, status="pending" if not ok else "sent")
        self.state.last_heartbeat_at = payload["timestamp"]
        self.state.atsys_link_status = "connected" if ok else self.state.atsys_link_status

    def _run(self) -> None:
        while not self._stop.is_set():
            self.tick()
            self._stop.wait(self.interval_seconds)

    def start(self) -> None:
        if not self.enabled or self._thread:
            return
        self._thread = threading.Thread(target=self._run, name="heartbeat-manager", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
