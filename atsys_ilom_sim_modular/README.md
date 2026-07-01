# ATsys ILOM Simulator for Raspberry Pi 4

Simulador modular de eventos ILOM para Raspberry Pi 4, pensado como una SP board virtual.

## Qué incluye

- Identidad de dispositivo tipo SP virtual
- Perfiles ILOM simulados por cadenas de fallas
- Emisión en modo manual, random y scripted
- Persistencia local en SQLite
- Respaldo en JSONL
- Publicación opcional por HTTP POST
- Base preparada para futura inyección de eventos a ATsys

## Estructura

```text
atsys_ilom_sim_modular/
├── main.py
├── retry_pending.py
├── config.yaml
├── requirements.txt
├── README.md
├── data/
│   └── logs/
├── examples/
│   └── sample_profile_run.json
└── ilom_sim/
    ├── __init__.py
    ├── device_identity.py
    ├── event_catalog.py
    ├── profiles.py
    ├── publisher.py
    ├── scheduler.py
    ├── storage.py
    └── utils.py
```

## Instalación

```bash
cd ~/atsys_ilom_sim_modular
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

### Modo manual

```bash
python3 main.py
```

### Reintentar eventos pendientes

```bash
python3 retry_pending.py
```

## Modos

En `config.yaml`:

- `manual`: eliges un perfil por número
- `random`: genera perfiles según pesos
- `scripted`: ejecuta una secuencia definida en JSON

## Preparado para ATsys

Para conectar luego con ATsys:

1. activa `http_post_enabled: true`
2. apunta `http_post_url` al endpoint de ingestión de ATsys
3. deja SQLite activo para cola local `pending/sent/failed`
4. usa `retry_pending.py` para reintentos si cae la red o el endpoint

## JSON estándar

Cada evento incluye:

- `event_id`
- `sequence_id`
- `timestamp`
- `source`
- `origin`
- `class`
- `subclass`
- `severity`
- `server_model`
- `hostname`
- `serial_number`
- `rack_id`
- `station`
- `firmware_version`
- `board_type`
- `component`
- `location`
- `fru`
- `sensor`
- `test_phase`
- `description`
- `details`
- `tags`

## Siguiente integración recomendada

Después de validar localmente en Raspberry:

- publicar hacia VM_v1
- generar `ATsys_ilom_answer`
- disparar reglas automáticas
- reflejar eventos en HMI / Prism / Enigma
