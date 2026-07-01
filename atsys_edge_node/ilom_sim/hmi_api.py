from __future__ import annotations

from typing import Any, Dict, Optional

import yaml
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from .command_queue import CommandExecutor
from .storage import SQLiteStore

CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

TOKEN = CONFIG.get("hmi_api", {}).get("auth_token", "")
STORE = SQLiteStore(CONFIG["runtime"]["sqlite_path"])
app = FastAPI(title="ATsys Edge Node API", version="1.0.0")


class EmitProfileRequest(BaseModel):
    profile_name: str
    delay_seconds: Optional[int] = None


class SetModeRequest(BaseModel):
    mode: str


def _auth(x_atsys_token: Optional[str]) -> None:
    if TOKEN and x_atsys_token != TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
def health():
    return {"status": "ok", "service": "atsys-edge-api"}


@app.get("/node/info")
def node_info(x_atsys_token: Optional[str] = Header(default=None)):
    _auth(x_atsys_token)
    return {
        "device": CONFIG["device"],
        "edge_node": CONFIG["edge_node"],
        "profiles": CONFIG["profiles"]["enabled"],
    }


@app.get("/node/state")
def node_state(x_atsys_token: Optional[str] = Header(default=None)):
    _auth(x_atsys_token)
    node_id = CONFIG["edge_node"]["node_id"]
    state = STORE.get_node_state(node_id)
    return state or {"node_id": node_id, "status": "unknown"}


@app.get("/events/recent")
def recent_events(limit: int = 20, x_atsys_token: Optional[str] = Header(default=None)):
    _auth(x_atsys_token)
    return {"events": STORE.get_recent_events(limit=limit)}


@app.post("/emit/profile")
def emit_profile(req: EmitProfileRequest, x_atsys_token: Optional[str] = Header(default=None)):
    _auth(x_atsys_token)
    executor = CommandExecutor.shared()
    result = executor.execute({
        "command_type": "emit_profile",
        "node_id": CONFIG["edge_node"]["node_id"],
        "payload": {"profile_name": req.profile_name, "delay_seconds": req.delay_seconds},
    })
    return result


@app.post("/mode/set")
def mode_set(req: SetModeRequest, x_atsys_token: Optional[str] = Header(default=None)):
    _auth(x_atsys_token)
    executor = CommandExecutor.shared()
    return executor.execute({
        "command_type": "set_mode",
        "node_id": CONFIG["edge_node"]["node_id"],
        "payload": {"mode": req.mode},
    })


@app.post("/service/restart")
def service_restart(x_atsys_token: Optional[str] = Header(default=None)):
    _auth(x_atsys_token)
    executor = CommandExecutor.shared()
    return executor.execute({
        "command_type": "restart_service",
        "node_id": CONFIG["edge_node"]["node_id"],
        "payload": {},
    })


@app.post("/commands/execute")
def commands_execute(command: Dict[str, Any], x_atsys_token: Optional[str] = Header(default=None)):
    _auth(x_atsys_token)
    executor = CommandExecutor.shared()
    return executor.execute(command)
