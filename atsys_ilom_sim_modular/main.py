print("Cargando configuración YAML...")
from fastapi import FastAPI
from event_engine import generate_event, events
from sensor_engine import get_sensors

app = FastAPI()

@app.get("/rest/v1/Systems/Server/logs/events")
def get_events():
    return {"events": events}

@app.post("/rest/v1/Systems/Server/generate")
def generate():
    return generate_event()

@app.get("/rest/v1/Systems/Server/Sensors")
def sensors():
    return get_sensors()
