import ollama
import sys
import sqlite3
import time
import os
import re
from datetime import datetime

# Rutas
TEST_PROMPTS_FILE = os.path.join('tmp', 'pruebas.txt')
DB_PATH = os.path.join('db', 'test_history.db')

def init_db():
    """Inicializa la base de datos de pruebas SQLite."""
    os.makedirs('db', exist_ok=True)
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
    """Guarda un mensaje y sus estadísticas en la base de datos de test."""
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

def extract_prompts(filepath):
    """Extrae automáticamente los prompts encerrados en comillas después de 'Prompt de prueba:'."""
    prompts = []
    if not os.path.exists(filepath):
        print(f"❌ Error: El archivo {filepath} no existe.")
        return prompts
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    matches = re.findall(r'Prompt de prueba:\s*"([^"]+)"', content)
    
    if not matches:
        print("Tratando de usar extracción alternativa línea a línea porque no detectó comillas dobles...")
        lines = content.split('\n')
        for line in lines:
            if 'Prompt de prueba:' in line:
                val = line.split('Prompt de prueba:')[1].strip()
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                prompts.append(val)
    else:
        prompts = matches
        
    return prompts

def main():
    AVAILABLE_MODELS = [
        'qwen3.5:4b',
        'qwen3.5:9b'
    ]
    SYSTEM_PROMPT = """Eres un asistente virtual amigable y útil. Tu objetivo principal es ayudar al usuario a resolver dudas, explorar ideas y asistir en tareas generales o de código de forma clara y directa. Mantén un tono conversacional, responde siempre en español y proporciona explicaciones concisas."""
    
    print("="*80)
    print(f"🚀 INICIANDO BATERÍA DE PRUEBAS MULTIMODELO AUTOMATIZADA")
    print(f"📂 Extrayendo pruebas de: {TEST_PROMPTS_FILE}")
    print(f"💾 Guardando resultados en: {DB_PATH}")
    print("="*80)
    
    conn = init_db()
    
    prompts = extract_prompts(TEST_PROMPTS_FILE)
    if not prompts:
        print("❌ No se encontraron prompts en el archivo de origen. Revisa el formato.")
        return
        
    print(f"\n📋 Detectados {len(prompts)} prompts. Iniciando test secuencial iterativo por modelo...\n")
    
    for MODEL_NAME in AVAILABLE_MODELS:
        print("\n" + "="*80)
        print(f"⚙️  EJECUTANDO TESTS EN MODELO: {MODEL_NAME}")
        print("="*80)
        
        for idx, user_input in enumerate(prompts):
            time.sleep(1)
            messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
            
            # ID por modelo y subprueba
            current_session_id = f"TEST_{MODEL_NAME.replace(':', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_P{idx+1}"
            
            print(f"\n" + "-"*80)
            print(f"📝 {MODEL_NAME} - PRUEBA {idx+1}/{len(prompts)}")
            print(f"🧑 Tú: {user_input}")
            print("-" * 80)
            
            messages.append({'role': 'user', 'content': user_input})
            log_message(conn, 'user', user_input, model=MODEL_NAME, session_id=current_session_id)
            
            print("🤖 Asistente: ", end="", flush=True)
            
            try:
                stream = ollama.chat(
                    model=MODEL_NAME,
                    messages=messages,
                    stream=True,
                    options={
                        "temperature": 1.0,           
                        "top_p": 0.95,
                        "top_k": 20,
                        "presence_penalty": 1.5,      
                        "num_predict": 32768,
                        "num_ctx": 32768
                    }
                )
                
                assistant_response = ""
                assistant_thoughts = ""
                
                t0 = time.time()
                t_first_token = None
                t_think_start = None
                t_think_end = None
                t_speak_start = None
                t_speak_end = None
                
                prompt_eval_count = 0
                prompt_eval_duration = 0.0
                eval_count = 0
                eval_duration_ns = 0
                
                think_token_count = 0
                speak_token_count = 0
                
                started_thinking = False
                has_spoken = False
                
                for chunk in stream:
                    if t_first_token is None:
                        t_first_token = time.time()
                        
                    if t_think_start is None:
                        t_think_start = time.time()
                        
                    message_chunk = chunk.get('message', {})
                    
                    think_content = message_chunk.get('thinking')
                    if think_content is not None and think_content != '':
                        think_token_count += 1
                        if not started_thinking:
                            print("\n\033[90m[Pensamiento Interno Nativo:]\n", end="", flush=True)
                            started_thinking = True
                            
                        print(f"\033[90m{think_content}\033[0m", end="", flush=True)
                        assistant_thoughts += think_content
                        
                    content = message_chunk.get('content')
                    if content is not None and content != '':
                        speak_token_count += 1
                        if started_thinking:
                            t_think_end = time.time()
                            t_speak_start = time.time()
                            print("\n\n\033[0m[Respuesta:]\n", end="", flush=True)
                            started_thinking = False
                        elif not has_spoken and not assistant_thoughts:
                            t_speak_start = time.time()
                            
                        has_spoken = True
                        print(f"\033[0m{content}", end="", flush=True)
                        assistant_response += content
                        
                    if chunk.get('done'):
                        prompt_eval_count = chunk.get('prompt_eval_count', 0)
                        prompt_eval_duration = chunk.get('prompt_eval_duration', 0) / 1e9
                        eval_count = chunk.get('eval_count', 0)
                        eval_duration_ns = chunk.get('eval_duration', 0)
                        t_speak_end = time.time()
                        if t_think_end is None and started_thinking:
                            t_think_end = time.time()
                
                print("\n", flush=True) 
                
                ttft = (t_first_token - t0) if t_first_token else 0.0
                dur_think = (t_think_end - t_think_start) if t_think_end and t_think_start else 0.0
                dur_speak = (t_speak_end - t_speak_start) if t_speak_end and t_speak_start else 0.0
                
                dur_total = dur_think + dur_speak
                total_tokens = think_token_count + speak_token_count
                
                prompt_time = prompt_eval_duration
                prompt_tps = (prompt_eval_count / prompt_time) if prompt_time > 0 else 0.0
                
                tps_think = (think_token_count / dur_think) if dur_think > 0 else 0.0
                tps_speak = (speak_token_count / dur_speak) if dur_speak > 0 else 0.0
                tps_total = (total_tokens / dur_total) if dur_total > 0 else 0.0
                
                print(f"\033[36m📊 [Estadísticas Guardadas en BD]\033[0m")
                print(f"\033[36m  ├─ ⏱️ TTFT: {ttft:.2f}s\033[0m")
                print(f"\033[36m  ├─ 📥 Prompt: {prompt_eval_count} tokens | Tiempo: {prompt_time:.2f}s | Velocidad: {prompt_tps:.2f} t/s\033[0m")
                print(f"\033[36m  ├─ 🧠 Pensamiento: {think_token_count} tokens | Tiempo: {dur_think:.2f}s | Velocidad: {tps_think:.2f} t/s\033[0m")
                print(f"\033[36m  └─ 🚀 Respuesta: {speak_token_count} tokens | Tiempo: {dur_speak:.2f}s | Velocidad: {tps_speak:.2f} t/s\033[0m\n")
                print("✅ Prueba completada exitosamente.")
                
                log_message(conn, role='assistant', content=assistant_response, thoughts=assistant_thoughts,
                            model=MODEL_NAME, system_prompt=SYSTEM_PROMPT,
                            think_tokens=think_token_count, speak_tokens=speak_token_count, total_tokens=total_tokens,
                            think_time=dur_think, speak_time=dur_speak, total_time=dur_total,
                            think_tps=tps_think, speak_tps=tps_speak, total_tps=tps_total,
                            ttft=ttft, prompt_tokens=prompt_eval_count, prompt_time=prompt_time, prompt_tps=prompt_tps,
                            session_id=current_session_id)
                            
            except Exception as e:
                print(f"\n❌ Error durante la inferencia de {MODEL_NAME} prueba {idx+1}: {e}")
            
    conn.close()
    print("🎉\n\n=== BATERÍA DE PRUEBAS FINALIZADA ===")
    print(f"Resultados de todos los benchmarks registrados en: {DB_PATH}")

if __name__ == "__main__":
    os.system("") 
    main()
