# ATsys Edge Node for Raspberry Pi

Este paquete convierte la Raspberry Pi en un nodo oficial ATsys con:

- SP virtual / simulador ILOM
- heartbeat periódico
- sincronización base con Prism
- API local para HMI
- cola local SQLite
- servicio systemd

## Instalación rápida

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
cd ~/atsys_edge_node
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Ejecutar la API local

```bash
source .venv/bin/activate
uvicorn ilom_sim.hmi_api:app --host 0.0.0.0 --port 8090
```

## Servicio systemd

Copia `deploy/atsys-edge-node.service` a `/etc/systemd/system/` y ajusta el usuario/ruta.

```bash
sudo cp deploy/atsys-edge-node.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable atsys-edge-node
sudo systemctl start atsys-edge-node
sudo systemctl status atsys-edge-node
```

## API local

- `GET /health`
- `GET /node/info`
- `GET /node/state`
- `GET /events/recent?limit=20`
- `POST /emit/profile`
- `POST /mode/set`
- `POST /service/restart`
- `POST /commands/execute`

Usa header:

```text
X-ATSYS-TOKEN: CHANGE_ME_EDGE_TOKEN
```

## Flujo

Raspberry Pi Edge Node -> SQLite local -> Heartbeat / Prism Sync -> HMI / ATsys
