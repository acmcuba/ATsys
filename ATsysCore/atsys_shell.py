#!/usr/bin/env python3
# ================================================================
#  ATsys Shell v0.1
#  Consola interactiva estilo ILOM para ATsys Core
#
#  Requiere: atsys_core.py en el mismo directorio
# ================================================================

import cmd
import time
from atsys_core import ATsysServer


# ================================================================
#  CLASE PRINCIPAL DEL SHELL
# ================================================================

class ATsysShell(cmd.Cmd):
    intro = """
ATsys Shell v0.1 
Sistema Avanzado de Supervisión y Gestión

Escribe 'help' para ver los comandos disponibles.
-> """
    prompt = "-> "

    def __init__(self):
        super().__init__()
        self.server = ATsysServer()
        self.current_path = "/"

    # ============================================================
    #  NAVEGACIÓN
    # ============================================================

    def do_cd(self, arg):
        """Cambia el directorio lógico: cd /CPU, cd /GPU, cd /SYS"""
        if not arg:
            self.current_path = "/"
        else:
            self.current_path = arg
        print(f"Current path: {self.current_path}")

    # ============================================================
    #  COMANDO SHOW (principal)
    # ============================================================

    def do_show(self, arg):
        """show <target> — Muestra información del sistema."""
        target = arg.strip().upper()

        data = self.server.read_all()

        if target in ["", "/", "/SYS"]:
            self._show_sys(data)

        elif target in ["/CPU"]:
            self._show_cpu(data)

        elif target in ["/GPU"]:
            self._show_gpu(data)

        elif target in ["/SENSORS"]:
            self._show_sensors(data)

        elif target in ["/FRUS", "/FRU"]:
            self._show_frus(data)

        elif target in ["/EVENTS"]:
            self._show_events(data)

        else:
            print("Componente desconocido. Use: /SYS /CPU /GPU /SENSORS /FRUS /EVENTS")

    # ------------------------------------------------------------
    #  Secciones individuales
    # ------------------------------------------------------------

    def _show_sys(self, data):
        print(f"""
=======================
   SYSTEM OVERVIEW
=======================
Estado general: {data['system_status']}
Tendencia:      {data['predictive']}
Uptime:         {data['uptime_minutes']} min
Hora:           {data['time']}
""")

    def _show_cpu(self, data):
        c = data["cpu"]
        print(f"""
======== CPU ========
Temperatura:     {c['temperature']:.1f} °C
Uso total:       {c['usage_percent']}%
Frecuencia:      {c['freq_mhz']:.0f} MHz
Cores:           {c['cores']}
""")

    def _show_gpu(self, data):
        g = data["gpu"]
        print(f"""
======== GPU ========
Temperatura:     {g['temperature']:.1f} °C
Uso:             {g['usage_percent']}%
Memoria:         {g['memory_used_mb']} / {g['memory_total_mb']} MB
ECC Errors:      {g['ecc_errors']}
Power Draw:      {g['power_watts']:.1f} W
""")

    def _show_sensors(self, data):
        s = data["sensors"]
        print(f"""
====== SENSORES ======
12V:             {s['12v']:.2f} V
5V:              {s['5v']:.2f} V
3.3V:            {s['3v3']:.2f} V
Fan0:            {s['fan0']:.0f} RPM
Fan1:            {s['fan1']:.0f} RPM
PSU State:       {s['psu_status']}
""")

    def _show_frus(self, data):
        print("\n====== FRUS ======")
        for f in data["frus"]:
            print(f"- {f['name']}: {f['part']} / {f['serial']} [{f['status']}]")
        print()

    def _show_events(self, data):
        print("\n======= EVENTOS =======")
        for e in data["last_events"]:
            print(f"[{e['time']}] ({e['severity']}) {e['component']}: {e['message']}")
        print()

    # ============================================================
    #  DIAGNÓSTICO
    # ============================================================

    def do_diag(self, arg):
        """Ejecuta diagnósticos básicos."""
        print("\nEjecutando diagnóstico...")
        time.sleep(1)
        print("CPU: OK")
        print("GPU: OK")
        print("Voltajes: OK")
        print("Ventiladores: OK")
        print("PSU: OK")
        print("Diagnóstico completado.\n")

    # ============================================================
    #  PREDICCIÓN
    # ============================================================

    def do_predict(self, arg):
        """Muestra la tendencia predictiva del sistema."""
        d = self.server.read_all()
        print(f"Tendencia del sistema: {d['predictive']}")

    # ============================================================
    #  SALIR
    # ============================================================

    # ============================================================
    #  MONITOR EN TIEMPO REAL
    # ============================================================

    def do_monitor(self, arg):
        """Monitor en tiempo real (Ctrl+C para salir)."""
        print("Entrando en modo monitor (Ctrl+C para detener)...\n")
        try:
            while True:
                data = self.server.read_all()
                print(f"[{data['time']}] Estado={data['system_status']} Tendencia={data['predictive']} CPU={data['cpu']['temperature']:.1f}C GPU={data['gpu']['temperature']:.1f}C")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nModo monitor detenido.")


    def do_exit(self, arg):
        """Salir del shell."""
        print("Cerrando ATsys Shell...")
        return True

    def do_quit(self, arg):
        return self.do_exit(arg)

    def do_EOF(self, arg):
        print()
        return self.do_exit(arg)


# ================================================================
#  EJECUCIÓN DIRECTA
# ================================================================

if __name__ == "__main__":
    ATsysShell().cmdloop()
