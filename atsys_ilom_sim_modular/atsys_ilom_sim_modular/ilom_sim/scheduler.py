import json
import random
import time
from typing import Any, Dict

from .device_identity import DeviceIdentity
from .event_catalog import EventFactory
from .profiles import PROFILE_REGISTRY
from .publisher import EventPublisher
from .utils import make_sequence_id


def emit_profile(
    profile_name: str,
    factory: EventFactory,
    publisher: EventPublisher,
    delay_seconds: int,
) -> None:
    if profile_name not in PROFILE_REGISTRY:
        raise ValueError(f"Perfil no soportado: {profile_name}")

    sequence_id = make_sequence_id()
    events = PROFILE_REGISTRY[profile_name](factory, sequence_id)

    print(f"\n[INFO] Ejecutando perfil: {profile_name} | sequence_id={sequence_id}\n")

    for idx, event in enumerate(events):
        publisher.publish(event)
        if idx < len(events) - 1:
            time.sleep(delay_seconds)


def choose_weighted_profile(weights: Dict[str, int]) -> str:
    names = list(weights.keys())
    values = list(weights.values())
    return random.choices(names, weights=values, k=1)[0]


def run_manual_mode(config: Dict[str, Any], identity: DeviceIdentity, publisher: EventPublisher) -> None:
    enabled_profiles = config["profiles"]["enabled"]
    delay_seconds = config["timing"]["default_delay_seconds"]
    factory = EventFactory(identity)

    print("\n=== ATsys ILOM Simulator / Manual Mode ===")
    for i, name in enumerate(enabled_profiles, start=1):
        print(f"{i}. {name}")

    selection = input("\nSelecciona un perfil por número: ").strip()
    index = int(selection) - 1
    profile_name = enabled_profiles[index]
    emit_profile(profile_name, factory, publisher, delay_seconds)


def run_random_mode(config: Dict[str, Any], identity: DeviceIdentity, publisher: EventPublisher) -> None:
    interval_seconds = config["random_mode"]["interval_seconds"]
    weights = config["random_mode"]["profile_weights"]
    delay_seconds = config["timing"]["default_delay_seconds"]
    factory = EventFactory(identity)

    print("\n=== ATsys ILOM Simulator / Random Mode ===")
    print("Presiona Ctrl+C para detener.\n")

    while True:
        profile_name = choose_weighted_profile(weights)
        emit_profile(profile_name, factory, publisher, delay_seconds)
        time.sleep(interval_seconds)


def run_scripted_mode(config: Dict[str, Any], identity: DeviceIdentity, publisher: EventPublisher) -> None:
    delay_seconds = config["timing"]["default_delay_seconds"]
    script_path = config.get("scripted", {}).get("script_path", "examples/sample_profile_run.json")
    factory = EventFactory(identity)

    with open(script_path, "r", encoding="utf-8") as f:
        steps = json.load(f)

    print("\n=== ATsys ILOM Simulator / Scripted Mode ===\n")

    for step in steps:
        profile_name = step["profile"]
        wait_before = step.get("wait_before_seconds", 0)
        if wait_before > 0:
            time.sleep(wait_before)
        emit_profile(profile_name, factory, publisher, delay_seconds)
