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
if os.name == 'nt':
    RUTA_LLAMA_SERVER = os.path.join(BASE_DIR, "llama-b9245-bin-win-cuda-12.4-x64", "llama-server.exe")
else:
    RUTA_LLAMA_SERVER = os.path.join(BASE_DIR, "llama-b9245-bin-ubuntu-x64", "llama-server")
PUERTO = 8085
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
modelo_actual = "google_gemma-4-E2B-it-Q4_K_M.gguf"
historial_chat = []

SYSTEM_PROMPT = """Eres un asistente de Inteligencia Artificial super avanzado y administrador de sistemas.
Tienes acceso al sistema anfitrión mediante una herramienta de shell.
Si el usuario te pide ejecutar un comando o revisar archivos en su máquina, DEBES usar el siguiente formato XML estricto para generar la orden:

<tool_call>
{"name": "ejecutar_comando_sistema", "arguments": {"comando": "dir"}}
</tool_call>

<tools>
{"type": "function", "function": {"name": "ejecutar_comando_sistema", "description": "Ejecuta un comando en la terminal de Windows", "parameters": {"type": "object", "properties": {"comando": {"type": "string"}}}, "required": ["comando"]}}
</tools>

Instrucciones:
1. Explica al humano brevemente lo que vas a hacer.
2. Emite la etiqueta <tool_call> con el JSON válido.
3. Pausa tu generación; recibirás el resultado de la terminal en una etiqueta <tool_response> en el próximo turno.

Solo usa <tool_call> si el usuario te lo solicita implícita o explícitamente y necesitas interaccionar con el PC real."""

def init_db():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect('db/llama_history_tools.db')
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
    print(f"\n[+] Iniciando llama-server TOOLS (Modelo: {modelo} | Thinking: {estado})...")
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

    print("[+] Servidor en línea. ¡Listo para interactuar!\n")

def detener_servidor():
    global servidor_process
    if servidor_process is not None:
        print("\n[-] Apagando el servidor...")
        servidor_process.terminate()
        servidor_process.wait()
        servidor_process = None

def imprimir_ayuda():
    print("\n" + "="*50)
    print("🤖 CHAT INTERACTIVO (CON HERRAMIENTAS)")
    print("="*50)
    print("Comandos disponibles:")
    print("  /modo think    -> Reinicia el servidor CON modo de pensamiento")
    print("  /modo nothink  -> Reinicia el servidor SIN modo de pensamiento")
    print("  /modelo        -> Muestra la lista y permite cambiar de modelo GGUF")
    print("  /limpiar       -> Borra el historial de la conversación")
    print("  /salir         -> Apaga el servidor y cierra el programa")
    print("="*50 + "\n")

def procesar_herramienta(respuesta_completa, historial_chat):
    """Busca tool_calls en la respuesta y ejecuta si el usuario lo permite."""
    # Extraemos el bloque JSON dentro de <tool_call> ... </tool_call>
    match = re.search(r'<tool_call>\s*({.*?})\s*</tool_call>', respuesta_completa, re.DOTALL)
    
    if not match:
        return False # No hubo llamada a herramienta

    json_str = match.group(1)
    try:
        tool_data = json.loads(json_str)
        if tool_data.get("name") == "ejecutar_comando_sistema":
            comando = tool_data.get("arguments", {}).get("comando", "")
            if not comando:
                raise ValueError("JSON de argumentos vacío.")
            
            print(f"\n\n\033[1;33m[⚠️ ATENCIÓN] El modelo solicita ejecutar un comando en tu sistema computacional:\033[0m")
            print(f"\033[93m> {comando}\033[0m")
            
            # Human in the Loop (Confirmación)
            confirmacion = input("\033[91m¿Permitir ejecución? (S/N):\033[0m ").strip().lower()
            
            if confirmacion == 's':
                print("[*] Ejecutando comando...")
                try:
                    # Ejecutamos con shell=True porque en Windows los built-ins (dir, echo) lo requieren
                    resultado = subprocess.run(
                        comando, 
                        shell=True, 
                        capture_output=True, 
                        text=True, 
                        timeout=30,
                        cwd=BASE_DIR
                    )
                    salida = resultado.stdout if resultado.returncode == 0 else resultado.stderr
                    if not salida.strip():
                        salida = "[Comando ejecutado con éxito. Sin salida visible.]"
                    
                    # Asegurar que la salida no exceda el límite de tokens del LLM
                    if len(salida) > 3000:
                        salida = salida[:3000] + "\n\n...[ALERTA: Salida truncada por ser excesivamente larga para el contexto]..."
                except subprocess.TimeoutExpired:
                    salida = "[Error: El comando excedió el tiempo límite y fue abortado.]"
                except Exception as e:
                    salida = f"[Error al ejecutar: {e}]"
                
                print(f"\n\033[90m{salida}\033[0m\n")
                
                codigo_respuesta = f"<tool_response>\n{salida}\n</tool_response>"
                historial_chat.append({"role": "user", "content": codigo_respuesta})
                return True
            else:
                print("\033[91m[!] Ejecución cancelada por ti.\033[0m")
                codigo_respuesta = f"<tool_response>\n[Error: El humano ha rechazado la ejecución del comando por motivos de seguridad]\n</tool_response>"
                historial_chat.append({"role": "user", "content": codigo_respuesta})
                return True
                
    except json.JSONDecodeError:
        print("\n\033[91m[!] El modelo generó un JSON de tool alucinado o malformado.\033[0m")
        codigo_respuesta = f"<tool_response>\n[Error: Formato JSON inválido. Reestructura e inténtalo de nuevo]\n</tool_response>"
        historial_chat.append({"role": "user", "content": codigo_respuesta})
        return True
    except Exception as e:
        print(f"\n\033[91m[!] Error al procesar herramienta: {e}\033[0m")
        return False
        
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
                print("\n[+] Modelos disponibles:")
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
                    
                    # Guardamos la inferencia actual en el chat
                    historial_chat.append({"role": "assistant", "content": respuesta_completa})
                    log_message(conn, 'assistant', respuesta_completa, thoughts=pensamiento_completo,
                                model=modelo_actual, ttft=ttft, session_id=current_session_id)
                                
                    # Procesador automático de Herramientas
                    # Si detecta herramienta, la ejecuta (con confirmación), añade resultado como USER, y exige otra vuelta
                    tuvo_herramienta = procesar_herramienta(respuesta_completa, historial_chat)
                    
                    if tuvo_herramienta:
                        # Log the user's response to the tool execution so it stays in DB
                        ultimo_mensaje_user = historial_chat[-1]["content"]
                        log_message(conn, 'user', ultimo_mensaje_user, session_id=current_session_id)
                        
                        requiere_respuesta = True # El modelo vuelve a hablar al recibir la "tool_response"
                    else:
                        requiere_respuesta = False # Terminamos turno, vuelve a hablar el humano real
                    
                except Exception as e:
                    print(f"\n[!] Error: {e}")
                    # Retroceder si hubo fallo de conexión grave
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
