import random

def get_sensors():
    return {
        "MB/TEMP0": {"value": random.randint(35, 70), "unit": "C", "status": "ok"},
        "MB/TEMP1": {"value": random.randint(35, 70), "unit": "C", "status": "ok"},
        "PDB/VOLT0": {"value": round(random.uniform(11.8, 12.3), 2), "unit": "V", "status": "ok"},
        "FAN0/RPM": {"value": random.randint(3000, 8000), "unit": "RPM", "status": "ok"},
        "FAN1/RPM": {"value": random.randint(3000, 8000), "unit": "RPM", "status": "ok"}
    }
