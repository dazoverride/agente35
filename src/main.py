import ollama
import sys
import sqlite3
import time
from datetime import datetime

def init_db():
    """Inicializa la base de datos SQLite y crea la tabla si no existe."""
    conn = sqlite3.connect('chat_history.db')
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
            prompt_tps REAL
        )
    ''')
    
    # Migración básica si la base de datos ya existía con el esquema anterior
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN model TEXT")
        cursor.execute("ALTER TABLE messages ADD COLUMN system_prompt TEXT")
        cursor.execute("ALTER TABLE messages ADD COLUMN think_tokens INTEGER")
        cursor.execute("ALTER TABLE messages ADD COLUMN speak_tokens INTEGER")
        cursor.execute("ALTER TABLE messages ADD COLUMN total_tokens INTEGER")
        cursor.execute("ALTER TABLE messages ADD COLUMN think_time REAL")
        cursor.execute("ALTER TABLE messages ADD COLUMN speak_time REAL")
        cursor.execute("ALTER TABLE messages ADD COLUMN total_time REAL")
        cursor.execute("ALTER TABLE messages ADD COLUMN think_tps REAL")
        cursor.execute("ALTER TABLE messages ADD COLUMN speak_tps REAL")
        cursor.execute("ALTER TABLE messages ADD COLUMN total_tps REAL")
    except sqlite3.OperationalError:
        pass # Las columnas ya existen o tabla recien creada
        
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN ttft REAL")
        cursor.execute("ALTER TABLE messages ADD COLUMN prompt_tokens INTEGER")
        cursor.execute("ALTER TABLE messages ADD COLUMN prompt_time REAL")
        cursor.execute("ALTER TABLE messages ADD COLUMN prompt_tps REAL")
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    return conn

def log_message(conn, role, content, thoughts="", model="", system_prompt="", 
                think_tokens=0, speak_tokens=0, total_tokens=0, 
                think_time=0.0, speak_time=0.0, total_time=0.0, 
                think_tps=0.0, speak_tps=0.0, total_tps=0.0,
                ttft=0.0, prompt_tokens=0, prompt_time=0.0, prompt_tps=0.0):
    """Guarda un mensaje y sus estadísticas en la base de datos."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (
            role, content, thoughts, model, system_prompt,
            think_tokens, speak_tokens, total_tokens,
            think_time, speak_time, total_time,
            think_tps, speak_tps, total_tps,
            ttft, prompt_tokens, prompt_time, prompt_tps
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (role, content, thoughts, model, system_prompt, 
          think_tokens, speak_tokens, total_tokens, 
          think_time, speak_time, total_time, 
          think_tps, speak_tps, total_tps,
          ttft, prompt_tokens, prompt_time, prompt_tps))
    conn.commit()

def main():
    """
    Initializes and runs a command-line virtual assistant using Ollama and the Qwen 3.5 model.

    This function sets up an interactive loop where the user can chat with the AI.
    It configures the model with optimal sampling parameters for reasoning/thinking mode.
    It uses Ollama's native support for capturing the internal Chain of Thought (CoT)
    via the 'thinking' field in the API response and logs the chat history to SQLite.

    Parameters:
        None

    Returns:
        None
    """
    MODEL_NAME = 'qwen3.5:4b'
    SYSTEM_PROMPT = ""
    
    print(f"🤖 Asistente Virtual Ollama iniciado (Modelo: {MODEL_NAME} - Modo Pensamiento Nativo)")
    print("Escribe 'salir' o 'exit' para terminar.\n")
    
    # Inicializar Base de Datos
    conn = init_db()
    
    messages = []
    
    while True:
        try:
            user_input = input("\n🧑 Tú: ")
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("¡Hasta luego!")
                break
                
            if not user_input.strip():
                continue
                
            messages.append({'role': 'user', 'content': user_input})
            # Guardar mensaje del usuario en SQLite
            log_message(conn, 'user', user_input)
            
            print("🤖 Asistente: ", end="", flush=True)
            
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
            
            # Variables de tiempo y telemetria
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
            
            # Bandera para saber si ya hemos impreso el inicio del bloque de pensamientos
            started_thinking = False
            has_spoken = False
            
            for chunk in stream:
                if t_first_token is None:
                    t_first_token = time.time()
                    
                if t_think_start is None:
                    t_think_start = time.time()
                    
                message_chunk = chunk.get('message', {})
                
                # 1. Capturar el pensamiento nativo si existe
                think_content = message_chunk.get('thinking')
                if think_content is not None and think_content != '':
                    think_token_count += 1
                    if not started_thinking:
                        print("\n\033[90m[Pensamiento Interno Nativo:]\n", end="", flush=True)
                        started_thinking = True
                        
                    print(f"\033[90m{think_content}\033[0m", end="", flush=True)
                    assistant_thoughts += think_content
                    
                # 2. Capturar el contenido hablado final de la respuesta
                content = message_chunk.get('content')
                if content is not None and content != '':
                    speak_token_count += 1
                    if started_thinking:
                        # Si estaba pensando y ahora habla, metemos un salto y reseteamos bandera
                        t_think_end = time.time()
                        t_speak_start = time.time()
                        print("\n\n\033[0m[Respuesta:]\n", end="", flush=True)
                        started_thinking = False
                    elif not has_spoken and not assistant_thoughts:
                        t_speak_start = time.time()
                        
                    has_spoken = True
                    print(f"\033[0m{content}", end="", flush=True)
                    assistant_response += content
                    
                # 3. Capturar metricas finales de Ollama
                if chunk.get('done'):
                    prompt_eval_count = chunk.get('prompt_eval_count', 0)
                    prompt_eval_duration = chunk.get('prompt_eval_duration', 0) / 1e9
                    eval_count = chunk.get('eval_count', 0)
                    eval_duration_ns = chunk.get('eval_duration', 0)
                    t_speak_end = time.time()
                    if t_think_end is None and started_thinking:
                        t_think_end = time.time()
                
            print("\n", flush=True) 
            
            # Calculos de estadisticas
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
            
            print(f"\033[36m📊 [Estadísticas de la Inferencia]\033[0m")
            print(f"\033[36m  ├─ ⏱️ Reacción (TTFT) : {ttft:.2f}s (Tiempo hasta el primer token)\033[0m")
            if prompt_time > 0:
                print(f"\033[36m  ├─ 📥 Prompt (Entrada): {prompt_eval_count} tokens | Tiempo: {prompt_time:.2f}s | Velocidad: {prompt_tps:.2f} t/s\033[0m")
            print(f"\033[36m  ├─ 🧠 Pensamiento     : {think_token_count} tokens | Tiempo: {dur_think:.2f}s | Velocidad: {tps_think:.2f} t/s\033[0m")
            print(f"\033[36m  ├─ 🗣️ Respuesta       : {speak_token_count} tokens | Tiempo: {dur_speak:.2f}s | Velocidad: {tps_speak:.2f} t/s\033[0m")
            print(f"\033[36m  └─ 🚀 Total Generado  : {total_tokens} tokens | Tiempo: {dur_total:.2f}s | Velocidad: {tps_total:.2f} t/s\033[0m\n")
            
            # Guardamos la respuesta normal en el historial (los pensamientos no van al historial para no confundir contexto futuro)
            messages.append({'role': 'assistant', 'content': assistant_response})
            # Guardar la respuesta Y las métricas completas del asistente en SQLite
            log_message(conn, role='assistant', content=assistant_response, thoughts=assistant_thoughts,
                        model=MODEL_NAME, system_prompt=SYSTEM_PROMPT,
                        think_tokens=think_token_count, speak_tokens=speak_token_count, total_tokens=total_tokens,
                        think_time=dur_think, speak_time=dur_speak, total_time=dur_total,
                        think_tps=tps_think, speak_tps=tps_speak, total_tps=tps_total,
                        ttft=ttft, prompt_tokens=prompt_eval_count, prompt_time=prompt_time, prompt_tps=prompt_tps)
            
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break # Salir del bucle para cerrar la conexión DB
        except Exception as e:
            print(f"\nError: {e}")
            
    # Cerrar conexión al salir
    conn.close()

if __name__ == "__main__":
    import os
    os.system("") 
    main()
