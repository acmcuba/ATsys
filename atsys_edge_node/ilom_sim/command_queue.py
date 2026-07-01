from __future__ import annotations

from typing import Any, Dict, Optional

from .utils import iso_now_local


class CommandExecutor:
    _instance: Optional["CommandExecutor"] = None

    def __init__(self):
        self.context = None

    @classmethod
    def shared(cls) -> "CommandExecutor":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def bind(self, context: Any) -> None:
        self.context = context

    def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        if self.context is None:
            raise RuntimeError("CommandExecutor has no bound context")

        command_id = command.get("command_id") or self.context.make_command_id()
        command_type = command["command_type"]
        payload = command.get("payload", {})
        node_id = command.get("node_id", self.context.node_id)
        now = iso_now_local()

        self.context.store.save_command({
            "command_id": command_id,
            "node_id": node_id,
            "command_type": command_type,
            "payload": payload,
            "timestamp": now,
        }, status="received")

        try:
            if command_type == "emit_profile":
                profile_name = payload["profile_name"]
                delay = int(payload.get("delay_seconds", self.context.default_delay_seconds))
                result = self.context.emit_profile(profile_name, delay_seconds=delay)
            elif command_type == "set_mode":
                mode = payload["mode"]
                self.context.set_mode(mode)
                result = {"mode": mode}
            elif command_type == "get_status":
                result = self.context.get_status_payload()
            elif command_type == "pause_emission":
                self.context.pause_emission()
                result = {"paused": True}
            elif command_type == "resume_emission":
                self.context.resume_emission()
                result = {"paused": False}
            elif command_type == "restart_service":
                result = {"message": "systemd should restart this service externally"}
            else:
                raise ValueError(f"Unsupported command_type: {command_type}")

            final = {
                "command_id": command_id,
                "node_id": node_id,
                "status": "completed",
                "started_at": now,
                "finished_at": iso_now_local(),
                "result": result,
            }
            self.context.store.mark_command_result(command_id, "completed", final)
            self.context.state.last_command_at = final["finished_at"]
            return final
        except Exception as exc:
            final = {
                "command_id": command_id,
                "node_id": node_id,
                "status": "failed",
                "started_at": now,
                "finished_at": iso_now_local(),
                "result": {"error": str(exc)},
            }
            self.context.store.mark_command_result(command_id, "failed", final)
            self.context.state.last_command_at = final["finished_at"]
            self.context.state.last_error = str(exc)
            return final
