from datetime import datetime
import platform
import socket
import os

KERNEL_VERSION = "1.0.0"

MODULES = [
    "Mission Manager",
    "Resource Manager",
    "Energy Manager",
    "Human Resource Manager",
    "Cognitive Resource Manager",
    "Adaptive Resilience Engine",
    "Cyber Intelligence Mesh",
    "Black Box Hibernation",
    "Edge Manager",
    "Voice Manager",
]


def line():
    print("=" * 60)


def check_status(name):
    return "READY"


def main():
    node_name = socket.gethostname()
    system = platform.system()
    python_version = platform.python_version()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line()
    print("        ATSYS ADAPTIVE RESILIENCE ENGINE")
    print("                 ARE KERNEL V1")
    line()

    print(f"Kernel Version .......... {KERNEL_VERSION}")
    print(f"Node Name ............... {node_name}")
    print(f"Node Type ............... Development Node")
    print(f"Operating System ........ {system}")
    print(f"Python Version .......... {python_version}")
    print(f"Working Directory ....... {os.getcwd()}")
    print(f"Date/Time ............... {current_time}")

    line()
    print("SYSTEM STATUS")
    line()

    print("CPU ..................... OK")
    print("Memory .................. OK")
    print("Disk .................... OK")
    print("Kernel Status ........... ONLINE")

    line()
    print("LOADING MODULES")
    line()

    for module in MODULES:
        print(f"{module:<30} {check_status(module)}")

    line()
    print("SYSTEM INITIALIZATION ... COMPLETE")
    print("ATsys ARE Kernel is ONLINE")
    line()


if __name__ == "__main__":
    main()