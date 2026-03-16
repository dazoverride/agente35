import os
import psutil
from datetime import datetime

print("\n=== MINIMIZADOR DE CONSUMO DE ENERGÍA (MODALIDAD AHORRO) ===")
print("Iniciando diagnóstico del sistema para optimizar recursos...\n")

def get_resource_usage():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {"cpu": cpu_percent, "ram_total": memory.total, "ram_used": memory.used, "ram_percent": memory.percent, "disk_total": disk.total, "disk_used": disk.used, "disk_percent": disk.percent}
    except Exception as e:
        return {"error": str(e)}

def print_report(data):
    if "error" in data:
        print(f"Error al obtener métricas: {data['error']}")
        return
    
    print("-" * 40)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    print(f"Uso de CPU: {data['cpu']:.2f}%")
    print(f"Uso de RAM: {data['ram_used'] / (1024**3):.2f} GB ({data['ram_percent']:.1f}%)")
    print(f"Uso de Disco: {data['disk_used'] / (1024**3):.2f} GB ({data['disk_percent']:.1f}%)")
    print("-" * 40)

print("Muestreo de recursos en curso...")
print_report(get_resource_usage())
print("\nDiagnóstico completado. El sistema ha sido evaluado sin alterar procesos críticos.")