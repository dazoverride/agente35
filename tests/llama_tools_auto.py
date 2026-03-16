import subprocess
import time
import sys
import json
import os
import sqlite3
import re
import tempfile
from datetime import datetime
from openai import OpenAI

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_MODELOS = os.path.join(BASE_DIR, "models")
RUTA_LLAMA_SERVER = os.path.join(BASE_DIR, "llama-b8352-bin-win-cuda-12.4-x64", "llama-server.exe")
PUERTO = 8080
URL_BASE = f"http://127.0.0.1:{PUERTO}/v1"

# Obtener modelos disponibles
os.makedirs(CARPETA_MODELOS, exist_ok=True)
MODELOS_DISPONIBLES = [f for f in os.listdir(CARPETA_MODELOS) if f.endswith(".gguf")]
if not MODELOS_DISPONIBLES:
    print(f"❌ Error: No se encontraron modelos .gguf en {CARPETA_MODELOS}")
    sys.exit(1)

# Variables globales
servidor_process = None
modo_thinking_actual = False
modelo_actual = MODELOS_DISPONIBLES[-1] # Por defecto usa el último en la lista
historial_chat = []

SYSTEM_PROMPT = """Eres un asistente de Inteligencia Artificial avanzado con capacidades de ejecutar acciones en el sistema del usuario (Windows).
Si necesitas realizar una acción o automatización compleja en nombre del usuario, DEBES usar el siguiente formato XML estricto:

<tool_call>
{"name": "NOMBRE_HERRAMIENTA", "arguments": {"param1": "valor1"}}
</tool_call>

Tienes las siguientes herramientas pre-hechas a tu disposición:
<tools>
[
  {
    "type": "function", "function": {
      "name": "ejecutar_comando_sistema", 
      "description": "Ejecuta un comando en la terminal CMD/PowerShell de Windows.", 
      "parameters": {"type": "object", "properties": {"comando": {"type": "string"}}}, 
      "required": ["comando"]
    }
  },
  {
    "type": "function", "function": {
      "name": "crear_script_python", 
      "description": "Crea y guarda un script de Python reutilizable en tu carpeta permanente 'workspace/scripts_auto' y lo ejecuta al instante devolviendo su salida. IMPORTANTE: DEBEN ser genéricos. No pongas valores fijos en el código (ej. no pongas c = 5 + 5). Usa siempre sys.argv o argparse para atrapar variables dinámicas desde la consola, para que el script ('ej: sumar_numeros.py') se quede guardado y puedas usarlo mil veces después cambiándole los argumentos.", 
      "parameters": {"type": "object", "properties": {"nombre_script": {"type": "string", "description": "Nombre con el que se guardará el script en disco, ej: sumar_numeros.py"}, "script_code": {"type": "string", "description": "El código fuente en python completo. DEBE estar parametrizado y leer sys.argv. Usar print() al final para escupir la salida."}, "argumentos_iniciales": {"type": "string", "description": "Los argumentos separados por espacios para esta primera ejecución inmediata del script (opcional)."}}}, 
      "required": ["nombre_script", "script_code"]
    }
  },
  {
    "type": "function", "function": {
      "name": "ejecutar_script_guardado", 
      "description": "Ejecuta un script de Python que tú u otro modelo haya creado anteriormente y que esté guardado en la carpeta 'workspace/scripts_auto'. Ideal para reutilizar herramientas genéricas leyendo sys.argv.", 
      "parameters": {"type": "object", "properties": {"nombre_script": {"type": "string", "description": "Nombre del archivo a ejecutar, ej: sumar_numeros.py"}, "argumentos": {"type": "string", "description": "Nuevos argumentos CLI separados por espacios pasados a tu script ya guardado (opcional)."}}}, 
      "required": ["nombre_script"]
    }
  },
  {
    "type": "function", "function": {
      "name": "escribir_archivo", 
      "description": "Crea o sobrescribe un archivo en el disco con un texto concreto.", 
      "parameters": {"type": "object", "properties": {"ruta_archivo": {"type": "string"}, "contenido": {"type": "string"}}}, 
      "required": ["ruta_archivo", "contenido"]
    }
  },
  {
    "type": "function", "function": {
      "name": "leer_archivo", 
      "description": "Devuelve el texto contenido de un archivo en el disco del usuario.", 
      "parameters": {"type": "object", "properties": {"ruta_archivo": {"type": "string", "description": "Debe ser al menos una ruta relativa o absoluta."}}}, 
      "required": ["ruta_archivo"]
    }
  }
]
</tools>

Instrucciones de Uso:
1. Explica en lenguaje humano natural lo que vas a hacer y piensa si ya creaste un script para esto antes. Si ya lo tienes, llama a 'ejecutar_script_guardado' en vez de crear uno nuevo.
2. Emite SIEMPRE una sola etiqueta <tool_call> con tu petición estructurada en JSON.
3. Espera silenciosamente a que se te reinyecte la etiqueta <tool_response>.
4. IMPORTANTE: En 'crear_script_python', nunca dejes la lógica final hardcodeada. Programa herramientas genéricas modulares.
"""

def init_db():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect('db/llama_history_tools_auto.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            thoughts TEXT,
            model TEXT,
            system_prompt TEXT,
            think_tokens INTEGER,
            speak_tokens INTEGER,
            total_tokens INTEGER,
            ttft REAL,
            session_id TEXT
        )
    ''')
    conn.commit()
    return conn

def log_message(conn, role, content, thoughts="", model="", system_prompt="", 
                think_tokens=0, speak_tokens=0, total_tokens=0, 
                ttft=0.0, session_id=""):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (
            role, content, thoughts, model, system_prompt,
            think_tokens, speak_tokens, total_tokens,
            ttft, session_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (role, content, thoughts, model, system_prompt, 
          think_tokens, speak_tokens, total_tokens, ttft, session_id))
    conn.commit()

def iniciar_servidor(thinking=False, modelo=None):
    global servidor_process, modelo_actual
    detener_servidor()
    
    if modelo is None:
        modelo = modelo_actual
        
    ruta_modelo_completa = os.path.join(CARPETA_MODELOS, modelo)
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
    print(f"\n[+] Iniciando llama-server TOOLS-AUTO MUTLITAREA (Modelo: {modelo} | Thinking: {estado})...")
    servidor_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import urllib.request
    print("    [!] Esperando a que el modelo cargue en memoria...")
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
             print("\n❌ Error: El proceso de llama-server ha colapsado.")
             sys.exit(1)
        time.sleep(1)
    else:
        print("\n❌ Error: Tiempo de espera agotado al cargar el modelo.")
        sys.exit(1)

    print("[+] Servidor Multi-Tool online. ¡Listo para interactuar!\n")

def detener_servidor():
    global servidor_process
    if servidor_process is not None:
        print("\n[-] Apagando el servidor...")
        servidor_process.terminate()
        servidor_process.wait()
        servidor_process = None

def imprimir_ayuda():
    print("\n" + "="*60)
    print("🤖 CHAT INTERACTIVO AUTO-TOOLS (MULTI-FUNCIONES AUTÓNOMAS)")
    print("="*60)
    print("El modelo ahora tiene capacidad para usar 4 herramientas simultáneas:")
    print(" - CMD System")
    print(" - Python Script Coder & Executor (Persistent in workspace/)")
    print(" - Saved Script Executor (Reusability)")
    print(" - File Writer")
    print(" - File Reader")
    print("Comandos disponibles:")
    print("  /modo think    -> Activa razonamiento")
    print("  /modo nothink  -> Desactiva razonamiento")
    print("  /modelo        -> Cambiar GGUF")
    print("  /salir         -> Cerrar programa")
    print("="*60 + "\n")

def procesar_herramienta(respuesta_completa, historial_chat):
    """Busca tool_calls en la respuesta y enruta a la herramienta Python adecuada con Autorización HITL."""
    match = re.search(r'<tool_call>\s*({.*?})\s*</tool_call>', respuesta_completa, re.DOTALL)
    
    if not match:
        return False

    raw_json_str = match.group(1)
    # Limpieza JSON de seguridad por alucinaciones XML del LLM
    clean_json_str = re.sub(r'(?<!\\)\n', r'\\n', raw_json_str) 
    clean_json_str = re.sub(r'(?<!\\)\r', r'\\r', clean_json_str)
    clean_json_str = re.sub(r'(?<!\\)\t', r'\\t', clean_json_str)
    
    try:
        try:
             tool_data = json.loads(raw_json_str, strict=False)
        except json.JSONDecodeError:
             tool_data = json.loads(clean_json_str, strict=False)
             
        tool_name = tool_data.get("name")
        args = tool_data.get("arguments", {})
        
        print(f"\n\n\033[1;33m[🛡️ SISTEMA MULTI-HERRAMIENTAS] Petición entrante de la IA:\033[0m")
        print(f"\033[93m> Herramienta a Usar: {tool_name}\033[0m")
        
        # Enseñar preview de seguridad de la petición
        if tool_name == "ejecutar_comando_sistema":
             print(f"\033[35m  Comando:\033[0m {args.get('comando', '')}")
        elif tool_name == "crear_script_python":
             print(f"\033[35m  Nombre :\033[0m {args.get('nombre_script', 'script_temp.py')}")
             if "argumentos_iniciales" in args:
                  print(f"\033[35m  Args   :\033[0m {args['argumentos_iniciales']}")
             print(f"\033[35m  Código:\033[0m\n{args.get('script_code', '')}")
        elif tool_name == "ejecutar_script_guardado":
             print(f"\033[35m  Script:\033[0m {args.get('nombre_script', '')}")
             print(f"\033[35m  Args  :\033[0m {args.get('argumentos', '')}")
        elif tool_name == "escribir_archivo":
             print(f"\033[35m  Ruta :\033[0m {args.get('ruta_archivo', '')}")
             print(f"\033[35m  Bytes:\033[0m {len(args.get('contenido', ''))} caracteres")
        elif tool_name == "leer_archivo":
             print(f"\033[35m  Ruta :\033[0m {args.get('ruta_archivo', '')}")

        # Human in the Loop (HITL)
        confirmacion = input("\n\033[91m¿Permitir ejecución de esta herramienta? (S/N/auto):\033[0m ").strip().lower()
        
        if confirmacion in ['s', 'auto', '']:
            print("[*] Ejecutando puente...\n")
            salida = ""
            
            # --- RUTEO DE LA PETICIÓN AL MÓDULO CORRESPONDIENTE ---
            try:
                WORKSPACE_AUTO = os.path.join(BASE_DIR, "workspace", "scripts_auto")
                os.makedirs(WORKSPACE_AUTO, exist_ok=True)
                
                if tool_name == "ejecutar_comando_sistema":
                    comando = args.get("comando", "")
                    resultado = subprocess.run(
                        comando, shell=True, capture_output=True, text=True, timeout=30, cwd=BASE_DIR
                    )
                    salida = resultado.stdout if resultado.returncode == 0 else resultado.stderr
                    
                elif tool_name == "crear_script_python":
                    codigo = args.get("script_code", "")
                    nombre_script = args.get("nombre_script", f"script_{int(time.time())}.py")
                    if not nombre_script.endswith(".py"): nombre_script += ".py"
                    argumentos_iniciales = args.get("argumentos_iniciales", "")
                    
                    # Escribimos el script del LLM permanentemente en workspace/scripts_auto
                    ruta_script = os.path.join(WORKSPACE_AUTO, nombre_script)
                    with open(ruta_script, 'w', encoding='utf-8') as f:
                        f.write(codigo)
                        
                    cmd = [sys.executable, ruta_script]
                    if argumentos_iniciales:
                        import shlex
                        cmd.extend(shlex.split(argumentos_iniciales))
                        
                    resultado = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=60, cwd=BASE_DIR
                    )
                    salida = f"[Script guardado con éxito en: {ruta_script}]\n\n--- Salida del script ---\n" + (resultado.stdout if resultado.returncode == 0 else resultado.stderr)
                    
                elif tool_name == "ejecutar_script_guardado":
                    nombre_script = args.get("nombre_script", "")
                    argumentos = args.get("argumentos", "")
                    if not nombre_script.endswith(".py"): nombre_script += ".py"
                    ruta_script = os.path.join(WORKSPACE_AUTO, nombre_script)
                    
                    if not os.path.exists(ruta_script):
                        salida = f"[Error Crítico del Sistema: El script '{nombre_script}' NO EXISTE en la carpeta '{WORKSPACE_AUTO}'. Debes crearlo primero usando 'crear_script_python' o usar otro nombre.]"
                    else:
                        cmd = [sys.executable, ruta_script]
                        if argumentos:
                            import shlex
                            cmd.extend(shlex.split(argumentos))
                            
                        resultado = subprocess.run(
                            cmd, capture_output=True, text=True, timeout=60, cwd=BASE_DIR
                        )
                        salida = resultado.stdout if resultado.returncode == 0 else resultado.stderr
                    
                elif tool_name == "leer_archivo":
                    ruta = args.get("ruta_archivo", "")
                    with open(ruta, "r", encoding='utf-8') as f:
                        salida = f.read()
                        
                elif tool_name == "escribir_archivo":
                    ruta = args.get("ruta_archivo", "")
                    contenido = args.get("contenido", "")
                    with open(ruta, "w", encoding='utf-8') as f:
                        f.write(contenido)
                    salida = f"¡Éxito! El archivo '{ruta}' se guardó exitosamente."
                    
                else:
                    salida = f"[Error Crítico del Sistema: La Herramienta '{tool_name}' no existe en la base de datos de python.]"
                
                if not salida.strip():
                    salida = "[Herramienta procesada correctamente. Salida estándar vacía.]"
                
                # Truncar la devolución para evitar saturar el LLM Memory
                if len(salida) > 4000:
                    salida = salida[:4000] + "\n\n...[SISTEMA INTERNO: Salida truncada por ser excesivamente grande]..."
                    
            except subprocess.TimeoutExpired:
                 salida = "[Error del Sistema: Tiempo límite (timeout) de la herramienta excedido. Ejecución abortada.]"
            except Exception as e:
                 salida = f"[Error del Sistema empacando la acción: {e}]"
            
            print(f"\033[90m{salida}\033[0m\n")
            historial_chat.append({"role": "user", "content": f"<tool_response>\n{salida}\n</tool_response>"})
            return True
            
        else:
            print("\033[91m[!] Denegado manualmente en nombre de Qwen.\033[0m")
            historial_chat.append({"role": "user", "content": "<tool_response>\n[Error: El Administrador Humano de la terminal ha rechazado y abortado esta acción que ibas a realizar por razones estrictas de seguridad de la red.]\n</tool_response>"})
            return True

    except Exception as e:
        print(f"\n\033[91m[!] Fallo grave al convertir JSON o estructurar el tool loop: {e}\033[0m")
        historial_chat.append({"role": "user", "content": "<tool_response>\n[Error fatal: Format JSON Inválido proveniente de ti. Revisa las comillas y asilamientos.]\n</tool_response>"})
        return True
        
    return False

def main():
    global modo_thinking_actual, historial_chat, modelo_actual
    
    iniciar_servidor(thinking=modo_thinking_actual, modelo=modelo_actual)
    cliente = OpenAI(base_url=URL_BASE, api_key="local")
    
    historial_chat = [{"role": "system", "content": SYSTEM_PROMPT}]
    imprimir_ayuda()

    try:
        current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        conn = init_db()
        
        while True:
            usuario = input("\033[92mTú:\033[0m ")
            if not usuario.strip(): continue
                
            comando = usuario.strip().lower()
            if comando in ["/salir", "/exit", "/quit"]:
                break
            elif comando == "/limpiar":
                historial_chat = [{"role": "system", "content": SYSTEM_PROMPT}]
                current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                print("[!] Historial borrado.")
                continue
            elif comando == "/modo think":
                modo_thinking_actual = True
                iniciar_servidor(thinking=True)
                cliente = OpenAI(base_url=URL_BASE, api_key="local")
                continue
            elif comando == "/modo nothink":
                modo_thinking_actual = False
                iniciar_servidor(thinking=False)
                cliente = OpenAI(base_url=URL_BASE, api_key="local")
                continue
            elif comando == "/modelo":
                for i, m in enumerate(MODELOS_DISPONIBLES):
                    print(f"{'📍' if m == modelo_actual else '  '} {i+1}. {m}")
                sel = input("\nElige número: ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(MODELOS_DISPONIBLES):
                    modelo_actual = MODELOS_DISPONIBLES[int(sel)-1]
                    iniciar_servidor(thinking=modo_thinking_actual, modelo=modelo_actual)
                    cliente = OpenAI(base_url=URL_BASE, api_key="local")
                continue

            historial_chat.append({"role": "user", "content": usuario})
            log_message(conn, 'user', usuario, session_id=current_session_id)
            
            requiere_respuesta = True
            while requiere_respuesta:
                print("\033[96mAsistente MultiTool:\033[0m ", end="", flush=True)
                
                try:
                    t0 = time.time()
                    t_first_token = None
                    stream = cliente.chat.completions.create(
                        model="qwen-local",
                        messages=historial_chat,
                        temperature=0.6,
                        stream=True
                    )
                    
                    respuesta_completa = ""
                    pensamiento_completo = ""
                    empezo_respuesta_final = False
                    
                    for chunk in stream:
                        if t_first_token is None:
                            t_first_token = time.time()
                            
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                            print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)
                            pensamiento_completo += delta.reasoning_content
                            
                        elif hasattr(delta, 'content') and delta.content:
                            if not empezo_respuesta_final and pensamiento_completo != "":
                                print("\n\n\033[92m[🗣️ Final:]\033[0m\n", end="")
                                empezo_respuesta_final = True
                            print(delta.content, end="", flush=True)
                            respuesta_completa += delta.content
                            
                    print("\n")
                    ttft = (t_first_token - t0) if t_first_token else 0.0
                    
                    historial_chat.append({"role": "assistant", "content": respuesta_completa})
                    log_message(conn, 'assistant', respuesta_completa, thoughts=pensamiento_completo,
                                model=modelo_actual, ttft=ttft, session_id=current_session_id)
                                
                    tuvo_herramienta = procesar_herramienta(respuesta_completa, historial_chat)
                    
                    if tuvo_herramienta:
                        log_message(conn, 'user', historial_chat[-1]["content"], session_id=current_session_id)
                        requiere_respuesta = True
                    else:
                        requiere_respuesta = False
                    
                except Exception as e:
                    print(f"\n[!] Error red/conexión: {e}")
                    if len(historial_chat) > 0 and historial_chat[-1]["role"] == "user":
                        historial_chat.pop()
                    requiere_respuesta = False
                    
    except KeyboardInterrupt:
        pass
    finally:
        detener_servidor()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
