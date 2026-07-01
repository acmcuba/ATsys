#!/usr/bin/env python3
# ============================================================
#  ATsys API v0.1
#  API REST para ATsys Core (Raspberry Pi 4 compatible)
#  Autor: Tú + IA (OpenAI GPT)
#
#  Endpoints:
#   /system/overview
#   /cpu
#   /gpu
#   /sensors
#   /frus
#   /events
#   /predict
#
#  Auto-documentación:
#    http://<raspberry_ip>:8000/docs
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from atsys_core import ATsysServer


# ============================================================
#  Inicialización ATsys Core
# ============================================================

server = ATsysServer()


# ============================================================
#  Configuración FastAPI
# ============================================================

app = FastAPI(
    title="ATsys API",
    description="API REST del sistema avanzado de supervisión ATsys",
    version="0.1"
)

# Permitir acceso desde dashboard web futuro
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
#  ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "ATsys": "Online",
        "version": "0.1",
        "message": "API del sistema ATsys funcionando correctamente"
    }


@app.get("/system/overview")
def system_overview():
    return server.read_all()


@app.get("/cpu")
def cpu():
    data = server.read_all()
    return data["cpu"]


@app.get("/gpu")
def gpu():
    data = server.read_all()
    return data["gpu"]


@app.get("/sensors")
def sensors():
    data = server.read_all()
    return data["sensors"]


@app.get("/frus")
def frus():
    data = server.read_all()
    return data["frus"]


@app.get("/events")
def events():
    data = server.read_all()
    return data["last_events"]


@app.get("/predict")
def predict():
    data = server.read_all()
    return {
        "system_status": data["system_status"],
        "predictive": data["predictive"]
    }


# ============================================================
#  EJECUCIÓN DIRECTA
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print("Iniciando ATsys API en [0.0.0.0](http://0.0.0.0:8000) ...")
    uvicorn.run("atsys_api:app", host="0.0.0.0", port=8000, reload=True)
