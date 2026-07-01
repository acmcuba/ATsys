import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml


def iso_now_local() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_parent_dir(file_path: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def make_sequence_id() -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    rand = random.randint(1000, 9999)
    return f"SEQ-{ts}-{rand}"


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dumps_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False)
