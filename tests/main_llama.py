import subprocess
import time
import sys
import json
import os
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
            
            print("\033[96mAsistente:\033[0m ", end="", flush=True)
            
            try:
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
                    # Extraer el fragmento de texto desde la lista de choices
                    delta = chunk.choices[0].delta
                    
                    # 1. Capturar y mostrar el "Pensamiento" (reasoning_content)
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                        # Imprimimos el pensamiento en color gris oscuro
                        print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)
                        pensamiento_completo += delta.reasoning_content
                        
                    # 2. Capturar y mostrar el "Contenido" (la respuesta final)
                    if hasattr(delta, 'content') and delta.content is not None:
                        # Si es la primera vez que entramos a la respuesta final y hubo pensamiento previo
                        if not empezo_respuesta_final and pensamiento_completo != "":
                            print("\n\n\033[92m[Respuesta Final:]\033[0m\n", end="")
                            empezo_respuesta_final = True
                            
                        # Imprimimos la respuesta final normal
                        print(delta.content, end="", flush=True)
                        respuesta_completa += delta.content
                        
                print("\n") # Salto de línea final
                
                # Guardar SOLO la respuesta final en el historial (no queremos que el modelo lea sus propios pensamientos pasados)
                historial_chat.append({"role": "assistant", "content": respuesta_completa})
                
            except Exception as e:
                print(f"\n[!] Error de conexión: {e}")
                print("[!] ¿El servidor sigue cargando o colapsó?")
                historial_chat.pop() # Quitar el mensaje del usuario si falló
                
    except KeyboardInterrupt:
        print("\n[!] Interrupción detectada.")
    finally:
        # Asegurarnos SIEMPRE de matar el servidor al salir
        detener_servidor()
        print("¡Adiós!")

if __name__ == "__main__":
    main()