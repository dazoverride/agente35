import subprocess
import time
import sys
import json
import os
import sqlite3
from datetime import datetime
from openai import OpenAI

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_MODELO = os.path.join(BASE_DIR, "llama-b8352-bin-win-cuda-12.4-x64", "Qwen_Qwen3.5-9B-Q5_K_M.gguf")
RUTA_LLAMA_SERVER = os.path.join(BASE_DIR, "llama-b8352-bin-win-cuda-12.4-x64", "llama-server.exe")
PUERTO = 8080
URL_BASE = f"http://127.0.0.1:{PUERTO}/v1"

# Variables globales
servidor_process = None
modo_thinking_actual = False
historial_chat = []

def init_db():
    """Inicializa la base de datos SQLite y crea la tabla si no existe."""
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect('db/llama_history.db')
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
            think_time REAL,
            speak_time REAL,
            total_time REAL,
            think_tps REAL,
            speak_tps REAL,
            total_tps REAL,
            ttft REAL,
            prompt_tokens INTEGER,
            prompt_time REAL,
            prompt_tps REAL,
            session_id TEXT
        )
    ''')
    conn.commit()
    return conn

def log_message(conn, role, content, thoughts="", model="", system_prompt="", 
                think_tokens=0, speak_tokens=0, total_tokens=0, 
                think_time=0.0, speak_time=0.0, total_time=0.0, 
                think_tps=0.0, speak_tps=0.0, total_tps=0.0,
                ttft=0.0, prompt_tokens=0, prompt_time=0.0, prompt_tps=0.0, session_id=""):
    """Guarda un mensaje y sus estadísticas en la base de datos."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (
            role, content, thoughts, model, system_prompt,
            think_tokens, speak_tokens, total_tokens,
            think_time, speak_time, total_time,
            think_tps, speak_tps, total_tps,
            ttft, prompt_tokens, prompt_time, prompt_tps, session_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (role, content, thoughts, model, system_prompt, 
          think_tokens, speak_tokens, total_tokens, 
          think_time, speak_time, total_time, 
          think_tps, speak_tps, total_tps,
          ttft, prompt_tokens, prompt_time, prompt_tps, session_id))
    conn.commit()

def iniciar_servidor(thinking=False):
    global servidor_process
    detener_servidor()  # Asegurarnos de que no haya otro corriendo
    
    # Al pasar los argumentos en una lista a subprocess, Python maneja las comillas automáticamente
    kwargs = json.dumps({"enable_thinking": thinking})
    comando = [
        RUTA_LLAMA_SERVER, # Usando el ejecutable de la carpeta local
        "-m", RUTA_MODELO,
        "-c", "4096",
        "-ngl", "99",
        "--port", str(PUERTO),
        "--chat-template-kwargs", kwargs
    ]
    
    estado = "ACTIVADO" if thinking else "DESACTIVADO"
    print(f"\n[+] Iniciando llama-server (Modo Thinking: {estado})...")
    
    # Redirigimos la salida del servidor para que no ensucie nuestro chat
    servidor_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Esperar a que el servidor esté listo
    time.sleep(5)
    print("[+] Servidor en línea. ¡Listo para chatear!\n")

def detener_servidor():
    global servidor_process
    if servidor_process is not None:
        print("\n[-] Apagando el servidor...")
        servidor_process.terminate()
        servidor_process.wait()
        servidor_process = None

def imprimir_ayuda():
    print("\n" + "="*50)
    print("🤖 CHAT INTERACTIVO CON QWEN 3.5")
    print("="*50)
    print("Comandos disponibles:")
    print("  /modo think    -> Reinicia el servidor CON modo de pensamiento")
    print("  /modo nothink  -> Reinicia el servidor SIN modo de pensamiento")
    print("  /limpiar       -> Borra el historial de la conversación")
    print("  /salir         -> Apaga el servidor y cierra el programa")
    print("="*50 + "\n")

def main():
    global modo_thinking_actual, historial_chat
    
    # Iniciar con el modo por defecto (sin pensar)
    iniciar_servidor(thinking=modo_thinking_actual)
    cliente = OpenAI(base_url=URL_BASE, api_key="local")
    
    # Prompt de sistema inicial
    historial_chat = [{"role": "system", "content": "Eres un asistente útil, directo y conciso."}]
    
    imprimir_ayuda()

    try:
        current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        conn = init_db()
        
        while True:
            usuario = input("\033[92mTú:\033[0m ")
            
            if not usuario.strip():
                continue
                
            # Procesar comandos
            comando = usuario.strip().lower()
            if comando in ["/salir", "/exit", "/quit"]:
                break
            elif comando == "/limpiar":
                historial_chat = [{"role": "system", "content": "Eres un asistente útil, directo y conciso."}]
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

            # Agregar mensaje del usuario al historial
            historial_chat.append({"role": "user", "content": usuario})
            log_message(conn, 'user', usuario, session_id=current_session_id)
            
            print("\033[96mAsistente:\033[0m ", end="", flush=True)
            
            try:
                t0 = time.time()
                t_first_token = None
                t_think_start = None
                t_think_end = None
                t_speak_start = None
                t_speak_end = None
                think_token_count = 0
                speak_token_count = 0
                
                # Petición a llama-server con streaming para ver la respuesta en tiempo real
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
                        
                    # La estructura JSON de llama-server la mapeamos a la de OpenAI
                    delta = chunk.choices[0].delta
                    
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                        if t_think_start is None:
                            t_think_start = time.time()
                            
                        think_token_count += 1
                        print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)
                        pensamiento_completo += delta.reasoning_content
                        
                    elif hasattr(delta, 'content') and delta.content is not None:
                        if t_think_end is None and pensamiento_completo != "":
                            t_think_end = time.time()
                            
                        if t_speak_start is None:
                            t_speak_start = time.time()
                            
                        if not empezo_respuesta_final and pensamiento_completo != "":
                            print("\n\n\033[92m[Respuesta Final:]\033[0m\n", end="")
                            empezo_respuesta_final = True
                            
                        speak_token_count += 1
                        print(delta.content, end="", flush=True)
                        respuesta_completa += delta.content
                        
                if t_speak_end is None:
                    t_speak_end = time.time()
                    
                print("\n") # Salto de línea final
                
                # Calculos de estadisticas
                ttft = (t_first_token - t0) if t_first_token else 0.0
                dur_think = (t_think_end - t_think_start) if t_think_end and t_think_start else 0.0
                dur_speak = (t_speak_end - t_speak_start) if t_speak_end and t_speak_start else 0.0
                dur_total = dur_think + dur_speak
                total_tokens = think_token_count + speak_token_count
                
                tps_think = (think_token_count / dur_think) if dur_think > 0 else 0.0
                tps_speak = (speak_token_count / dur_speak) if dur_speak > 0 else 0.0
                tps_total = (total_tokens / dur_total) if dur_total > 0 else 0.0
                
                print(f"\033[36m📊 [Estadísticas de la Inferencia]\033[0m")
                print(f"\033[36m  ├─ ⏱️ Reacción (TTFT) : {ttft:.2f}s (Tiempo hasta el primer token)\033[0m")
                print(f"\033[36m  ├─ 🧠 Pensamiento     : {think_token_count} tokens | Tiempo: {dur_think:.2f}s | Velocidad: {tps_think:.2f} t/s\033[0m")
                print(f"\033[36m  ├─ 🗣️ Respuesta       : {speak_token_count} tokens | Tiempo: {dur_speak:.2f}s | Velocidad: {tps_speak:.2f} t/s\033[0m")
                print(f"\033[36m  └─ 🚀 Total Generado  : {total_tokens} tokens | Tiempo: {dur_total:.2f}s | Velocidad: {tps_total:.2f} t/s\033[0m\n")
                
                # Guardar SOLO la respuesta final en el historial
                historial_chat.append({"role": "assistant", "content": respuesta_completa})
                
                log_message(conn, role='assistant', content=respuesta_completa, thoughts=pensamiento_completo,
                            model="qwen-local", system_prompt="Eres un asistente útil, directo y conciso.",
                            think_tokens=think_token_count, speak_tokens=speak_token_count, total_tokens=total_tokens,
                            think_time=dur_think, speak_time=dur_speak, total_time=dur_total,
                            think_tps=tps_think, speak_tps=tps_speak, total_tps=tps_total,
                            ttft=ttft, prompt_tokens=0, prompt_time=0.0, prompt_tps=0.0, 
                            session_id=current_session_id)
                
            except Exception as e:
                print(f"\n[!] Error de conexión: {e}")
                print("[!] ¿El servidor sigue cargando o colapsó?")
                historial_chat.pop() # Quitar el mensaje del usuario si falló
                
    except KeyboardInterrupt:
        print("\n[!] Interrupción detectada.")
    finally:
        # Asegurarnos SIEMPRE de matar el servidor al salir y cerrar base de datos
        detener_servidor()
        if 'conn' in locals():
            conn.close()
        print("¡Adiós!")

if __name__ == "__main__":
    main()