import sqlite3
import os

DB_PATH = 'db/chat_history.db'

def get_connection():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: No se encontró la base de datos '{DB_PATH}'.")
        return None
    return sqlite3.connect(DB_PATH)

def list_sessions():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT session_id, COUNT(id) as msg_count, MIN(timestamp) as start_time
            FROM messages
            GROUP BY session_id
            ORDER BY start_time DESC
        ''')
        sessions = cursor.fetchall()
        
        if not sessions:
            print("\n📂 No se encontraron sesiones en la base de datos.")
            return
            
        print("\n" + "="*80)
        print(f"{'SESIONES ALMACENADAS':^80}")
        print("="*80)
        print(f"{'Nº':<4} | {'ID de Sesión':<22} | {'Fecha/Hora Inicio':<22} | {'Mensajes':<10}")
        print("-" * 80)
        
        for i, (sid, count, ts) in enumerate(sessions):
            print(f"[{i+1:<2}] | {str(sid):<22} | {str(ts):<22} | {count:<10}")
            
        print("="*80)
        return sessions
    except sqlite3.OperationalError as e:
        print(f"❌ Error al leer las sesiones: {e}")
    finally:
        conn.close()

def view_session_messages(session_id):
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, timestamp, role, content, total_tokens, dur_total, tps_total, model, prompt_tokens, ttft, thoughts
            FROM (
                SELECT id, timestamp, role, content, total_tokens, total_time as dur_total, total_tps as tps_total, model, prompt_tokens, ttft, thoughts
                FROM messages
                WHERE session_id = ?
            )
            ORDER BY id ASC
        ''', (session_id,))
        messages = cursor.fetchall()
        
        if not messages:
            print(f"\n📂 No hay mensajes en la sesión {session_id}.")
            return

        print("\n" + "="*100)
        print(f" MENSAJES DE LA SESIÓN: {session_id} ".center(100, "="))
        print("="*100)
        
        for msg in messages:
            msg_id, ts, role, content, tokens, time_s, tps, model, prompts, ttft, thoughts = msg
            
            # Formato de visualización
            color = "\033[94m" if role == 'user' else "\033[92m"
            reset = "\033[0m"
            emoji = "🧑 Tú" if role == 'user' else "🤖 Asistente"
            
            print(f"\n{color}--- [{msg_id}] {ts} - {emoji} {reset}")
            
            if role == 'assistant' and model:
                print(f"\033[90m(Modelo: {model} | Prompt Tokens: {prompts or 0} | Generado: {tokens or 0} tokens | Tiempo: {time_s or 0:.2f}s | TTFT: {ttft or 0:.2f}s)\033[0m")
                
            # Limitar contenido largo para legibilidad si excede 500 caracteres, a menos que sea muy largo
            display_content = content
            print(f"\n{display_content}")
            
            if thoughts and str(thoughts).strip():
                print("\n\033[93m[Pensamientos]\033[0m")
                thought_preview = thoughts[:200].replace('\n', ' ') + "..." if len(thoughts) > 200 else thoughts
                print(f"\033[90m{thought_preview}\033[0m")
                
        print("\n" + "="*100 + "\n")
            
    except sqlite3.OperationalError as e:
        print(f"❌ Error de esquema: {e}")
    finally:
        conn.close()

def main_menu():
    print("🌟 Bienvenido al Visor de Base de Datos Telemetríca Ollama 🌟")
    while True:
        try:
            sessions = list_sessions()
            if not sessions:
                input("\nPresiona Enter para intentar nuevamente o Ctrl+C para salir.")
                continue

            print("\nOpciones:")
            print(" - Escribe el 'Nº' de una sesión para ver sus mensajes.")
            print(" - Escribe 'q' o 'salir' para terminar.")
            
            choice = input("\nElige una opción: ").strip().lower()
            
            if choice in ['q', 'salir', 'exit', 'quit']:
                print("¡Hasta luego!")
                break
                
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(sessions):
                    selected_session = sessions[idx][0]
                    view_session_messages(selected_session)
                    input("\nPulsa Enter para volver al menú principal...")
                else:
                    print("❌ Número de sesión inválido.")
            else:
                if choice:
                    print("❌ Opción no reconocida.")
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break

if __name__ == "__main__":
    main_menu()
