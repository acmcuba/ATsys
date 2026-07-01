from __future__ import annotations

import random
import time
from typing import Dict

from .profiles import PROFILE_REGISTRY
from .utils import make_sequence_id


def choose_weighted_profile(weights: Dict[str, int]) -> str:
    names = list(weights.keys())
    values = list(weights.values())
    return random.choices(names, weights=values, k=1)[0]


def emit_profile(profile_name: str, factory, publisher, delay_seconds: int) -> str:
    if profile_name not in PROFILE_REGISTRY:
        raise ValueError(f"Perfil no soportado: {profile_name}")
    sequence_id = make_sequence_id()
    events = PROFILE_REGISTRY[profile_name](factory, sequence_id)
    print(f"\n[INFO] Ejecutando perfil: {profile_name} | sequence_id={sequence_id}\n")
    for idx, event in enumerate(events):
        publisher.publish(event)
        if idx < len(events) - 1:
            time.sleep(delay_seconds)
    return sequence_id
