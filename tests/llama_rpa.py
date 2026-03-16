import subprocess
import time
import sys
import json
import os
import webbrowser
from openai import OpenAI

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_MODELOS = os.path.join(BASE_DIR, "models")
RUTA_LLAMA_SERVER = os.path.join(BASE_DIR, "llama-b8352-bin-win-cuda-12.4-x64", "llama-server.exe")
PUERTO = 8080
URL_BASE = f"http://127.0.0.1:{PUERTO}/v1"

os.makedirs(CARPETA_MODELOS, exist_ok=True)
MODELOS_DISPONIBLES = [f for f in os.listdir(CARPETA_MODELOS) if f.endswith(".gguf")]

if not MODELOS_DISPONIBLES:
    print(f"❌ Error: No se encontraron modelos en {CARPETA_MODELOS}")
    sys.exit(1)

servidor_process = None
modelo_actual = MODELOS_DISPONIBLES[-1]

# 2. Definir las herramientas nativas OpeanAI (Tool Schema) - Basado en tmp/rpa.txt
herramientas = [
    {
        "type": "function",
        "function": {
            "name": "abrir_navegador",
            "description": "Abre el navegador web del sistema en una URL específica para buscar información o visitar páginas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "La URL completa de la página web a visitar, ej: https://es.wikipedia.org/wiki/Alan_Turing"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

def abrir_navegador(url):
    print(f"\n[🔧 Acción RPA] Abriendo navegador en: {url}...")
    webbrowser.open(url)
    return f"Éxito: Se ha abierto {url} en el navegador del usuario."

def iniciar_servidor():
    global servidor_process
    if servidor_process is not None:
        servidor_process.terminate()
        servidor_process.wait()
        
    ruta_modelo_completa = os.path.join(CARPETA_MODELOS, modelo_actual)
    comando = [
        RUTA_LLAMA_SERVER,
        "-m", ruta_modelo_completa,
        "-c", "8192", 
        "-ngl", "99",
        "--port", str(PUERTO)
    ]
    
    print(f"\n[+] Iniciando llama-server RPA (Modelo: {modelo_actual})...")
    servidor_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import urllib.request
    print("    [!] Esperando a que el motor arranque...")
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
             print("\n❌ Error: El proceso colapsó.")
             sys.exit(1)
        time.sleep(1)
    else:
        print("\n❌ Error: Timeout al arrancar.")
        sys.exit(1)
    print(f"[+] Servidor RPA online.\n")

def detener_servidor():
    global servidor_process
    if servidor_process is not None:
        print("\n[-] Apagando el servidor...")
        servidor_process.terminate()
        servidor_process.wait()

def main():
    iniciar_servidor()
    cliente = OpenAI(base_url=URL_BASE, api_key="local")
    
    print("\n" + "="*50)
    print("🤖 AGENTE RPA CON QWEN 3.5 (Compatibilidad Nativa OpenAI Tools)")
    print("="*50)
    print("El modelo ahora usará llamadas JSON estructuradas oficiales")
    print("en lugar de hacks XML. Puedes pedirle que abra páginas web.")
    print("Escribe 'salir' para terminar.")
    print("="*50 + "\n")

    historial = [
        {"role": "system", "content": "Eres un asistente de escritorio automatizado. Usa SIEMPRE las herramientas proporcionadas para cumplir la petición del usuario si requiere buscar información externa o interactuar con el navegador."}
    ]

    try:
        while True:
            # Entrada de usuario
            usuario = input("\033[92mTú:\033[0m ").strip()
            
            if usuario.lower() in ["salir", "exit", "quit"]:
                break
                
            if not usuario:
                continue

            historial.append({"role": "user", "content": usuario})
            
            print("\033[96mAsistente (Razonando...):\033[0m ", end="", flush=True)

            # Primera llamada: El modelo decide si usa la herramienta
            try:
                respuesta = cliente.chat.completions.create(
                    model="qwen-local",
                    messages=historial,
                    tools=herramientas,
                    temperature=0.2 # Temperatura baja para que acierte en los esquemas JSON
                )
                
                # Agregamos la respuesta cruda del asistente al historial de roles
                mensaje_modelo = respuesta.choices[0].message
                historial.append(mensaje_modelo)
                
                print("[Listo]")
                
                # Comprobar si decidió usar herramientas nativas en la respuesta
                if getattr(mensaje_modelo, 'tool_calls', None):
                    for tool_call in mensaje_modelo.tool_calls:
                        if tool_call.function.name == "abrir_navegador":
                            try:
                                argumentos = json.loads(tool_call.function.arguments)
                                url_solicitada = argumentos.get("url", "")
                                
                                # HITL (Human-in-the-Loop) Interceptación
                                confirmacion = input(f"\n\033[93m⚠️ PRECAUCIÓN: Qwen quiere abrir el navegador en '{url_solicitada}'. ¿Permitir? (s/n): \033[0m")
                                
                                if confirmacion.lower() == 's':
                                    resultado_herramienta = abrir_navegador(url_solicitada)
                                else:
                                    resultado_herramienta = "Error: El usuario denegó el permiso por seguridad. Indícaselo y pídele disculpas o pregunta si prefiere otra cosa."
                                    print("    [!] Permiso denegado.")
                                
                                # Inyectar resultado ejecutado al historial con rol de 'tool'
                                historial.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_call.function.name,
                                    "content": resultado_herramienta
                                })
                                
                                # Segunda llamada: Qwen genera la contestación final sabiendo qué pasó en el navegador
                                print("\033[96mAsistente (Final):\033[0m ", end="", flush=True)
                                stream = cliente.chat.completions.create(
                                    model="qwen-local",
                                    messages=historial,
                                    temperature=0.5,
                                    stream=True
                                )
                                
                                r_final = ""
                                for chunk in stream:
                                    delta = chunk.choices[0].delta
                                    if hasattr(delta, 'content') and delta.content:
                                        print(delta.content, end="", flush=True)
                                        r_final += delta.content
                                print("\n")
                                historial.append({"role": "assistant", "content": r_final})
                                
                            except Exception as e:
                                print(f"\n[!] Error procesando JSON de la herramienta nativa: {e}")
                else:
                    # Contestación general sin activar herramientas
                    contenido = getattr(mensaje_modelo, 'content', None) or "(Sin respuesta textual, solo pensó en sí mismo)."
                    print(f"\n\033[96mAsistente:\033[0m {contenido}\n")
                    
            except Exception as e:
                print(f"\n[!] Error en la comunicación TCP/IP con llama-server: {e}")
                historial.pop()

    except KeyboardInterrupt:
        print("\n[!] Uso detenido manualmente.")
    finally:
        detener_servidor()

if __name__ == "__main__":
    main()
