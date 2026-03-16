import subprocess
import time
import sys
import json
import os
import re
from datetime import datetime
from openai import OpenAI

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_MODELOS = os.path.join(BASE_DIR, "models")
RUTA_LLAMA_SERVER = os.path.join(BASE_DIR, "llama-b8352-bin-win-cuda-12.4-x64", "llama-server.exe")
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
PUERTO = 8080
URL_BASE = f"http://127.0.0.1:{PUERTO}/v1"

os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(CARPETA_MODELOS, exist_ok=True)
MODELOS_DISPONIBLES = [f for f in os.listdir(CARPETA_MODELOS) if f.endswith(".gguf")]

if not MODELOS_DISPONIBLES:
    print(f"❌ Error: No se encontraron modelos .gguf en {CARPETA_MODELOS}")
    sys.exit(1)

servidor_process = None
modelo_actual = MODELOS_DISPONIBLES[-1]

SYSTEM_PROMPT = """Eres el Arquitecto de una Fábrica de Software Python Autónoma.
Tu misión principal es inventar y programar scripts de Python útiles, creativos, variados y funcionales.

REGLAS E INSTRUCCIONES ESTRICTAS:
1. Lee atentamente el historial de proyectos que el usuario te proporcionará para evitar crear programas redundantes o similares.
2. Extrae el número de ID correspondiente al siguiente script a fabricar en base a cuántos hay en el historial.
3. Para operar, DEBES usar el formato XML estricto con la herramienta artificial "crear_proyecto_python".
4. Escribe código modular, robusto, y si es posible, con comentarios.
5. NO respondas con texto fuera de las etiquetas <tool_call> para no malgastar el tiempo de CPU y ser rápido.

<tools>
{"type": "function", "function": {"name": "crear_proyecto_python", "description": "Fabrica físicamente el proyecto en disco", "parameters": {"type": "object", "properties": {"id_nombre_carpeta": {"type": "string", "description": "Nombre de la carpeta, por ejemplo: 1_calculadora, 2_ahorcado, 3_webscraper"}, "codigo_main": {"type": "string", "description": "El código fuente de main.py completo"}, "contenido_readme": {"type": "string", "description": "Un documento explicativo MD sobre qué hace el programa, cómo correrlo y qué dependencias tiene"}, "descripcion_corta": {"type": "string", "description": "Resumen de 1 o 2 líneas para el archivo maestro de historial"}}}, "required": ["id_nombre_carpeta", "codigo_main", "contenido_readme", "descripcion_corta"]}}
</tools>

Uso Obligatorio:
<tool_call>
{"name": "crear_proyecto_python", "arguments": {"id_nombre_carpeta": "X_nombre_proyecto", "codigo_main": "def main():...", "contenido_readme": "# Nombre\\n...", "descripcion_corta": "Breve descripción..."}}
</tool_call>
"""

def iniciar_servidor(thinking=True):
    global servidor_process
    if servidor_process is not None:
        servidor_process.terminate()
        servidor_process.wait()
        
    ruta_modelo_completa = os.path.join(CARPETA_MODELOS, modelo_actual)
    kwargs = json.dumps({"enable_thinking": thinking})
    comando = [
        RUTA_LLAMA_SERVER,
        "-m", ruta_modelo_completa,
        "-c", "8192", 
        "-ngl", "99",
        "--port", str(PUERTO),
        "--chat-template-kwargs", kwargs
    ]
    
    estado = "ACTIVADO" if thinking else "DESACTIVADO"
    print(f"\n[+] Iniciando llama-server FABRICA (Modelo: {modelo_actual} | Thinking: {estado})...")
    servidor_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import urllib.request
    print("    [!] Esperando a que el motor arranque...")
    for i in range(120):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{PUERTO}/health")
            with urllib.request.urlopen(req, timeout=1) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get("status") in ["ok", "ready"]:
                        break
        except Exception:
            pass
        if servidor_process.poll() is not None:
             print("\n❌ Error: El proceso colapsó.")
             sys.exit(1)
        time.sleep(1)
    else:
        print("\n❌ Error: Timeout al arrancar.")
        sys.exit(1)
    print(f"[+] Fábrica online.\n")

def detener_servidor():
    global servidor_process
    if servidor_process is not None:
        print("\n[-] Apagando el servidor...")
        servidor_process.terminate()
        servidor_process.wait()

def main():
    iniciar_servidor(thinking=False) # Se puede cambiar a True si prefieres que la fábrica "piense" largo rato
    cliente = OpenAI(base_url=URL_BASE, api_key="local")
    
    base_scripts = os.path.join(WORKSPACE_DIR, "scripts_python")
    os.makedirs(base_scripts, exist_ok=True)
    historial_file = os.path.join(base_scripts, "scripts_historial.txt")
    
    print("\n" + "="*50)
    print("🏭 FÁBRICA DE SCRIPTS AUTÓNOMA")
    print("="*50)
    print(f"Directorio de Salida: {base_scripts}")
    print("="*50 + "\n")

    try:
        while True:
            val = input("\n\033[93m¿Cuántos scripts distintos quieres crear en esta tanda? (Ingresa número o 0 para salir): \033[0m").strip()
            if not val.isdigit() or int(val) <= 0:
                print("Finalizando ejecución.")
                break
                
            num_scripts = int(val)
            
            for iteracion in range(num_scripts):
                # Leer historial dinámicamente en cada ciclo
                if not os.path.exists(historial_file):
                    with open(historial_file, 'w', encoding='utf-8') as f:
                        f.write("=== HISTORIAL DE PROGRAMAS CREADOS ===\n")
                
                with open(historial_file, 'r', encoding='utf-8') as f:
                    historial_actual = f.read()

                print(f"\n\033[96m[➔] Iniciando producción: Script {iteracion + 1} de {num_scripts}...\033[0m")
                
                # Reseteamos el historial de chat para evitar el límite de 8192 tokens y acelerar la inferencia!
                user_prompt = f"Inicia la producción. Aquí tienes el inventario actual de scripts_historial.txt. Inventa un programa NUEVO basándote en que no se repita con este listado u otorga el ID '1_' si la lista está vacía:\n\n{historial_actual}\n\nRECUERDA: Excluye charlas triviales, responde usando la estructura <tool_call> estrictamente."
                chat_fabricacion = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
                
                try:
                    stream = cliente.chat.completions.create(
                        model="qwen-local",
                        messages=chat_fabricacion,
                        temperature=0.7,
                        stream=True
                    )
                    
                    respuesta_completa = ""
                    for chunk in stream:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                            print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)
                        elif hasattr(delta, 'content') and delta.content:
                            # Hacemos printeo gris para no molestar mucho al usuario
                            print(f"\033[90m{delta.content}\033[0m", end="", flush=True)
                            respuesta_completa += delta.content

                    print("\n")
                    # Parsear la herramienta
                    match = re.search(r'<tool_call>\s*({.*?})\s*</tool_call>', respuesta_completa, re.DOTALL)
                    if match:
                        raw_json_str = match.group(1)
                        
                        # Limpieza intensiva de caracteres de control ilegales en JSON generados por el modelo (saltos de línea reales en crudo)
                        # Reemplazamos saltos literales por escapados \\n, tabulaciones por \\t, etc.
                        clean_json_str = re.sub(r'(?<!\\)\n', r'\\n', raw_json_str) 
                        clean_json_str = re.sub(r'(?<!\\)\r', r'\\r', clean_json_str)
                        clean_json_str = re.sub(r'(?<!\\)\t', r'\\t', clean_json_str)
                        
                        try:
                            # A veces re.sub introduce dobles escapes accidentales si el LLM sí escapó algunas cosas pero no otras
                            # Intentamos cargar el original y si falla intentamos con el parseado.
                            try:
                                data = json.loads(raw_json_str, strict=False)
                            except json.JSONDecodeError:
                                data = json.loads(clean_json_str, strict=False)
                                
                            args = data.get("arguments", {})
                            
                            id_nombre = args.get("id_nombre_carpeta", f"desc_{int(time.time())}").replace(" ", "_").replace("/", "_")
                            codigo_main = args.get("codigo_main", "")
                            contenido_readme = args.get("contenido_readme", "")
                            descripcion_corta = args.get("descripcion_corta", "Sin descripción")
                            
                            proyecto_dir = os.path.join(base_scripts, id_nombre)
                            os.makedirs(proyecto_dir, exist_ok=True)
                            
                            with open(os.path.join(proyecto_dir, "main.py"), "w", encoding='utf-8') as f:
                                f.write(codigo_main)
                            
                            with open(os.path.join(proyecto_dir, "README.md"), "w", encoding='utf-8') as f:
                                f.write(contenido_readme)
                            
                            with open(historial_file, "a", encoding='utf-8') as f:
                                f.write(f"- {id_nombre} : {descripcion_corta}\n")
                            
                            print(f"\033[92m[✅ ÉXITO] El proyecto '{id_nombre}' fue creado y registrado.\033[0m")
                            
                        except json.JSONDecodeError as je:
                            print(f"\033[91m[❌ ERROR] El modelo generó un JSON irrecuperable de parsear: {je}. Saltando al siguiente...\033[0m")
                    else:
                        print(f"\033[91m[❌ ERROR] El modelo falló al estructurar la petición <tool_call>. Saltando al siguiente...\033[0m")
                        
                except Exception as e:
                    print(f"\n[!] Error en el ciclo de producción: {e}")
                    
    except KeyboardInterrupt:
        print("\n[!] Fabrica detenida manualmente.")
    finally:
        detener_servidor()

if __name__ == "__main__":
    main()
