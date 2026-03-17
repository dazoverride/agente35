import subprocess
import time
import sys
import json
import os
import sqlite3
import threading
import re
from datetime import datetime
from flask import Flask, request, Response, render_template, jsonify
from openai import OpenAI
from ddgs import DDGS

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
modelo_actual = MODELOS_DISPONIBLES[-1] # Por defecto usa el último
historial_chat = []
cliente = None

SYSTEM_PROMPT = """Eres el Agente Orquestador Principal (Lead Orchestrator). 
Tu trabajo es desglosar tareas complejas y delegarlas a tus sub-agentes especialistas utilizando las herramientas proporcionadas.

## Reglas de Delegación (CRÍTICO)
1. **NO leas archivos ni ejecutes comandos de sistema directamente.** Debes DELEGAR estas tareas a tus sub-agentes usando el formato XML de herramientas.
2. Tienes tres sub-agentes especialistas:
   - **Sysadmin (call_sysadmin_agent):** Para comandos powershell y sistema operativo local.
   - **Coder (call_coder_agent):** EXCLUSIVAMENTE para LEER/ESCRIBIR archivos de código fuente.
   - **Web (call_web_agent):** Para buscar información, documentación o resolución de errores en Internet empleando DuckDuckGo.
3. Pasa referencias ligeras (como rutas de archivo o temas) en lugar de bloques masivos de código.

## Uso de herramientas
Usa estrictamente XML para delegar:
<tool_call>
{"name": "call_coder_agent", "arguments": {"task_description": "Añade un manejador de excepciones en main.py", "target_files": ["main.py"]}}
</tool_call>

<tools>
{"type": "function", "function": {"name": "call_sysadmin_agent", "description": "Delega una tarea de exploración de sistema o terminal al Administrador de Sistemas.", "parameters": {"type": "object", "properties": {"task_description": {"type": "string"}, "context_focus_question": {"type": "string"}}}, "required": ["task_description", "context_focus_question"]}}
{"type": "function", "function": {"name": "call_coder_agent", "description": "Delega una tarea de programación al agente programador para que lea y escriba en archivos de código.", "parameters": {"type": "object", "properties": {"task_description": {"type": "string"}, "target_files": {"type": "array", "items": {"type": "string"}}}}, "required": ["task_description", "target_files"]}}
{"type": "function", "function": {"name": "call_web_agent", "description": "Delega una tarea de búsqueda en internet al agente Web.", "parameters": {"type": "object", "properties": {"task_description": {"type": "string"}, "search_query": {"type": "string"}}}, "required": ["task_description", "search_query"]}}
</tools>

4. ABSTENCIÓN: Si te falta información, no finjas. Delega o pide ayuda al usuario."""

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'tests', 'templates'))
PUERTO_WEB = 5000

SYSADMIN_PROMPT = """Eres el Agente Sysadmin (System Administrator Sub-Agent).
Tu tarea es ejecutar comandos precisos de terminal en Windows (Powershell) para explorar directorios o recopilar configuraciones para tu Orquestador.

## Tarea Asignada y Enfoque
- Tarea General: {task_description}
- Pregunta de Filtro: {context_focus_question}

## Proceso
1. Usa la herramienta `ejecutar_comando_sistema` si necesitas inspeccionar el disco.
<tool_call>
{"name": "ejecutar_comando_sistema", "arguments": {"comando": "dir"}}
</tool_call>
3. Cuando tengas la respuesta, redacta un **RESUMEN DESTILADO Y CONCISO** sin verbosidad.

<tools>
{"type": "function", "function": {"name": "ejecutar_comando_sistema", "description": "Ejecuta powershell.", "parameters": {"type": "object", "properties": {"comando": {"type": "string"}}}, "required": ["comando"]}}
</tools>"""

CODER_PROMPT = """Eres el Agente Programador (Coder Sub-Agent).
Tu tarea es modificar el código fuente del proyecto exactamente como pide el orquestador.

## Requerimientos y Restricciones:
- Tarea a realizar: {task_description}
- Archivos objetivo previstos: {target_files}
- **THOUGHT FIRST:** Antes de hacer una tool call, DEBES escribir un bloque `Thought: [tu razonamiento]` analizando qué vas a leer/escribir.
- **NO EXTRA FEATURES:** Implementa SOLO lo solicitado. No inventes UI o animaciones extra.

## Herramientas:
1. Para LEER un archivo usa `leer_archivo`.
2. Para ESCRIBIR/SOBRESCRIBIR un archivo usa `escribir_archivo`.

<tool_call>
{"name": "leer_archivo", "arguments": {"filepath": "tests/app.py"}}
</tool_call>

<tools>
{"type": "function", "function": {"name": "leer_archivo", "description": "Lee contenido de un archivo", "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}}}, "required": ["filepath"]}}
{"type": "function", "function": {"name": "escribir_archivo", "description": "Escribe contenido reemplazando todo el archivo", "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}, "content": {"type": "string"}}}, "required": ["filepath", "content"]}}
</tools>

Cuando hayas terminado, redacta un **RESUMEN BREVE** de los archivos que modificaste para el Orquestador."""

WEB_PROMPT = """Eres el Agente de Búsqueda Web (Web Browser Sub-Agent).
Tu tarea es buscar información en internet para responder preguntas técnicas o de documentación.

## Requerimientos y Restricciones:
- Tarea General: {task_description}
- **THOUGHT FIRST:** Analiza qué términos de búsqueda usar en un bloque `Thought: [tu razonamiento]`.
- **EFICIENCIA:** Las páginas web son largas. Si lees una URL (`read_webpage`) y ya contiene los datos, DETENTE y responde. NO sigas buscando ni leyendo más páginas.
- **ABSTENCIÓN:** Si tras 3 intentos no encuentras nada útil, responde: "Datos insuficientes". No alucines soluciones.
- **GROUNDING:** Basa tu respuesta final ÚNICAMENTE en el contexto recuperado de la web. Cita la fuente/URL.

## Herramientas:
Tienes acceso a dos herramientas: `search_web` para buscar información y `read_webpage` para leer el contenido completo de una URL específica.

Ejemplo de uso:
<tool_call>
{"name": "search_web", "arguments": {"query": "python socket example"}}
</tool_call>
o
<tool_call>
{"name": "read_webpage", "arguments": {"url": "https://es.wikipedia.org/wiki/Ejemplo"}}
</tool_call>

<tools>
{"type": "function", "function": {"name": "search_web", "description": "Busca información en la web mediante DuckDuckGo.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}, "required": ["query"]}}
{"type": "function", "function": {"name": "read_webpage", "description": "Lee el contenido de texto de una URL.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}}, "required": ["url"]}}
</tools>

CRÍTICO REGLA DE PARADA: Una vez que hayas leído los resultados en `<tool_response>` y tengas la información suficiente para responder a la tarea, DEBES escribir tu respuesta final de forma NORMAL (texto o markdown) y DEBES omitir por completo cualquier bloque `<tool_call>`. Si incluyes un `<tool_call>` seguirás buscando infinitamente."""

def ag_sysadmin_ejecutar_comando(comando):
    print(f"\n\033[95m[🔧 Sysadmin Sub-Agent]: Ejecutando -> {comando}\033[0m")
    try:
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        resultado = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "chcp 65001 >$null; " + comando], 
            shell=False, capture_output=True, text=True, timeout=30, cwd=BASE_DIR, env=env
        )
        salida = resultado.stdout if resultado.returncode == 0 else resultado.stderr
        if not salida.strip(): salida = "[Ejecutado. Salida vacía.]"
        if len(salida) > 2500: salida = salida[:2500] + "...[TRUNCADO]"
    except Exception as e:
        salida = f"[Error: {e}]"
    return salida

def call_sysadmin_agent(task_description: str, context_focus_question: str) -> str:
    print("\n\033[96m[🤖 Orchestrator]: Delegando tarea al Sub-Agente Sysadmin...\033[0m")
    prompt_con_datos = SYSADMIN_PROMPT.replace("{task_description}", task_description).replace("{context_focus_question}", context_focus_question)
    r_messages = [
        {"role": "system", "content": prompt_con_datos},
        {"role": "user", "content": "Comienza la tarea de Sysadmin ahora. Analiza la petición y llama a la herramienta adecuada en formato XML."}
    ]
    for step in range(5):
        res = cliente.chat.completions.create(model="qwen-local", messages=r_messages, temperature=0.4, frequency_penalty=0.3)
        msg_crudo = res.choices[0].message.content
        r_messages.append({"role": "assistant", "content": msg_crudo})
        call_match = re.search(r'<tool_call>(.*?)</tool_call>', msg_crudo, re.DOTALL)
        if call_match:
            try:
                tool_data = json.loads(call_match.group(1).strip())
                if tool_data.get("name") == "ejecutar_comando_sistema":
                    salida = ag_sysadmin_ejecutar_comando(tool_data["arguments"]["comando"])
                    r_messages.append({"role": "user", "content": f"<tool_response>\n{salida}\n</tool_response>"})
                    continue
            except:
                r_messages.append({"role": "user", "content": f"<tool_response>[Error de Parseo JSON]</tool_response>"})
                continue
        return msg_crudo
    return "Error: Límite de turnos sysadmin."

def ag_coder_leer_archivo(filepath):
    print(f"\n\033[32m[💻 Coder Sub-Agent]: Leyendo archivo -> {filepath}\033[0m")
    full_path = os.path.join(BASE_DIR, filepath)
    if not os.path.exists(full_path):
        return f"[Error: El archivo {filepath} no existe]"
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            contenido = f.read()
            if len(contenido) > 8000:
                return contenido[:8000] + "\n...[TRUNCADO por tamaño masivo]"
            return contenido
    except Exception as e:
        return f"[Error al leer {filepath}: {e}]"

def ag_coder_escribir_archivo(filepath, content):
    print(f"\n\033[32m[💻 Coder Sub-Agent]: Escribiendo archivo -> {filepath}\033[0m")
    full_path = os.path.join(BASE_DIR, filepath)
    os.makedirs(os.path.dirname(os.path.abspath(full_path)), exist_ok=True)
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[Éxito: Archivo {filepath} actualizado]"
    except Exception as e:
        return f"[Error al escribir {filepath}: {e}]"

def call_coder_agent(task_description: str, target_files: list) -> str:
    print("\n\033[96m[🤖 Orchestrator]: Delegando tarea al Sub-Agente Coder...\033[0m")
    prompt_con_datos = CODER_PROMPT.replace("{task_description}", task_description).replace("{target_files}", ", ".join(target_files))
    r_messages = [
        {"role": "system", "content": prompt_con_datos},
        {"role": "user", "content": "Comienza la tarea de programación ahora. Examina los archivos usando herramientas si es necesario (Recuerda poner el bloque Thought: primero)."}
    ]
    for step in range(6):
        res = cliente.chat.completions.create(model="qwen-local", messages=r_messages, temperature=0.3, frequency_penalty=0.3)
        msg_crudo = res.choices[0].message.content
        r_messages.append({"role": "assistant", "content": msg_crudo})
        call_match = re.search(r'<tool_call>(.*?)</tool_call>', msg_crudo, re.DOTALL)
        if call_match:
            try:
                tool_data = json.loads(call_match.group(1).strip())
                n_herr = tool_data.get("name")
                args = tool_data.get("arguments", {})
                if n_herr == "leer_archivo":
                    salida = ag_coder_leer_archivo(args.get("filepath", ""))
                elif n_herr == "escribir_archivo":
                    salida = ag_coder_escribir_archivo(args.get("filepath", ""), args.get("content", ""))
                else:
                    salida = "[Error: Herramienta desconocida]"
                
                r_messages.append({"role": "user", "content": f"<tool_response>\n{salida}\n</tool_response>"})
                continue
            except Exception as e:
                r_messages.append({"role": "user", "content": f"<tool_response>[Error de Parseo JSON: {e}]</tool_response>"})
                continue
        return msg_crudo
    return "Error: Límite de turnos coder alcanzado."

def ag_web_buscar(query):
    print(f"\n\033[36m[🌐 Web Sub-Agent]: Buscando en DuckDuckGo -> {query}\033[0m")
    try:
        raw_results = list(DDGS().text(query, max_results=3))
        # Formatear la salida más simple para el LLM
        clean_text = ""
        for i, r in enumerate(raw_results):
            clean_text += f"\nResultado {i+1}: {r.get('title', '')}\nURL: {r.get('href', '')}\n{r.get('body', '')}\n"
        
        if len(clean_text) > 4000:
            return clean_text[:4000] + "...[TRUNCADO]"
        return clean_text if clean_text else "No se encontraron resultados relevantes."
    except Exception as e:
        return f"[Error en búsqueda web: {e}]"

def ag_web_leer_pagina(url):
    print(f"\n\033[36m[🌐 Web Sub-Agent]: Leyendo página -> {url}\033[0m")
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            text = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
            text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
            text = re.sub(r'<.*?>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 8000:
                return text[:8000] + "...[TRUNCADO]"
            return text if text else "[Página vacía]"
    except Exception as e:
        return f"[Error al leer página: {e}]"

def call_web_agent(task_description: str, search_query: str) -> str:
    print("\n\033[96m[🤖 Orchestrator]: Delegando tarea al Sub-Agente Web...\033[0m")
    prompt_con_datos = WEB_PROMPT.replace("{task_description}", task_description)
    r_messages = [
        {"role": "system", "content": prompt_con_datos},
        {"role": "user", "content": f"Comienza la tarea de búsqueda Web ahora con la consulta sugerida: '{search_query}'. Llama a la herramienta <tool_call> search_web si lo necesitas."}
    ]
    for step in range(8):
        res = cliente.chat.completions.create(model="qwen-local", messages=r_messages, temperature=0.3, frequency_penalty=0.3)
        msg_crudo = res.choices[0].message.content
        r_messages.append({"role": "assistant", "content": msg_crudo})
        
        # Debugging the thought process to terminal:
        print(f"\n\033[90m[Web Agent Step {step+1}] {msg_crudo[:300]}...\033[0m")
        
        call_match = re.search(r'<tool_call>(.*?)</tool_call>', msg_crudo, re.DOTALL)
        if call_match:
            try:
                tool_data = json.loads(call_match.group(1).strip())
                if tool_data.get("name") == "search_web":
                    salida = ag_web_buscar(tool_data["arguments"]["query"])
                    r_messages.append({"role": "user", "content": f"<tool_response>\n{salida}\n</tool_response>"})
                    continue
                elif tool_data.get("name") == "read_webpage":
                    salida = ag_web_leer_pagina(tool_data["arguments"]["url"])
                    r_messages.append({"role": "user", "content": f"<tool_response>\n{salida}\n</tool_response>"})
                    continue
            except Exception as e:
                r_messages.append({"role": "user", "content": f"<tool_response>[Error de Parseo JSON: {e}]</tool_response>"})
                continue
        return msg_crudo
    return "[Error: Límite de turnos Web alcanzado repentinamente en el step 8 sin encontrar el final.]"

@app.route('/')
def index():
    return render_template('agents.html')

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
    historial_chat = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"status": "success"})

def preparar_historial_enmascarado(historial_completo, ventana_conservar=10):
    """
    Observation Masking: Mantiene las últimas N interacciones completas.
    Para interacciones más antiguas con la terminal <tool_response>, reemplaza 
    el contenido verboso con un placeholder para ahorrar tokens masivamente.
    """
    if len(historial_completo) <= ventana_conservar:
        return historial_completo
        
    historial_enmascarado = []
    umbral_idx = len(historial_completo) - ventana_conservar
    
    for i, msg in enumerate(historial_completo):
        if i < umbral_idx and msg["role"] == "user" and "<tool_response>" in msg["content"]:
            # Es viejo y es la salida de una terminal. Masking agresivo.
            contenido_limpio = re.sub(
                r'<tool_response>.*?</tool_response>', 
                '<tool_response>\n[Detalles de la salida terminal antigua omitidos por brevedad para preservar contexto]\n</tool_response>', 
                msg["content"], 
                flags=re.DOTALL
            )
            historial_enmascarado.append({"role": msg["role"], "content": contenido_limpio})
        else:
            historial_enmascarado.append(msg)
            
    return historial_enmascarado

def generador_stream_llm():
    global historial_chat, cliente
    try:
        historial_optimizado = preparar_historial_enmascarado(historial_chat, 10)
        
        stream = cliente.chat.completions.create(
            model="qwen-local",
            messages=historial_optimizado,
            temperature=0.6,
            frequency_penalty=0.3,
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

@app.route('/api/chat', methods=['POST'])
def chat_stream():
    global historial_chat
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
        
    historial_chat.append({"role": "user", "content": user_message})

    return Response(generador_stream_llm(), mimetype='text/event-stream')

@app.route('/api/tool_action', methods=['POST'])
def tool_action():
    global historial_chat
    data = request.json
    accion = data.get('action') # 'accept' o 'reject'
    
    # 1. Buscar el ultimo mensaje del asistente en el historial para encontrar el tool_call
    ultimo_msg = None
    for msg in reversed(historial_chat):
        if msg["role"] == "assistant":
            ultimo_msg = msg["content"]
            break
            
    if not ultimo_msg:
        return jsonify({"error": "No hay mensaje previo en el historial para procesar herramienta"}), 400
        
    match = re.search(r'<tool_call>\s*({.*?})\s*</tool_call>', ultimo_msg, re.DOTALL)
    if not match:
        return jsonify({"error": "No se encontró <tool_call> en el último mensaje"}), 400
        
    try:
        if accion == "accept":
            print(f"\n[*] Ejecutando herramienta delegada desde WebUI...")
            # Delegamos a la lógica nativa del orquestador que usa sub-agentes
            ejecuto = procesar_herramienta(ultimo_msg, historial_chat)
            if not ejecuto:
                historial_chat.append({"role": "user", "content": "<tool_response>[Error: Falló la ejecución del agente delegado]</tool_response>"})
        else:
            # Rechazado por el usuario en la UI
            print("\n[!] Ejecución cancelada por el usuario desde WebUI.")
            codigo_respuesta = f"<tool_response>\n[Error: El humano ha rechazado la ejecución del comando por motivos de seguridad]\n</tool_response>"
            historial_chat.append({"role": "user", "content": codigo_respuesta})
        
        # Devolver el stream para que el modelo lea la tool_response y conteste inmediatamente
        return Response(generador_stream_llm(), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"Error procesando accion_tool: {e}")
        return jsonify({"error": str(e)}), 500

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
 ║  [ ◉ ] Modelo: Qwen 3.5 Turbo         (Modo Agentivo Tools)              ║
 ║  [ ◉ ] Framework: Python 3        [ Estado: Online & Esperando input ]   ║
 ║                                                                          ║
 ╚══════════════════════════════════════════════════════════════════════════╝
""" + "\033[0m"

def init_db():
    os.makedirs(os.path.join(BASE_DIR, 'db'), exist_ok=True)
    db_path = os.path.join(BASE_DIR, 'db', 'llama_history_tools.db')
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
    
    nuevo_historial = [{"role": "system", "content": SYSTEM_PROMPT}]
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
        "-c", "8192",  # Aumentado a 8192 para mejor contexto de herramientas
        "-ngl", "99",
        "--port", str(PUERTO),
        "--chat-template-kwargs", kwargs
    ]
    
    estado = "ACTIVADO" if thinking else "DESACTIVADO"
    print(f"\n\033[90m[+] Iniciando backend A35 Tools (Modelo: {modelo} | Thinking: {estado})...\033[0m")
    
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

    print("\033[92m[+] Conectado al cerebro neural (Modo Agente). Listo.\033[0m\n")

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
    print("🤖 TERMINAL DE CONTROL AGENTE 35 (CON HERRAMIENTAS)")
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

def procesar_herramienta(respuesta_completa, historial_chat):
    """Busca tool_calls en la respuesta y ejecuta si el usuario lo permite."""
    # Extraemos el bloque JSON dentro de <tool_call> ... </tool_call>
    match = re.search(r'<tool_call>\s*({.*?})\s*</tool_call>', respuesta_completa, re.DOTALL)
    
    if not match:
        return False # No hubo llamada a herramienta

    json_str = match.group(1)
    try:
        tool_data = json.loads(json_str)
    except json.JSONDecodeError:
        print("\n\033[91m[!] El modelo generó un JSON de tool alucinado o malformado.\033[0m")
        codigo_respuesta = f"<tool_response>\n[Error: Formato JSON inválido. Reestructura e inténtalo de nuevo]\n</tool_response>"
        historial_chat.append({"role": "user", "content": codigo_respuesta})
        return True

    if tool_data and tool_data.get("name") == "call_sysadmin_agent":
        print(f"\n\033[93m[>] Agente Delegado [Sysadmin] Instanciado...\033[0m")
        t_desc = tool_data.get("arguments", {}).get("task_description", "N/A")
        focus_q = tool_data.get("arguments", {}).get("context_focus_question", "N/A")
        
        resumen_destilado = call_sysadmin_agent(t_desc, focus_q)
        
        tool_res_str = f"=== RESUMEN EXCLUSIVO DEL SYSADMIN ===\n{resumen_destilado}\n======================================\n"
        print(f"\n\033[92m[<] Resumen Recibido del Sysadmin: {len(tool_res_str)} chars.\033[0m")
        
        historial_chat.append({"role": "user", "content": f"<tool_response>\n{tool_res_str}\n</tool_response>"})
        return True

    elif tool_data and tool_data.get("name") == "call_coder_agent":
        print(f"\n\033[93m[>] Agente Delegado [Coder] Instanciado...\033[0m")
        t_desc = tool_data.get("arguments", {}).get("task_description", "N/A")
        t_files = tool_data.get("arguments", {}).get("target_files", [])
        
        resumen_codigo = call_coder_agent(t_desc, t_files)
        
        tool_res_str = f"=== REPORTE DEL CODER ===\n{resumen_codigo}\n=========================\n"
        print(f"\n\033[92m[<] Reporte Recibido del Coder: {len(tool_res_str)} chars.\033[0m")
        
        historial_chat.append({"role": "user", "content": f"<tool_response>\n{tool_res_str}\n</tool_response>"})
        return True
        
    elif tool_data and tool_data.get("name") == "call_web_agent":
        print(f"\n\033[93m[>] Agente Delegado [Web] Instanciado...\033[0m")
        t_desc = tool_data.get("arguments", {}).get("task_description", "N/A")
        s_query = tool_data.get("arguments", {}).get("search_query", "N/A")
        
        resumen_web = call_web_agent(t_desc, s_query)
        
        tool_res_str = f"=== REPORTE WEB ===\n{resumen_web}\n===================\n"
        print(f"\n\033[92m[<] Reporte Recibido del Web: {len(tool_res_str)} chars.\033[0m")
        
        historial_chat.append({"role": "user", "content": f"<tool_response>\n{tool_res_str}\n</tool_response>"})
        return True
        
    elif tool_data and tool_data.get("name") == "ejecutar_comando_sistema":
        print("\n\033[91m[!] Error Arquitectónico: Orquestador intentó usar comandos básicos directamente.\033[0m")
        historial_chat.append({
            "role": "user",
            "content": f"<tool_response>\n[ERROR ARQUITECTÓNICO]: El Orquestador NO TIENE PERMISO para acceder directo. DEBES delegar al call_sysadmin_agent o call_coder_agent.\n</tool_response>"
        })
        return True
    else:
        # Fallback a viejas herramientas 
        historial_chat.append({
            "role": "user",
            "content": f"<tool_response>\nHerramienta Desconocida.\n</tool_response>"
        })
        return True

def main():
    global modo_thinking_actual, historial_chat, modelo_actual, cliente, SYSTEM_PROMPT
    
    os.makedirs(os.path.join(BASE_DIR, "tests"), exist_ok=True)
    iniciar_servidor(thinking=modo_thinking_actual, modelo=modelo_actual)
    cliente = OpenAI(base_url=URL_BASE, api_key="local")
    
    historial_chat = [{"role": "system", "content": SYSTEM_PROMPT}]
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
                historial_chat = [{"role": "system", "content": SYSTEM_PROMPT}]
                print("\033[33m[!] Historial limpio. Siguiendo en sesión actual.\033[0m")
                continue
            elif comando == "/new":
                historial_chat = [{"role": "system", "content": SYSTEM_PROMPT}]
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
                    SYSTEM_PROMPT = nuevo_prompt
                    historial_chat[0]['content'] = SYSTEM_PROMPT
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
            
            requiere_respuesta = True
            
            while requiere_respuesta:
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
                    
                    historial_optimizado = preparar_historial_enmascarado(historial_chat, 10)
                    
                    stream = cliente.chat.completions.create(
                        model="qwen-local",
                        messages=historial_optimizado,
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
                                model=modelo_actual, system_prompt=SYSTEM_PROMPT,
                                think_tokens=think_token_count, speak_tokens=speak_token_count, total_tokens=total_tokens,
                                think_time=dur_think, speak_time=dur_speak, total_time=dur_total,
                                think_tps=tps_think, speak_tps=tps_speak, total_tps=tps_total,
                                ttft=ttft, prompt_tokens=0, prompt_time=0.0, prompt_tps=0.0, 
                                session_id=current_session_id)
                                
                    tuvo_herramienta = procesar_herramienta(respuesta_completa, historial_chat)
                    
                    if tuvo_herramienta:
                        # Log the user's response to the tool execution so it stays in DB
                        ultimo_mensaje_user = historial_chat[-1]["content"]
                        log_message(conn, role='user', content=ultimo_mensaje_user, session_id=current_session_id)
                        
                        requiere_respuesta = True # El modelo vuelve a hablar al recibir la "tool_response"
                    else:
                        requiere_respuesta = False # Terminamos turno, vuelve a hablar el humano real
                    
                except Exception as e:
                    print(f"\n\033[91m[!] Error de conexión u orquestación: {e}\033[0m")
                    if len(historial_chat) > 0 and historial_chat[-1]["role"] == "user":
                        historial_chat.pop()
                    requiere_respuesta = False
                
    except KeyboardInterrupt:
        print("\n\033[33m[!] Interrupción humana (Ctrl+C).\033[0m")
    finally:
        detener_servidor()
        if 'conn' in locals():
            conn.close()
        print("\033[96mDesconectado. ¡Hasta la próxima!\033[0m")

if __name__ == "__main__":
    main()
