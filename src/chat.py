import subprocess
import time
import sys
import json
import os
import sqlite3
import threading
from datetime import datetime
from flask import Flask, request, Response, render_template, jsonify
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
cliente = None

app = Flask(__name__)
PUERTO_WEB = 5000

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "models": MODELOS_DISPONIBLES,
        "current_model": modelo_actual,
        "thinking": modo_thinking_actual
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    global modelo_actual, modo_thinking_actual, cliente
    data = request.json
    modelo_req = data.get('modelo', modelo_actual)
    thinking_req = data.get('thinking', modo_thinking_actual)
    
    if modelo_req != modelo_actual or thinking_req != modo_thinking_actual:
        modelo_actual = modelo_req
        modo_thinking_actual = thinking_req
        iniciar_servidor(thinking=thinking_req, modelo=modelo_req)
        cliente = OpenAI(base_url=URL_BASE, api_key="local")
        
    return jsonify({"status": "success"})

@app.route('/api/clear', methods=['POST'])
def clear_chat_web():
    global historial_chat
    historial_chat = [{"role": "system", "content": "Eres un asistente útil, directo y conciso."}]
    return jsonify({"status": "success"})

@app.route('/api/chat', methods=['POST'])
def chat_stream():
    global historial_chat, cliente
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
        
    historial_chat.append({"role": "user", "content": user_message})

    def generate():
        try:
            stream = cliente.chat.completions.create(
                model="qwen-local",
                messages=historial_chat,
                temperature=0.6,
                stream=True
            )
            
            respuesta_completa = ""
            for chunk in stream:
                delta = chunk.choices[0].delta
                
                # Pensamientos
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    payload = json.dumps({"type": "think", "content": delta.reasoning_content})
                    yield f"data: {payload}\n\n"
                    
                # Respuesta final hablada
                elif hasattr(delta, 'content') and delta.content:
                    respuesta_completa += delta.content
                    payload = json.dumps({"type": "speak", "content": delta.content})
                    yield f"data: {payload}\n\n"
            
            historial_chat.append({"role": "assistant", "content": respuesta_completa})
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            print(f"Error en stream: {e}")
            yield f"data: {json.dumps({'type': 'speak', 'content': 'Error interno del servidor.'})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

def iniciar_servidor_web():
    def run_flask():
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        app.run(host='0.0.0.0', port=PUERTO_WEB, debug=False, use_reloader=False, threaded=True)

    print(f"\n\033[92m🚀 Servidor web iniciado en background!\033[0m")
    print(f"\033[96m   ► Local: http://127.0.0.1:{PUERTO_WEB}\033[0m")
    threading.Thread(target=run_flask, daemon=True).start()

ASCII_ART = "\033[96m" + """
 ╔══════════════════════════════════════════════════════════════════════════╗
 ║                                                                          ║
 ║  [ SYSTEM INIT ] > Cargando motor LLM Qwen-3.5 ................... [OK]  ║
 ║  [ MODULE LOAD ] > Entorno Python activado ....................... [OK]  ║
 ║                                                                          ║
 ║   █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗    ██████╗ ███████╗║
 ║  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝    ╚════██╗██╔════╝║
 ║  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   █████╗       █████╔╝███████╗║
 ║  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██╔══╝       ╚═══██╗╚════██║║
 ║  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████╗    ██████╔╝███████║║
 ║  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝    ╚═════╝ ╚══════╝║
 ║                                                                          ║
 ║  [ ◉ ] Modelo: Qwen 3.5 Turbo                                            ║
 ║  [ ◉ ] Framework: Python 3        [ Estado: Online & Esperando input ]   ║
 ║                                                                          ║
 ╚══════════════════════════════════════════════════════════════════════════╝
""" + "\033[0m"

def init_db():
    os.makedirs(os.path.join(BASE_DIR, 'db'), exist_ok=True)
    db_path = os.path.join(BASE_DIR, 'db', 'llama_history.db')
    conn = sqlite3.connect(db_path)
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

def obtener_sesiones(conn):
    """Devuelve las últimas 10 sesiones con su primer mensaje para identificarlas."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT session_id, MIN(timestamp), content 
        FROM messages 
        WHERE role = 'user' AND session_id != '' 
        GROUP BY session_id 
        ORDER BY MIN(timestamp) DESC 
        LIMIT 10
    ''')
    return cursor.fetchall()

def cargar_sesion(conn, session_id):
    """Reconstruye el historial de chat desde la base de datos para una sesión dada."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content 
        FROM messages 
        WHERE session_id = ? 
        ORDER BY id ASC
    ''', (session_id,))
    
    nuevo_historial = [{"role": "system", "content": "Eres un asistente útil, directo y conciso."}]
    for row in cursor.fetchall():
        role, content = row
        nuevo_historial.append({"role": role, "content": content})
    return nuevo_historial

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
        "-c", "4096",
        "-ngl", "99",
        "--port", str(PUERTO),
        "--chat-template-kwargs", kwargs
    ]
    
    estado = "ACTIVADO" if thinking else "DESACTIVADO"
    print(f"\n\033[90m[+] Iniciando backend A35 (Modelo: {modelo} | Thinking: {estado})...\033[0m")
    
    servidor_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import urllib.request
    
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
             print("\n\033[91m❌ Error: El proceso de llama-server colapsó.\033[0m")
             sys.exit(1)
             
        time.sleep(1)
    else:
        print("\n\033[91m❌ Error: Tiempo de espera agotado al cargar el modelo.\033[0m")
        sys.exit(1)

    print("\033[92m[+] Conectado al cerebro neural. Listo.\033[0m\n")

def detener_servidor():
    global servidor_process
    if servidor_process is not None:
        print("\n\033[90m[-] Desconectando backend...\033[0m")
        servidor_process.terminate()
        servidor_process.wait()
        servidor_process = None

def imprimir_ayuda():
    print(ASCII_ART)
    print("\033[33m" + "="*50)
    print("🤖 TERMINAL DE CONTROL AGENTE 35")
    print("="*50 + "\033[0m")
    print("\033[1mComandos disponibles:\033[0m")
    print("  \033[96m/think\033[0m     -> Activa modo de razonamiento interno")
    print("  \033[96m/nothink\033[0m   -> Desactiva modo de razonamiento")
    print("  \033[96m/model\033[0m     -> Lista y cambia el archivo .gguf actual")
    print("  \033[96m/prompt\033[0m    -> Muestra y permite cambiar la System Prompt")
    print("  \033[96m/clear\033[0m     -> Borra historial actual de la sesión")
    print("  \033[96m/new\033[0m       -> Inicia una nueva sesión id en blanco")
    print("  \033[96m/sessions\033[0m  -> Lista y restaura conversaciones anteriores")
    print("  \033[96m/web\033[0m       -> Inicia la interfaz web en http://127.0.0.1:5000")
    print("  \033[96m/exit\033[0m      -> Desconecta llama-server y cierra terminal")
    print("\033[33m" + "="*50 + "\033[0m\n")

def main():
    global modo_thinking_actual, historial_chat, modelo_actual, cliente
    
    os.makedirs(os.path.join(BASE_DIR, "src"), exist_ok=True)
    iniciar_servidor(thinking=modo_thinking_actual, modelo=modelo_actual)
    cliente = OpenAI(base_url=URL_BASE, api_key="local")
    
    historial_chat = [{"role": "system", "content": "Eres un asistente útil, directo y conciso."}]
    imprimir_ayuda()

    try:
        current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        conn = init_db()
        
        while True:
            usuario = input("\033[92mUsuario ❯\033[0m ")
            
            if not usuario.strip():
                continue
                
            comando = usuario.strip().lower()
            if comando in ["/salir", "/exit", "/quit"]:
                break
            elif comando == "/clear":
                historial_chat = [{"role": "system", "content": "Eres un asistente útil, directo y conciso."}]
                print("\033[33m[!] Historial limpio. Siguiendo en sesión actual.\033[0m")
                continue
            elif comando == "/new":
                historial_chat = [{"role": "system", "content": "Eres un asistente útil, directo y conciso."}]
                current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                print(f"\033[92m[+] Iniciada nueva sesión estandarte: {current_session_id}\033[0m")
                continue
            elif comando == "/sessions":
                sesiones = obtener_sesiones(conn)
                if not sesiones:
                    print("\033[33m[!] No hay sesiones previas guardadas.\033[0m")
                    continue
                    
                print("\n\033[36m--- SESIONES RECIENTES ---\033[0m")
                for i, sesion in enumerate(sesiones):
                    s_id, timestamp, u_msg = sesion
                    preview = u_msg[:40] + "..." if len(u_msg) > 40 else u_msg
                    marca = "📍" if s_id == current_session_id else "  "
                    print(f"\033[36m{marca} {i+1}. [{timestamp}] ID: {s_id}\033[0m -> {preview.replace(chr(10), ' ')}")
                
                sel = input("\n\033[92mElige número para restaurar (o Enter para cancelar) ❯\033[0m ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(sesiones):
                    elegida = sesiones[int(sel)-1][0]
                    current_session_id = elegida
                    historial_chat = cargar_sesion(conn, current_session_id)
                    print(f"\033[92m[+] Sesión {current_session_id} restaurada con éxito. Tiene {len(historial_chat)-1} interacciones.\033[0m")
                else:
                    print("\033[33m[!] Operación cancelada.\033[0m")
                continue
            elif comando == "/web":
                iniciar_servidor_web()
                continue
            elif comando == "/think":
                if not modo_thinking_actual:
                    modo_thinking_actual = True
                    iniciar_servidor(thinking=True)
                    cliente = OpenAI(base_url=URL_BASE, api_key="local")
                else:
                    print("\033[33m[!] Modo de razonamiento interno ya activo.\033[0m")
                continue
            elif comando == "/nothink":
                if modo_thinking_actual:
                    modo_thinking_actual = False
                    iniciar_servidor(thinking=False)
                    cliente = OpenAI(base_url=URL_BASE, api_key="local")
                else:
                    print("\033[33m[!] Modo de razonamiento ya desactivado.\033[0m")
                continue

            elif comando == "/prompt":
                print(f"\n\033[36m--- SYSTEM PROMPT ACTUAL ---\033[0m\n{historial_chat[0]['content']}\n\033[36m----------------------------\033[0m")
                nuevo_prompt = input("\033[92mEscribe la nueva System Prompt (o Enter para mantener la actual) ❯\033[0m ").strip()
                if nuevo_prompt:
                    historial_chat[0]['content'] = nuevo_prompt
                    print("\033[92m[+] System Prompt actualizada.\033[0m")
                else:
                    print("\033[33m[!] System Prompt sin cambios.\033[0m")
                continue
            elif comando == "/model":
                print("\n\033[36m--- MODELOS DISPONIBLES ---\033[0m")
                for i, m in enumerate(MODELOS_DISPONIBLES):
                    prefix = "📍" if m == modelo_actual else "  "
                    print(f"\033[36m{prefix} {i+1}.\033[0m {m}")
                    
                sel = input("\n\033[92mElige el número del modelo (o Enter para cancelar) ❯\033[0m ").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(MODELOS_DISPONIBLES):
                    modelo_nuevo = MODELOS_DISPONIBLES[int(sel)-1]
                    if modelo_nuevo != modelo_actual:
                        modelo_actual = modelo_nuevo
                        iniciar_servidor(thinking=modo_thinking_actual, modelo=modelo_actual)
                        cliente = OpenAI(base_url=URL_BASE, api_key="local")
                    else:
                        print("\033[33m[!] Ese modelo ya está cargado en memoria actualmente.\033[0m")
                else:
                    print("\033[33m[!] Cambio de modelo cancelado.\033[0m")
                continue

            historial_chat.append({"role": "user", "content": usuario})
            log_message(conn, 'user', usuario, session_id=current_session_id)
            
            print("\033[96mA35 ❯\033[0m ", end="", flush=True)
            
            try:
                t0 = time.time()
                t_first_token = None
                t_think_start = None
                t_think_end = None
                t_speak_start = None
                t_speak_end = None
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
                            print("\n\n\033[92m[Salida:]\033[0m\n", end="")
                            empezo_respuesta_final = True
                            
                        speak_token_count += 1
                        print(delta.content, end="", flush=True)
                        respuesta_completa += delta.content
                        
                if t_speak_end is None:
                    t_speak_end = time.time()
                    
                print("\n")
                
                ttft = (t_first_token - t0) if t_first_token else 0.0
                dur_think = (t_think_end - t_think_start) if t_think_end and t_think_start else 0.0
                dur_speak = (t_speak_end - t_speak_start) if t_speak_end and t_speak_start else 0.0
                dur_total = dur_think + dur_speak
                total_tokens = think_token_count + speak_token_count
                
                tps_think = (think_token_count / dur_think) if dur_think > 0 else 0.0
                tps_speak = (speak_token_count / dur_speak) if dur_speak > 0 else 0.0
                tps_total = (total_tokens / dur_total) if dur_total > 0 else 0.0
                
                print(f"\033[90m[⚡ TTFT: {ttft:.2f}s | 🧠 Think: {think_token_count} tk ({tps_think:.1f} t/s) | 🗣️ Speak: {speak_token_count} tk ({tps_speak:.1f} t/s)]\033[0m\n")
                
                historial_chat.append({"role": "assistant", "content": respuesta_completa})
                
                log_message(conn, role='assistant', content=respuesta_completa, thoughts=pensamiento_completo,
                            model=modelo_actual, system_prompt="Eres un asistente útil, directo y conciso.",
                            think_tokens=think_token_count, speak_tokens=speak_token_count, total_tokens=total_tokens,
                            think_time=dur_think, speak_time=dur_speak, total_time=dur_total,
                            think_tps=tps_think, speak_tps=tps_speak, total_tps=tps_total,
                            ttft=ttft, prompt_tokens=0, prompt_time=0.0, prompt_tps=0.0, 
                            session_id=current_session_id)
                
            except Exception as e:
                print(f"\n\033[91m[!] Error de conexión: {e}\033[0m")
                historial_chat.pop()
                
    except KeyboardInterrupt:
        print("\n\033[33m[!] Interrupción humana (Ctrl+C).\033[0m")
    finally:
        detener_servidor()
        if 'conn' in locals():
            conn.close()
        print("\033[96mDesconectado. ¡Hasta la próxima!\033[0m")

if __name__ == "__main__":
    main()
