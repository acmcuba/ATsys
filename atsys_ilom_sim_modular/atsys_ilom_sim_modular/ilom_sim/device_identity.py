from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class DeviceIdentity:
    server_model: str
    hostname: str
    serial_number: str
    rack_id: str
    station: str
    firmware_version: str
    board_type: str
    origin: str


def build_identity(config: Dict[str, Any]) -> DeviceIdentity:
    d = config["device"]
    return DeviceIdentity(
        server_model=d["server_model"],
        hostname=d["hostname"],
        serial_number=d["serial_number"],
        rack_id=d["rack_id"],
        station=d["station"],
        firmware_version=d["firmware_version"],
        board_type=d["board_type"],
        origin=d["origin"],
    )
