import subprocess
import time
import sys
import json
import os
import re
import sqlite3
from datetime import datetime
from openai import OpenAI

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_MODELOS = os.path.join(BASE_DIR, "models")
RUTA_LLAMA_SERVER = os.path.join(BASE_DIR, "llama-b8352-bin-win-cuda-12.4-x64", "llama-server.exe")
TEST_PROMPTS_FILE = os.path.join(BASE_DIR, 'tmp', 'pruebas.txt')
DB_PATH = os.path.join(BASE_DIR, 'db', 'llama_test_history.db')
PUERTO = 8080
URL_BASE = f"http://127.0.0.1:{PUERTO}/v1"

# Variables globales
servidor_process = None

def init_db():
    """Inicializa la base de datos de pruebas SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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
            session_id TEXT,
            modo_thinking INTEGER
        )
    ''')
    conn.commit()
    return conn

def log_message(conn, role, content, thoughts="", model="", system_prompt="", 
                think_tokens=0, speak_tokens=0, total_tokens=0, 
                think_time=0.0, speak_time=0.0, total_time=0.0, 
                think_tps=0.0, speak_tps=0.0, total_tps=0.0,
                ttft=0.0, prompt_tokens=0, prompt_time=0.0, prompt_tps=0.0, session_id="", modo_thinking=0):
    """Guarda un mensaje y sus estadísticas en la base de datos de test."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (
            role, content, thoughts, model, system_prompt,
            think_tokens, speak_tokens, total_tokens,
            think_time, speak_time, total_time,
            think_tps, speak_tps, total_tps,
            ttft, prompt_tokens, prompt_time, prompt_tps, session_id, modo_thinking
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (role, content, thoughts, model, system_prompt, 
          think_tokens, speak_tokens, total_tokens, 
          think_time, speak_time, total_time, 
          think_tps, speak_tps, total_tps,
          ttft, prompt_tokens, prompt_time, prompt_tps, session_id, modo_thinking))
    conn.commit()

def iniciar_servidor(thinking=False, modelo_archivo=""):
    global servidor_process
    detener_servidor()  
    
    ruta_modelo_completa = os.path.join(CARPETA_MODELOS, modelo_archivo)
    
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
    print(f"\n[+] Iniciando llama-server (Modo Thinking: {estado})...")
    servidor_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import urllib.request
    
    print("    [!] Esperando a que el modelo cargue en RAM/VRAM...")
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
             print("\n❌ Error: El proceso de llama-server ha colapsado (OOM/Crash).")
             sys.exit(1)
             
        time.sleep(1)
    else:
        print("\n❌ Error: Tiempo de espera agotado al cargar el modelo.")
        sys.exit(1)
        
    print("[+] Servidor de pruebas en línea.\n")

def detener_servidor():
    global servidor_process
    if servidor_process is not None:
        print("[-] Apagando servidor de pruebas actual...")
        servidor_process.terminate()
        servidor_process.wait()
        servidor_process = None

def extract_prompts(filepath):
    """Extrae automáticamente los prompts encerrados en comillas o por el prefijo 'Prompt de prueba:'."""
    prompts = []
    if not os.path.exists(filepath):
        print(f"❌ Error: El archivo {filepath} no existe.")
        return prompts
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    matches = re.findall(r'Prompt de prueba:\s*"([^"]+)"', content)
    if not matches:
        lines = content.split('\n')
        for line in lines:
            if 'Prompt de prueba:' in line:
                val = line.split('Prompt de prueba:')[1].strip()
                if val.startswith('"') and val.endswith('"'): val = val[1:-1]
                prompts.append(val)
    else:
        prompts = matches
    return prompts

def ejecutar_bateria(prompts, mod_thinking_activado=False, modelo_archivo=""):
    conn = init_db()
    
    # Arrancamos con el modo solicitado
    iniciar_servidor(thinking=mod_thinking_activado, modelo_archivo=modelo_archivo)
    cliente = OpenAI(base_url=URL_BASE, api_key="local")
    
    SYSTEM_PROMPT = "Eres un asistente útil, directo y conciso."
    nombre_bateria = "CON_THINKING" if mod_thinking_activado else "SIN_THINKING"
    
    for idx, user_input in enumerate(prompts):
        historial_chat = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        current_session_id = f"TEST_{modelo_archivo.replace(':', '_')}_{nombre_bateria}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_P{idx+1}"
        
        print(f"\n" + "-"*80)
        print(f"📝 {modelo_archivo} ({nombre_bateria}) - PRUEBA {idx+1}/{len(prompts)}")
        print(f"🧑 Tú: {user_input}")
        print("-" * 80)
        
        historial_chat.append({'role': 'user', 'content': user_input})
        log_message(conn, 'user', user_input, model=modelo_archivo, session_id=current_session_id, modo_thinking=int(mod_thinking_activado))
        
        print("🤖 Asistente: ", end="", flush=True)
        
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
                    if t_think_start is None: t_think_start = time.time()
                    think_token_count += 1
                    print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)
                    pensamiento_completo += delta.reasoning_content
                    
                elif hasattr(delta, 'content') and delta.content is not None:
                    if t_think_end is None and pensamiento_completo != "": t_think_end = time.time()
                    if t_speak_start is None: t_speak_start = time.time()
                        
                    if not empezo_respuesta_final and pensamiento_completo != "":
                        print("\n\n\033[92m[Respuesta Final:]\033[0m\n", end="")
                        empezo_respuesta_final = True
                        
                    speak_token_count += 1
                    print(delta.content, end="", flush=True)
                    respuesta_completa += delta.content
                    
            if t_speak_end is None: t_speak_end = time.time()
            
            print("\n")
            
            ttft = (t_first_token - t0) if t_first_token else 0.0
            dur_think = (t_think_end - t_think_start) if t_think_end and t_think_start else 0.0
            dur_speak = (t_speak_end - t_speak_start) if t_speak_end and t_speak_start else 0.0
            dur_total = dur_think + dur_speak
            total_tokens = think_token_count + speak_token_count
            
            tps_think = (think_token_count / dur_think) if dur_think > 0 else 0.0
            tps_speak = (speak_token_count / dur_speak) if dur_speak > 0 else 0.0
            tps_total = (total_tokens / dur_total) if dur_total > 0 else 0.0
            
            print(f"\033[36m📊 [Estadísticas Guardadas en BD]\033[0m")
            print(f"\033[36m  ├─ ⏱️ TTFT: {ttft:.2f}s\033[0m")
            print(f"\033[36m  ├─ 🧠 Pensamiento: {think_token_count} tokens | Tiempo: {dur_think:.2f}s | Velocidad: {tps_think:.2f} t/s\033[0m")
            print(f"\033[36m  └─ 🚀 Respuesta: {speak_token_count} tokens | Tiempo: {dur_speak:.2f}s | Velocidad: {tps_speak:.2f} t/s\033[0m\n")
            print("✅ Prueba completada exitosamente.")
            
            log_message(conn, role='assistant', content=respuesta_completa, thoughts=pensamiento_completo,
                        model=modelo_archivo, system_prompt=SYSTEM_PROMPT,
                        think_tokens=think_token_count, speak_tokens=speak_token_count, total_tokens=total_tokens,
                        think_time=dur_think, speak_time=dur_speak, total_time=dur_total,
                        think_tps=tps_think, speak_tps=tps_speak, total_tps=tps_total,
                        ttft=ttft, prompt_tokens=0, prompt_time=0.0, prompt_tps=0.0, 
                        session_id=current_session_id, modo_thinking=int(mod_thinking_activado))
                        
        except Exception as e:
            print(f"\n❌ Error durante la inferencia en prueba {idx+1}: {e}")
            
    conn.close()
    detener_servidor()

def main():
    os.system("") 
    
    os.makedirs(CARPETA_MODELOS, exist_ok=True)
    modelos_disponibles = [f for f in os.listdir(CARPETA_MODELOS) if f.endswith(".gguf")]
    
    if not modelos_disponibles:
        print(f"❌ Error: No se encontraron modelos .gguf en {CARPETA_MODELOS}")
        sys.exit(1)
        
    print("="*80)
    print(f"🚀 INICIANDO BATERÍA DE PRUEBAS LOCAL QWEN LLAMA.CPP")
    print(f"📂 Extrayendo pruebas de: {TEST_PROMPTS_FILE}")
    print(f"💾 Guardando resultados en: {DB_PATH}")
    print(f"📦 Modelos detectados para pruebas: {len(modelos_disponibles)}")
    for m in modelos_disponibles:
        print(f"  - {m}")
    print("="*80)
    
    prompts = extract_prompts(TEST_PROMPTS_FILE)
    if not prompts:
        print("❌ No se encontraron prompts en el archivo de origen. Revisa el formato y nombre de tmp/pruebas.txt.")
        return
        
    print("\n" + "="*80)
    print("Elige las fases de prueba a ejecutar:")
    print("  1. Solo Modo SIN Thinking")
    print("  2. Solo Modo CON Thinking")
    print("  3. Ambos modos (Secuencial)")
    opcion = input("Introduce 1, 2 o 3 (por defecto 3): ").strip()
    
    if opcion not in ["1", "2", "3"]:
        opcion = "3"
        print("> Opción no válida. Usando por defecto: 3 (Ambos)")
        
    for modelo in modelos_disponibles:
        print(f"\n\n{'='*80}")
        print(f"🧪 INICIANDO TESTS PARA EL MODELO: {modelo}")
        print(f"{'='*80}")
        
        if opcion in ["1", "3"]:
            print("\n\n" + "#"*40)
            print(f"    🚀 FASE 1: MODO SIN THINKING ({modelo})")
            print("#"*40)
            ejecutar_bateria(prompts, mod_thinking_activado=False, modelo_archivo=modelo)
            
            if opcion == "3":
                time.sleep(2)
        
        if opcion in ["2", "3"]:
            print("\n\n" + "#"*40)
            print(f"    🚀 FASE 2: MODO CON THINKING ({modelo})")
            print("#"*40)
            ejecutar_bateria(prompts, mod_thinking_activado=True, modelo_archivo=modelo)
        
    print("🎉\n\n=== BATERÍAS DE PRUEBAS FINALIZADAS ===")
    print(f"Resultados de todos los benchmarks locales registrados en: {DB_PATH}")

if __name__ == "__main__":
    main()
