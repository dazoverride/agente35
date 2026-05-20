import os
import sys

# Asegurar que importamos los modulos del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import tests.llama_test
import subprocess
import json
import time
from tests.llama_test import CARPETA_MODELOS, PUERTO, RUTA_LLAMA_SERVER, ejecutar_bateria

def iniciar_servidor_cpu(thinking=False, modelo_archivo=""):
    tests.llama_test.detener_servidor()
    ruta_modelo_completa = os.path.join(CARPETA_MODELOS, modelo_archivo)
    kwargs = json.dumps({"enable_thinking": thinking})
    comando = [
        RUTA_LLAMA_SERVER,
        "-m", ruta_modelo_completa,
        "-c", "4096",
        "-ngl", "0", # FORZAMOS USO DE CPU
        "--port", str(PUERTO),
        "--chat-template-kwargs", kwargs
    ]
    print(f"\n[+] Iniciando llama-server EN MODO CPU (-ngl 0)...")
    tests.llama_test.servidor_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import urllib.request
    print("    [!] Esperando a que el modelo cargue en RAM (Puede tardar más en CPU)...")
    for i in range(180):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{PUERTO}/health")
            with urllib.request.urlopen(req, timeout=1) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get("status") in ["ok", "ready"]:
                        break
        except Exception:
            pass
        if tests.llama_test.servidor_process.poll() is not None:
             print("\n❌ Error: El proceso de llama-server ha colapsado.")
             sys.exit(1)
        time.sleep(1)
    else:
        print("\n❌ Error: Tiempo de espera agotado al cargar el modelo.")
        sys.exit(1)
    print("[+] Servidor de pruebas en línea.\n")

tests.llama_test.iniciar_servidor = iniciar_servidor_cpu

def main():
    # Solo enfrentamos a estos dos colosos
    modelos_a_probar = [
        "google_gemma-4-E2B-it-Q4_K_M.gguf",
        "google_gemma-4-E4B-it-Q4_K_M.gguf"
    ]
    
    modelos_disponibles = [f for f in os.listdir(CARPETA_MODELOS) if f.endswith(".gguf")]
    modelos_finales = [m for m in modelos_a_probar if m in modelos_disponibles]
    
    if not modelos_finales:
        print("❌ No se encontraron los modelos en la carpeta 'models'.")
        return

    # Set de pruebas exhaustivas (Acertijos y Lógica)
    prompts_acertijos = [
        "Un bate y una pelota cuestan 1.10 euros en total. El bate cuesta 1.00 euro más que la pelota. ¿Cuánto cuesta la pelota exactamente? Explica tu razonamiento.",
        "Tengo ciudades pero no casas. Tengo montañas pero no árboles. Tengo agua pero no peces. ¿Qué soy?",
        "Estás participando en una carrera. De repente, adelantas a la persona que va en segundo lugar. ¿En qué posición te encuentras ahora?",
        "La madre de María tiene cuatro hijas. Sus nombres son Abril, Mayo, Junio y... ¿cuál es el nombre de la cuarta hija?",
        "Si me tienes, quieres compartirme. Si me compartes, ya no me tienes. ¿Qué soy?"
    ]

    print("="*80)
    print("🧠 INICIANDO TORNEO DE ACERTIJOS Y LÓGICA (LIVE STREAM) 🧠")
    print("="*80)
    print(f"Modelos combatientes: {', '.join(modelos_finales)}")
    print(f"Número de pruebas por modelo: {len(prompts_acertijos)}\n")
    
    for modelo in modelos_finales:
        print(f"\n\n{'*'*80}")
        print(f"🥊 CARGANDO MODELO: {modelo}")
        print(f"{'*'*80}")
        
        # Llamamos a ejecutar_bateria, que ya se encarga de mostrar la respuesta en directo (stream),
        # medir los tiempos, e ir guardando todo en SQLite.
        ejecutar_bateria(prompts_acertijos, mod_thinking_activado=False, modelo_archivo=modelo)

    print("\n✅ TORNEO EXHAUSTIVO COMPLETADO.")
    print("Puedes revisar los resultados en la base de datos o en el log de la terminal.")

if __name__ == "__main__":
    main()
