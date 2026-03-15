import ollama
import sys
import sqlite3
import time
from datetime import datetime

def init_db():
    """Inicializa la base de datos SQLite y crea la tabla si no existe."""
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect('db/chat_history.db')
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
        
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN session_id TEXT")
    except sqlite3.OperationalError:
        pass
        
    cursor.execute("UPDATE messages SET session_id = 'historial_anterior' WHERE session_id IS NULL")
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
    # Modelos disponibles
    AVAILABLE_MODELS = [
        'qwen3.5:0.8b',
        'qwen3.5:2b',
        'qwen3.5:4b',
        'qwen3.5:9b'
    ]
    
    MODEL_NAME = 'qwen3.5:4b'
    SYSTEM_PROMPT = """Eres un asistente virtual amigable y útil. Tu objetivo principal es ayudar al usuario a resolver dudas, explorar ideas y asistir en tareas generales o de código de forma clara y directa. Mantén un tono conversacional, responde siempre en español y proporciona explicaciones concisas."""
    
    print(f"🤖 Asistente Virtual Ollama iniciado (Modelo actual: {MODEL_NAME} - Modo Pensamiento Nativo)")
    print("Escribe '/salir' o '/exit' para terminar.")
    print("Comandos de sesión: '/new' o '/clear' (nueva), '/sessions' (cargar historial).")
    print("Comando de modelo: '/model' (cambiar modelo activo).\n")
    
    # Inicializar Base de Datos
    conn = init_db()
    
    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    while True:
        try:
            user_input = input("\n🧑 Tú: ")
            
            if not user_input.strip():
                continue
                
            # Intercept custom terminal commands
            if user_input.startswith('/'):
                command = user_input.strip().lower()
                if command in ['/salir', '/exit', '/quit']:
                    print("¡Hasta luego!")
                    break
                elif command in ['/clear', '/new']:
                    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
                    current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    print("✨ Nueva sesión iniciada. El contexto ha sido limpiado.")
                    continue
                elif command == '/sessions':
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT session_id, MIN(timestamp), content 
                        FROM messages 
                        WHERE role='user' 
                        GROUP BY session_id 
                        ORDER BY MIN(timestamp) DESC 
                        LIMIT 10
                    ''')
                    sessions = cursor.fetchall()
                    if not sessions:
                        print("📂 No hay sesiones previas guardadas.")
                        continue
                        
                    print("\n📂 Últimas 10 sesiones:")
                    for i, (sid, ts, preview) in enumerate(sessions):
                        pr_text = preview.replace('\n', ' ')
                        if len(pr_text) > 50: pr_text = pr_text[:50] + "..."
                        print(f"  [{i+1}] {ts} - {pr_text}")
                        
                    choice = input("\n🔢 Elige un número para cargar la sesión (o presiona Enter para cancelar): ")
                    if choice.strip().isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(sessions):
                            selected_session = sessions[idx][0]
                            # Cargar historial limpio (sin los pensamientos)
                            cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC", (selected_session,))
                            loaded_msgs = cursor.fetchall()
                            messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
                            for r, c in loaded_msgs:
                                messages.append({'role': r, 'content': c})
                            current_session_id = selected_session
                            print(f"✅ Sesión cargada con {len(messages)} mensajes en el contexto.")
                        else:
                            print("❌ Número fuera de rango. Operación cancelada.")
                    else:
                        print("❌ Operación cancelada.")
                    continue
                elif command == '/model':
                    print("\n🧮 Modelos disponibles:")
                    for idx, mod in enumerate(AVAILABLE_MODELS):
                        indicator = " (Actual)" if mod == MODEL_NAME else ""
                        print(f"  [{idx+1}] {mod}{indicator}")
                    
                    choice = input("\n🔢 Elige un número para cambiar de modelo (o Enter para cancelar): ")
                    if choice.strip().isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(AVAILABLE_MODELS):
                            MODEL_NAME = AVAILABLE_MODELS[idx]
                            print(f"✅ Modelo cambiado exitosamente a: {MODEL_NAME}")
                        else:
                            print("❌ Número fuera de rango. Operación cancelada.")
                    else:
                        print("❌ Operación cancelada.")
                    continue
                else:
                    print(f"⚠️ Comando desconocido: {command}")
                    continue
                
            messages.append({'role': 'user', 'content': user_input})
            # Guardar mensaje del usuario en SQLite
            log_message(conn, 'user', user_input, session_id=current_session_id)
            
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
                        ttft=ttft, prompt_tokens=prompt_eval_count, prompt_time=prompt_time, prompt_tps=prompt_tps,
                        session_id=current_session_id)
            
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
