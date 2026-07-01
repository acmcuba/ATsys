from __future__ import annotations

from typing import Any, Dict, List

from .device_identity import DeviceIdentity
from .utils import iso_now_local


class EventFactory:
    def __init__(self, identity: DeviceIdentity):
        self.identity = identity
        self._event_counter = 0

    def build_event(
        self,
        sequence_id: str,
        event_code: str,
        event_class: str,
        subclass: str,
        severity: str,
        component: str,
        location: str,
        fru: str,
        sensor: str,
        test_phase: str,
        description: str,
        details: Dict[str, Any],
        tags: List[str],
    ) -> Dict[str, Any]:
        self._event_counter += 1
        return {
            "event_id": f"{event_code}-{self._event_counter:04d}",
            "sequence_id": sequence_id,
            "timestamp": iso_now_local(),
            "source": "ILOM",
            "origin": self.identity.origin,
            "class": event_class,
            "subclass": subclass,
            "severity": severity,
            "server_model": self.identity.server_model,
            "hostname": self.identity.hostname,
            "serial_number": self.identity.serial_number,
            "rack_id": self.identity.rack_id,
            "station": self.identity.station,
            "firmware_version": self.identity.firmware_version,
            "board_type": self.identity.board_type,
            "component": component,
            "location": location,
            "fru": fru,
            "sensor": sensor,
            "test_phase": test_phase,
            "description": description,
            "details": details,
            "tags": tags,
        }
