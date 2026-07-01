from __future__ import annotations

import json
import threading
import time
from typing import Any, Dict

import yaml

from .command_queue import CommandExecutor
from .device_identity import DeviceIdentity
from .event_catalog import EventFactory
from .heartbeat import HeartbeatManager
from .node_state import NodeState
from .prism_sync import PrismSyncClient
from .publisher import EventPublisher
from .scheduler import choose_weighted_profile, emit_profile as scheduler_emit_profile
from .storage import SQLiteStore
from .utils import load_json_file, make_command_id


class EdgeNodeApp:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.store = SQLiteStore(config["runtime"]["sqlite_path"])
        self.identity = DeviceIdentity.from_config(config)
        self.factory = EventFactory(self.identity)
        self.publisher = EventPublisher(config, self.store)
        self.node_id = config["edge_node"]["node_id"]
        self.default_delay_seconds = config["timing"].get("default_delay_seconds", 2)
        self.state = NodeState(node_id=self.node_id, current_mode=config["runtime"]["mode"])
        self.pause_flag = threading.Event()
        self.pause_flag.set()
        self.heartbeat = HeartbeatManager(config, self.store, self.state)
        self.prism_sync = PrismSyncClient(config, self.store, self.state)
        CommandExecutor.shared().bind(self)
        self.persist_state()

    def make_command_id(self) -> str:
        return make_command_id()

    def persist_state(self) -> None:
        self.state.queue_depth = self.store.queue_depth()
        self.store.upsert_node_state(self.state.to_dict())

    def emit_profile(self, profile_name: str, delay_seconds: int | None = None) -> Dict[str, Any]:
        self.pause_flag.wait()
        delay = delay_seconds if delay_seconds is not None else self.default_delay_seconds
        self.state.active_profile = profile_name
        sequence_id = scheduler_emit_profile(profile_name, self.factory, self.publisher, delay)
        recent = self.store.get_recent_events(limit=1)
        self.state.last_event_timestamp = recent[0]["timestamp"] if recent else None
        self.state.active_profile = None
        self.persist_state()
        return {"sequence_id": sequence_id, "events_emitted": len(self.store.get_recent_events(limit=10))}

    def set_mode(self, mode: str) -> None:
        if mode not in {"manual", "random", "scripted"}:
            raise ValueError("Mode must be manual, random, or scripted")
        self.state.current_mode = mode
        self.persist_state()

    def pause_emission(self) -> None:
        self.pause_flag.clear()
        self.persist_state()

    def resume_emission(self) -> None:
        self.pause_flag.set()
        self.persist_state()

    def get_status_payload(self) -> Dict[str, Any]:
        self.persist_state()
        return self.store.get_node_state(self.node_id) or {"node_id": self.node_id}

    def run_manual_mode(self) -> None:
        enabled_profiles = self.config["profiles"]["enabled"]
        print("\n=== ATsys Edge Node / Manual Mode ===")
        for i, name in enumerate(enabled_profiles, start=1):
            print(f"{i}. {name}")
        selection = input("\nSelecciona un perfil por número: ").strip()
        index = int(selection) - 1
        self.emit_profile(enabled_profiles[index], self.default_delay_seconds)

    def run_random_mode(self) -> None:
        interval_seconds = self.config["random_mode"]["interval_seconds"]
        weights = self.config["random_mode"]["profile_weights"]
        print("\n=== ATsys Edge Node / Random Mode ===")
        print("Presiona Ctrl+C para detener.\n")
        while True:
            self.pause_flag.wait()
            profile_name = choose_weighted_profile(weights)
            self.emit_profile(profile_name, self.default_delay_seconds)
            time.sleep(interval_seconds)

    def run_scripted_mode(self) -> None:
        script_path = "examples/sample_profile_run.json"
        steps = load_json_file(script_path)
        print("\n=== ATsys Edge Node / Scripted Mode ===\n")
        for step in steps:
            self.pause_flag.wait()
            wait_before = step.get("wait_before_seconds", 0)
            if wait_before > 0:
                time.sleep(wait_before)
            self.emit_profile(step["profile"], self.default_delay_seconds)

    def start_background_services(self) -> None:
        self.heartbeat.start()
        self.prism_sync.start()
        self.persist_state()

    def stop_background_services(self) -> None:
        self.heartbeat.stop()
        self.prism_sync.stop()
        self.persist_state()

    def run(self) -> None:
        self.start_background_services()
        mode = self.state.current_mode
        if mode == "manual":
            self.run_manual_mode()
        elif mode == "random":
            self.run_random_mode()
        elif mode == "scripted":
            self.run_scripted_mode()
        else:
            raise ValueError(f"Modo no soportado: {mode}")


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    config = load_config()
    app = EdgeNodeApp(config)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo ATsys Edge Node...")
    finally:
        app.stop_background_services()
