from __future__ import annotations

import json
import random
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def iso_now_local() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_parent_dir(file_path: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def make_sequence_id() -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    rand = random.randint(1000, 9999)
    return f"SEQ-{ts}-{rand}"


def make_command_id() -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    rand = random.randint(1000, 9999)
    return f"CMD-{ts}-{rand}"


def load_json_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_ip_address() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def monotonic_seconds() -> int:
    return int(time.monotonic())
