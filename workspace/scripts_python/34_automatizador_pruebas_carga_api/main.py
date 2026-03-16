import json
import random
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional

# --- Configuración ---
BASE_URL = "https://jsonplaceholder.typicode.com"  # API pública de prueba
NUM_REQUESTS = 50  # Número de solicitudes simuladas
DELAY_BASE = 0.1   # Retraso base entre peticiones (segundos)

def get_random_user_id() -> int:
    return random.randint(1, 10)

def get_random_post_id() -> int:
    return random.randint(1, 100)

def simulate_load_test():
    """
    Simula una carga de trabajo aleatoria contra la API JSONPlaceholder.
    Registra tiempos de respuesta, estado HTTP y datos en un informe JSON.
    """
    report = {
        "fecha_inicio": datetime.now().isoformat(),
        "total_solicitudes": 0,
        "exitos": 0,
        "fallos": 0,
        "tiempos_promedio_usuarios": [],
        "tiempos_promedio_posts": [],
        "datos_muestral": []
    }

    print(f"Iniciando prueba de carga simulada: {NUM_REQUESTS} solicitudes...")
    start_time = time.time()

    for i in range(NUM_REQUESTS):
        # Elección aleatoria de endpoint
        endpoint_type = random.choice(["users", "posts", "comments"])
        endpoint = f"/{endpoint_type}"
        params = {}
        
        # Simular parámetros dinámicos (ej: userId para posts/comments)
        if endpoint_type == "posts":
            params["userId"] = get_random_user_id()
        elif endpoint_type == "comments":
            params["postId"] = get_random_post_id()
            params["limit"] = random.randint(1, 5)
        
        url = f"{BASE_URL}{endpoint}" + f"?{params}" if params else f"{BASE_URL}{endpoint}"
        
        try:
            # Retraso simulado de red
            time.sleep(random.uniform(0, DELAY_BASE))
            
            response = requests.get(url, timeout=5)
            duration = time.time() - start_time
            
            # Registro de datos
            data_point = {
                "id": i + 1,
                "endpoint": url,
                "status_code": response.status_code,
                "duration_ms": round((time.time() - start_time) * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }
            report["datos_muestral"].append(data_point)
            report["total_solicitudes"] += 1

            if response.status_code == 200:
                report["exitos"] += 1
                # Acumulación de tiempos para promedios simples
                if "users" in endpoint:
                    report["tiempos_promedio_usuarios"].append(data_point["duration_ms"])
                elif "posts" in endpoint:
                    report["tiempos_promedio_posts"].append(data_point["duration_ms"])
            else:
                report["fallos"] += 1

        except Exception as e:
            report["fallos"] += 1
            data_point = {
                "id": i + 1,
                "endpoint": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            report["datos_muestral"].append(data_point)

    report["fecha_fin"] = datetime.now().isoformat()
    report["tiempo_total_segundos"] = round(time.time() - start_time, 2)
    report["tiempo_promedio_segundos"] = round(report["tiempo_total_segundos"] / report["total_solicitudes"], 4)

    # Guardar reporte
    filename = f"reporte_carga_{int(time.time())}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=4)
    
    print(f"Prueba completada. Reporte guardado en: {filename}")
    print(f"Éxito: {report['exitos']}/{report['total_solicitudes']}")
    print(f"Tiempo promedio: {report['tiempo_promedio_segundos']}s")

if __name__ == "__main__":
    try:
        simulate_load_test()
    except KeyboardInterrupt:
        print("\nPrueba interrumpida por el usuario.")
    except Exception as e:
        print(f"Error crítico: {e}")