import uuid
import random
from datetime import datetime

events = []

messages = [
    "SP initiated a soft reset",
    "PSU0 voltage out of range",
    "FAN3 speed degraded",
    "CPU1 thermal trip detected",
    "OSFP2 link down",
    "BF3 heartbeat lost",
    "HMC0 link degraded",
    "PDB voltage instability detected"
]

classes = ["SP", "PDB", "CPU", "GPU", "OSFP", "FAN", "PSU"]

def generate_event():
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uuid": str(uuid.uuid4()),
        "severity": random.choice(["minor", "major", "critical"]),
        "class": random.choice(classes),
        "event": random.choice(["fault", "warning", "info"]),
        "message": random.choice(messages)
    }
    events.append(event)
    return event
