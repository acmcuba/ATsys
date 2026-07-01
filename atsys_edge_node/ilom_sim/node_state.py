from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

from .utils import iso_now_local


@dataclass
class NodeState:
    node_id: str
    status: str = "online"
    current_mode: str = "manual"
    active_profile: Optional[str] = None
    last_heartbeat_at: Optional[str] = None
    last_sync_at: Optional[str] = None
    last_command_at: Optional[str] = None
    atsys_link_status: str = "disconnected"
    queue_depth: int = 0
    last_event_timestamp: Optional[str] = None
    last_error: Optional[str] = None
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["updated_at"] = iso_now_local()
        return data
