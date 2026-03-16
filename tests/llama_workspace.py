import subprocess
import time
import sys
import json
import os
import sqlite3
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

# Crear la carpeta workspace si no existe
os.makedirs(WORKSPACE_DIR, exist_ok=True)

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

SYSTEM_PROMPT = """Eres un Asistente de Inteligencia Artificial Avanzado operando en un entorno de trabajo restringido y altamente especializado.
Tienes a tu disposición un directorio exclusivo llamado 'workspace' (donde tienes permiso total).

REGLAS DE SEGURIDAD ESTRICTAS A OBEDECER:
1. DENTRO DE 'workspace': Tienes permiso total. Puedes crear, editar y gestionar archivos como desees.
2. FUERA DE 'workspace': Tienes estrictamente PERMISO DE SOLO LECTURA. No debes borrar, alterar ni sobrescribir archivos del sistema anfitrión. 
3. COMANDOS GLOBALES: Tienes permiso para instalar programas (ej. `pip install`) y lanzar comandos de entorno, pero NUNCA debes usar comandos shell destructivos (como del, rm, rd) fuera del workspace.

Para operar, DEBES usar el formato XML estricto con las siguientes herramientas:

<tools>
{"type": "function", "function": {"name": "ejecutar_comando", "description": "Ejecuta un comando en la terminal. El directorio de trabajo (CWD) base será el workspace.", "parameters": {"type": "object", "properties": {"comando": {"type": "string"}}}, "required": ["comando"]}}
{"type": "function", "function": {"name": "leer_archivo", "description": "Lee contenido de un archivo en cualquier ruta de C:/ o del sistema.", "parameters": {"type": "object", "properties": {"ruta_absoluta": {"type": "string"}}}, "required": ["ruta_absoluta"]}}
{"type": "function", "function": {"name": "escribir_archivo", "description": "Guarda o sobrescribe un archivo automáticamente DENTRO de workspace.", "parameters": {"type": "object", "properties": {"nombre_relativo": {"type": "string", "description": "Nombre de archivo, ej: mi_script.py"}, "contenido": {"type": "string", "description": "Código o texto a inyectar"}}}, "required": ["nombre_relativo", "contenido"]}}
</tools>

Ejemplo de uso correcto:
"Claro, voy a leer el archivo de tu sistema:"
<tool_call>
{"name": "leer_archivo", "arguments": {"ruta_absoluta": "C:/Usuarios/ejemplo.txt"}}
</tool_call>

Instrucciones:
- Emite una etiqueta <tool_call> con JSON válido por turno SOLAMENTE cuando necesites hacer algo en el sistema a petición del usuario.
- ⛔ REGLA CRÍTICA: ABSOLUTAMENTE PROHIBIDO usar herramientas (tool_call) si el usuario solo te saluda (ej: "hola", "buenos días"), hace una pregunta trivial verbal, o conversan. SOLO lanza herramientas cuando te ordenen acciones sobre el sistema directamente. Tu rol principal también es charlar pacíficamente.
- Pausa tu generación cuando lances una petición: el usuario y Python te devolverán el resultado analizado en <tool_response> y tú continuarás a partir de ahí."""

def init_db():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect('db/llama_history_workspace.db')
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
        "-c", "8192", # Contexto amplio para tolerar tool_responses de logs largos
        "-ngl", "99",
        "--port", str(PUERTO),
        "--chat-template-kwargs", kwargs
    ]
    
    estado = "ACTIVADO" if thinking else "DESACTIVADO"
    print(f"\n[+] Iniciando llama-server WORKSPACE (Modelo: {modelo} | Thinking: {estado})...")
    servidor_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import urllib.request
    print("    [!] Esperando a que el modelo cargue en memoria...")
    max_intentos = 120
    for i in range(max_intentos):
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

    print(f"[+] Servidor en línea. Area de Trabajo anclada en: {WORKSPACE_DIR}\n")

def detener_servidor():
    global servidor_process
    if servidor_process is not None:
        print("\n[-] Apagando el servidor...")
        servidor_process.terminate()
        servidor_process.wait()
        servidor_process = None

def imprimir_ayuda():
    print("\n" + "="*50)
    print("🤖 CHAT AREA WORKSPACE (CON HERRAMIENTAS SEGREGADAS)")
    print("="*50)
    print("Comandos disponibles:")
    print("  /modo think    -> Reinicia el servidor CON modo de pensamiento")
    print("  /modo nothink  -> Reinicia el servidor SIN modo de pensamiento")
    print("  /modelo        -> Muestra la lista y permite cambiar de modelo GGUF")
    print("  /limpiar       -> Borra el historial de la conversación")
    print("  /salir         -> Apaga el servidor y cierra el programa")
    print("="*50 + "\n")

def procesar_herramienta(respuesta_completa, historial_chat):
    """Busca tool_calls, analiza la función que usa y protege las fronteras de carpetas."""
    match = re.search(r'<tool_call>\s*({.*?})\s*</tool_call>', respuesta_completa, re.DOTALL)
    
    if not match:
        return False # No hubo llamada a herramienta

    json_str = match.group(1)
    try:
        tool_data = json.loads(json_str)
        nombre_herramienta = tool_data.get("name")
        args = tool_data.get("arguments", {})
        
        salida_herramienta = ""

        # ------------- HERRAMIENTA 1: EJECUTAR COMANDO -------------
        if nombre_herramienta == "ejecutar_comando":
            comando = args.get("comando", "")
            if not comando: raise ValueError("Comando vacío")
            
            print(f"\n\n\033[1;33m[⚠️ ATENCIÓN] El modelo solicita ejecutar un comando (CWD = workspace):\033[0m")
            print(f"\033[93m> {comando}\033[0m")
            confirmacion = input("\033[91m¿Permitir ejecución? (S/N):\033[0m ").strip().lower()
            
            if confirmacion == 's':
                print("[*] Ejecutando comando dentro de tu workspace...")
                try:
                    resultado = subprocess.run(
                        comando, 
                        shell=True, capture_output=True, text=True, timeout=30,
                        cwd=WORKSPACE_DIR # Enjaulado por defecto en esta carpeta
                    )
                    salida_herramienta = resultado.stdout if resultado.returncode == 0 else resultado.stderr
                    if not salida_herramienta.strip():
                        salida_herramienta = "[Comando ejecutado con éxito. Sin salida visible en consola.]"
                    
                    if len(salida_herramienta) > 2500:
                        salida_herramienta = salida_herramienta[:2500] + "\n...[ALERTA: Salida truncada por límite de buffer]..."
                except subprocess.TimeoutExpired:
                    salida_herramienta = "[Error: Comando abortado por exceder límite de tiempo]"
                except Exception as e:
                    salida_herramienta = f"[Error al ejecutar shell: {e}]"
            else:
                salida_herramienta = "[Error: El humano ha rechazado la ejecución por motivos de seguridad]"
                print("\033[91m[!] Denegado.\033[0m")

        # ------------- HERRAMIENTA 2: LEER ARCHIVO -------------
        elif nombre_herramienta == "leer_archivo":
            ruta_absoluta = args.get("ruta_absoluta", "")
            print(f"\n\n\033[1;34m[📚 LECTURA LÍCITA] El modelo va a leer un archivo:\033[0m")
            print(f"\033[94m> {ruta_absoluta}\033[0m")
            
            try:
                if not os.path.exists(ruta_absoluta):
                    salida_herramienta = f"[Error: El archivo {ruta_absoluta} no existe]"
                else:
                    with open(ruta_absoluta, 'r', encoding='utf-8', errors='ignore') as f:
                        contenido = f.read()
                    if len(contenido) > 3000:
                        contenido = contenido[:3000] + "\n...[ALERTA: Archivo truncado por ser excesivamente grande]..."
                    salida_herramienta = f"[Contenido del archivo]\n{contenido}"
            except Exception as e:
                salida_herramienta = f"[Error al intentar leer: {e}]"

        # ------------- HERRAMIENTA 3: ESCRIBIR ARCHIVO -------------
        elif nombre_herramienta == "escribir_archivo":
            nombre_relativo = args.get("nombre_relativo", "")
            contenido = args.get("contenido", "")
            
            # Blindaje vital: Convertir a ruta absoluta usando WORKSPACE_DIR y asegurar que no haya ../ maliciously insertado
            ruta_objetivo = os.path.abspath(os.path.join(WORKSPACE_DIR, nombre_relativo))
            
            if not ruta_objetivo.startswith(WORKSPACE_DIR):
                salida_herramienta = "[! ERROR CRÍTICO AL MODELO: TU RUTA ESCAPABA DE workspace. ABORTADO POR MOTIVOS DE SEGURIDAD. COMPÓRTATE.]"
                print(f"\n\033[91m[!] ALERTA INTRUSIÓN: El modelo intentó escapar de la jaula escribiendo en {ruta_objetivo}\033[0m")
            else:
                print(f"\n\n\033[1;32m[📝 ESCRITURA EN ESPACIO SEGURO] El modelo quiere crear/modificar el archivo:\033[0m")
                print(f"\033[92m> {ruta_objetivo}\033[0m")
                confirmacion = input("\033[91m¿Permitir guardado? (S/N):\033[0m ").strip().lower()
                
                if confirmacion == 's':
                    try:
                        os.makedirs(os.path.dirname(ruta_objetivo), exist_ok=True)
                        with open(ruta_objetivo, 'w', encoding='utf-8') as f:
                            f.write(contenido)
                        salida_herramienta = f"[Éxito: Archivo {nombre_relativo} guardado en tu workspace]"
                        print("[+] Guardado con éxito.")
                    except Exception as e:
                        salida_herramienta = f"[Error grave en la escritura de disco: {e}]"
                else:
                    salida_herramienta = "[El usuario ha rechazado guardar el archivo.]"
                    print("\033[91m[!] Denegado.\033[0m")

        else:
            salida_herramienta = f"[Error: La herramienta {nombre_herramienta} no existe. Usa solo ejecutar_comando, leer_archivo o escribir_archivo.]"

        # DEVOLUCIÓN DE LA TOOL RESPONSE AL MODELO
        print(f"\n\033[90m(Devolviendo datos al modelo de contexto...)\033[0m\n")
        codigo_respuesta = f"<tool_response>\n{salida_herramienta}\n</tool_response>"
        historial_chat.append({"role": "user", "content": codigo_respuesta})
        return True
                
    except json.JSONDecodeError:
        print("\n\033[91m[!] El modelo generó un JSON de tool alucinado o malformado.\033[0m")
        codigo_respuesta = f"<tool_response>\n[Error: Formato JSON inválido. Reestructura e inténtalo de nuevo]\n</tool_response>"
        historial_chat.append({"role": "user", "content": codigo_respuesta})
        return True
    except Exception as e:
        print(f"\n\033[91m[!] Error al procesar lógica Python: {e}\033[0m")
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
                if not modo_thinking_actual:
                    modo_thinking_actual = True
                    iniciar_servidor(thinking=True)
                    cliente = OpenAI(base_url=URL_BASE, api_key="local")
                else:
                    print("[!] El modo thinking ya está activado.")
                continue
            elif comando == "/modo nothink":
                if modo_thinking_actual:
                    modo_thinking_actual = False
                    iniciar_servidor(thinking=False)
                    cliente = OpenAI(base_url=URL_BASE, api_key="local")
                else:
                    print("[!] El modo thinking ya está desactivado.")
                continue
            elif comando == "/modelo":
                print("\n[+] Modelos disponibles en /models:")
                for i, m in enumerate(MODELOS_DISPONIBLES):
                    prefix = "📍" if m == modelo_actual else "  "
                    print(f"{prefix} {i+1}. {m}")
                    
                sel = input("\nElige número (o Intro para cancelar): ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(MODELOS_DISPONIBLES):
                    modelo_nuevo = MODELOS_DISPONIBLES[int(sel)-1]
                    if modelo_nuevo != modelo_actual:
                        modelo_actual = modelo_nuevo
                        iniciar_servidor(thinking=modo_thinking_actual, modelo=modelo_actual)
                        cliente = OpenAI(base_url=URL_BASE, api_key="local")
                    else:
                        print("[!] Ya estás usando este modelo.")
                continue

            historial_chat.append({"role": "user", "content": usuario})
            log_message(conn, 'user', usuario, session_id=current_session_id)
            
            requiere_respuesta = True
            
            while requiere_respuesta:
                print("\033[96mAsistente:\033[0m ", end="", flush=True)
                
                try:
                    t0 = time.time()
                    t_first_token = None
                    think_token_count = 0
                    speak_token_count = 0
                    
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
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                            think_token_count += 1
                            print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)
                            pensamiento_completo += delta.reasoning_content
                            
                        elif hasattr(delta, 'content') and delta.content is not None:
                            if not empezo_respuesta_final and pensamiento_completo != "":
                                print("\n\n\033[92m[Respuesta Final:]\033[0m\n", end="")
                                empezo_respuesta_final = True
                                
                            speak_token_count += 1
                            print(delta.content, end="", flush=True)
                            respuesta_completa += delta.content
                            
                    print("\n")
                    ttft = (t_first_token - t0) if t_first_token else 0.0
                    
                    historial_chat.append({"role": "assistant", "content": respuesta_completa})
                    log_message(conn, 'assistant', respuesta_completa, thoughts=pensamiento_completo,
                                model=modelo_actual, ttft=ttft, session_id=current_session_id)
                                
                    tuvo_herramienta = procesar_herramienta(respuesta_completa, historial_chat)
                    
                    if tuvo_herramienta:
                        ultimo_mensaje_user = historial_chat[-1]["content"]
                        log_message(conn, 'user', ultimo_mensaje_user, session_id=current_session_id)
                        requiere_respuesta = True
                    else:
                        requiere_respuesta = False
                    
                except Exception as e:
                    print(f"\n[!] Error: {e}")
                    if len(historial_chat) > 0 and historial_chat[-1]["role"] == "user":
                        historial_chat.pop()
                    requiere_respuesta = False
                    
    except KeyboardInterrupt:
        print("\n[!] Interrupción detectada.")
    finally:
        detener_servidor()
        if 'conn' in locals():
            conn.close()
        print("¡Adiós!")

if __name__ == "__main__":
    main()
