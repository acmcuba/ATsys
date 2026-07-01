#!/usr/bin/env python3
# ============================================================
#  ATsys Core - Version 0.1 (Single-File Edition)
#  Sistema Avanzado de Supervisión, Sensores, FRUs y Predicción
#  Autor: Tú con asistencia de IA (OpenAI GPT)
#
#  Este archivo es autosuficiente y funciona en Raspberry Pi 4.
#  Es la base para: ATsys-Shell, API REST, Dashboard Web y
#  versión embebida en hardware BMC/SP de ATsys.
#
# ============================================================


import time
import random
import psutil
from datetime import datetime, timedelta


# ============================================================
#  UTILIDADES GENERALES
# ============================================================

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clamp(value, minv, maxv):
    return max(min(value, maxv), minv)


# ============================================================
#  CLASE: Sensor
# ============================================================

class Sensor:
    """
    Representa un sensor genérico del sistema:
    Temperatura, voltaje, amperaje, ventiladores, etc.
    """

    def __init__(self, name, sensor_type, unit, value=0.0,
                 min_val=None, max_val=None, simulate=False):
        self.name = name
        self.type = sensor_type      # "temperature", "voltage", "current", etc.
        self.unit = unit
        self.value = value
        self.min = min_val
        self.max = max_val
        self.simulate = simulate     # True = el sensor se actualizará solo
        self.last_update = datetime.now()

    def update(self):
        """
        Actualiza sensores simulados:
        temperatura, voltaje, ventiladores, etc.
        """
        if not self.simulate:
            return self.value

        # Simulación simple con variación suave
        delta = (random.random() - 0.5) * 0.3
        new_value = self.value + delta

        if self.min is not None and self.max is not None:
            new_value = clamp(new_value, self.min, self.max)

        self.value = new_value
        self.last_update = datetime.now()
        return self.value

    def read(self):
        """Devuelve valor actual (actualizando si aplica)."""
        self.update()
        return self.value


# ============================================================
#  CLASE: CPU
# ============================================================

class CPUStatus:
    """Estado del CPU, usando psutil si está disponible."""

    def __init__(self):
        self.cores = psutil.cpu_count(logical=True)
        self.temps = Sensor("CPU Temp", "temperature", "°C",
                            value=45, min_val=30, max_val=80, simulate=True)

    def read(self):
        return {
            "temperature": self.temps.read(),
            "usage_percent": psutil.cpu_percent(interval=0.1),
            "freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            "cores": self.cores
        }


# ============================================================
#  CLASE: GPU (SIMULADA ahora)
# ============================================================

class GPUStatus:
    """
    GPU simulada.
    Más adelante se reemplazará con NVML.
    """

    def __init__(self):
        self.present = True
        self.temp = Sensor("GPU Temp", "temperature", "°C",
                           value=50, min_val=35, max_val=85, simulate=True)
        self.memory_used = 1024       # MB simulados
        self.memory_total = 8192
        self.usage = 0
        self.ecc_errors = 0
        self.power = Sensor("GPU Power", "power", "W",
                            value=110, min_val=60, max_val=220, simulate=True)

    def update(self):
        self.usage = random.randint(0, 100)
        self.memory_used = clamp(
            self.memory_used + random.randint(-50, 50), 0, self.memory_total
        )
        self.ecc_errors += random.choice([0, 0, 1])  # ECC suave

    def read(self):
        self.update()
        return {
            "temperature": self.temp.read(),
            "usage_percent": self.usage,
            "memory_used_mb": self.memory_used,
            "memory_total_mb": self.memory_total,
            "ecc_errors": self.ecc_errors,
            "power_watts": self.power.read()
        }


# ============================================================
#  CLASE: SENSORES DEL SISTEMA
# ============================================================

class SystemSensors:
    """Sensores generales del sistema (voltaje, corriente, fans, PSU)."""

    def __init__(self):
        self.volt_12v = Sensor("12V Rail", "voltage", "V",
                               value=12.2, min_val=11.5, max_val=12.6, simulate=True)
        self.volt_5v = Sensor("5V Rail", "voltage", "V",
                              value=5.1, min_val=4.8, max_val=5.3, simulate=True)
        self.volt_3v3 = Sensor("3.3V Rail", "voltage", "V",
                               value=3.31, min_val=3.1, max_val=3.5, simulate=True)
        self.fan0 = Sensor("FAN0", "fan", "RPM",
                           value=3800, min_val=2000, max_val=5000, simulate=True)
        self.fan1 = Sensor("FAN1", "fan", "RPM",
                           value=3900, min_val=2000, max_val=5000, simulate=True)
        self.psu_status = "OK"

    def read(self):
        return {
            "12v": self.volt_12v.read(),
            "5v": self.volt_5v.read(),
            "3v3": self.volt_3v3.read(),
            "fan0": self.fan0.read(),
            "fan1": self.fan1.read(),
            "psu_status": self.psu_status
        }


# ============================================================
#  CLASE: FRU
# ============================================================

class FRU:
    """Field Replaceable Unit."""

    def __init__(self, name, part, serial, status="OK"):
        self.name = name
        self.part = part
        self.serial = serial
        self.status = status


# ============================================================
#  EVENTOS Y LOG
# ============================================================

class EventLog:
    """Registro de eventos del sistema."""

    def __init__(self):
        self.events = []

    def add(self, severity, component, message):
        entry = {
            "time": now(),
            "severity": severity,
            "component": component,
            "message": message
        }
        self.events.append(entry)

    def last(self, n=10):
        return self.events[-n:]


# ============================================================
#  REGLAS Y PREDICCIÓN
# ============================================================

class RuleEngine:
    """Reglas simples para determinar estado OK / DEGRADED / CRITICAL."""

    def evaluate(self, sensor_data, cpu_data, gpu_data):
        status = "OK"

        # CPU caliente
        if cpu_data["temperature"] > 75:
            status = "CRITICAL"
        elif cpu_data["temperature"] > 65:
            status = "DEGRADED"

        # GPU caliente
        if gpu_data["temperature"] > 80:
            status = "CRITICAL"
        elif gpu_data["temperature"] > 70 and status != "CRITICAL":
            status = "DEGRADED"

        # Voltajes fuera de rango
        if sensor_data["12v"] < 11.7 or sensor_data["12v"] > 12.4:
            status = "DEGRADED"

        return status


class PredictiveEngine:
    """Motor de detección de tendencias (versión ligera)."""

    def __init__(self):
        self.history = []

    def add(self, cpu_temp, gpu_temp):
        if len(self.history) > 120:
            self.history.pop(0)
        self.history.append((cpu_temp, gpu_temp))

    def trend(self):
        if len(self.history) < 10:
            return "INSUFFICIENT_DATA"

        c_temps = [c for c, g in self.history]
        g_temps = [g for c, g in self.history]

        cpu_up = c_temps[-1] > c_temps[-10]
        gpu_up = g_temps[-1] > g_temps[-10]

        if cpu_up or gpu_up:
            return "RISK_RISING"

        return "STABLE"


# ============================================================
#  CLASE PRINCIPAL: ATsysServer
# ============================================================

class ATsysServer:
    """Representa un servidor completo dentro de ATsys."""

    def __init__(self):
        self.boot_time = datetime.now()
        self.cpu = CPUStatus()
        self.gpu = GPUStatus()
        self.sensors = SystemSensors()
        self.events = EventLog()
        self.rules = RuleEngine()
        self.predict = PredictiveEngine()

        self.frus = [
            FRU("Motherboard", "MB-ATSYS-01", "SN-MB12345"),
            FRU("CPU", "RPi4-CPU", "SN-CPU0001"),
            FRU("RAM", "4GB-DDR4", "SN-RAM0001"),
            FRU("Storage", "MicroSD 64GB", "SN-SD0001"),
            FRU("PSU", "5V/3A", "SN-PSU0001"),
        ]

        self.events.add("INFO", "BOOT", "ATsys Core iniciado")

    def read_all(self):
        """Lee todos los subsistemas y evalúa estado general."""
        cpu_data = self.cpu.read()
        gpu_data = self.gpu.read()
        sensor_data = self.sensors.read()

        # Guardar en predictor
        self.predict.add(cpu_data["temperature"],
                         gpu_data["temperature"])

        # Evaluar estado
        system_status = self.rules.evaluate(
            sensor_data, cpu_data, gpu_data)

        return {
            "time": now(),
            "system_status": system_status,
            "predictive": self.predict.trend(),
            "cpu": cpu_data,
            "gpu": gpu_data,
            "sensors": sensor_data,
            "frus": [
                {"name": f.name, "part": f.part, "serial": f.serial, "status": f.status}
                for f in self.frus
            ],
            "last_events": self.events.last(5),
            "uptime_minutes": int((datetime.now() - self.boot_time).total_seconds() / 60)
        }


# ============================================================
#  DEMO — EJECUCIÓN DIRECTA DEL SISTEMA (Temporal)
# ============================================================

if __name__ == "__main__":
    server = ATsysServer()

    print("\nATsys Core v0.1 — Iniciado en modo demostración\n")

    for i in range(5):
        data = server.read_all()
        print(f"[{data['time']}] Estado del sistema: {data['system_status']}, Tendencia: {data['predictive']}")
        time.sleep(1)

    print("\nATsys Core finalizado.\n")
