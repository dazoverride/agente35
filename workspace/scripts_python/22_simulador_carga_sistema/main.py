import random
import time
import threading
import json
import sys
import os

# Configuración de los servicios del sistema
SERVICIOS = {
    "web_server": {"estado": "activo", "carga_cpu": 15, "carga_ram": 20, "errores": 0},
    "database": {"estado": "activo", "carga_cpu": 30, "carga_ram": 45, "errores": 0},
    "cache_redis": {"estado": "activo", "carga_cpu": 5, "carga_ram": 10, "errores": 0},
    "worker_queue": {"estado": "activo", "carga_cpu": 25, "carga_ram": 35, "errores": 0},
    "backup_service": {"estado": "pausado", "carga_cpu": 2, "carga_ram": 5, "errores": 0}
}

# Colores para la terminal
VERDE = '\033[92m'
ROJO = '\033[91m'
AMARILLO = '\033[93m'
BLANCO = '\033[0m'

def obtener_carga_aleatoria(base, variacion=10):
    return max(0, min(100, int(base + random.randint(-variacion, variacion))))

def simular_estado_servicio(servicio):
    # Simular cambios en la carga
    servicio['carga_cpu'] = obtener_carga_aleatoria(servicio['carga_cpu'])
    servicio['carga_ram'] = obtener_carga_aleatoria(servicio['carga_ram'])
    
    # Probabilidad baja de error (1% por tick)
    if random.random() < 0.01:
        servicio['errores'] += 1
        servicio['estado'] = 'inestable'
        return "[!!] ERROR DETECTADO"
    
    # Si los errores se acumulan demasiado, el servicio cae
    if servicio['errores'] >= 5:
        servicio['estado'] = 'caido'
        return "[CRIT] SERVICIO CAIDO"
    
    return ""

def renderizar_tablero():
    print(f"\n{'='*60}")
    print(f"{'SIMULADOR DE CARGA DE SISTEMA':^60}")
    print(f"{'='*60}\n")
    
    for nombre, datos in SERVICIOS.items():
        estado_texto = datos['estado'].upper()
        color = VERDE if datos['estado'] == 'activo' else AMARILLO if datos['estado'] == 'inestable' else ROJO
        
        barra_cpu = '█' * int(datos['carga_cpu'] / 5) + '░' * (20 - int(datos['carga_cpu'] / 5))
        barra_ram = '█' * int(datos['carga_ram'] / 5) + '░' * (20 - int(datos['carga_ram'] / 5))
        
        print(f"{color}[{nombre}] {BLANCO} {estado_texto} | CPU: {datos['carga_cpu']}% | RAM: {datos['carga_ram']}% | Errores: {datos['errores']} {barra_cpu} {barra_ram}")
    print(f"{'='*60}\n")

def loop_principal():
    print("Simulación iniciada. Presiona Ctrl+C para detener.")
    try:
        while True:
            for nombre in SERVICIOS:
                mensaje = simular_estado_servicio(SERVICIOS[nombre])
                if mensaje:
                    print(mensaje)
            renderizar_tablero()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulación detenida por el usuario.")
        # Guardar estado final
        with open('estado_final_simulacion.json', 'w') as f:
            json.dump(SERVICIOS, f, indent=4)
        print("Estado final guardado en estado_final_simulacion.json")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--load":
        if os.path.exists('estado_final_simulacion.json'):
            with open('estado_final_simulacion.json', 'r') as f:
                SERVICIOS.update(json.load(f))
            print("Estado cargado desde archivo.")
    
    loop_principal()
