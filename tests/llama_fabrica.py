import subprocess
import time
import sys
import json
import os
import re
from datetime import datetime
from openai import OpenAI

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_MODELOS = os.path.join(BASE_DIR, "models")
RUTA_LLAMA_SERVER = os.path.join(BASE_DIR, "llama-b8352-bin-win-cuda-12.4-x64", "llama-server.exe")
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
PUERTO = 8080
URL_BASE = f"http://127.0.0.1:{PUERTO}/v1"

os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(CARPETA_MODELOS, exist_ok=True)
MODELOS_DISPONIBLES = [f for f in os.listdir(CARPETA_MODELOS) if f.endswith(".gguf")]

if not MODELOS_DISPONIBLES:
    print(f"❌ Error: No se encontraron modelos .gguf en {CARPETA_MODELOS}")
    sys.exit(1)

servidor_process = None
modelo_actual = MODELOS_DISPONIBLES[-1]

ASCII_ART = "\033[96m" + """
 ╔══════════════════════════════════════════════════════════════════════════╗
 ║                                                                          ║
 ║  [ SYSTEM INIT ] > Cargando motor LLM Qwen-3.5 ................... [OK]  ║
 ║  [ MODULE LOAD ] > FÁBRICA DE SOFTWARE ........................... [OK]  ║
 ║                                                                          ║
 ║   █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗    ██████╗ ███████╗║
 ║  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝    ╚════██╗██╔════╝║
 ║  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   █████╗       █████╔╝███████╗║
 ║  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██╔══╝       ╚═══██╗╚════██║║
 ║  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████╗    ██████╔╝███████║║
 ║  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝    ╚═════╝ ╚══════╝║
 ║                                                                          ║
 ║  [ ◉ ] Modelo: Qwen 3.5 Turbo                                            ║
 ║  [ ◉ ] Framework: Python 3        [ Estado: Fábrica Autónoma Online ]    ║
 ║                                                                          ║
 ╚══════════════════════════════════════════════════════════════════════════╝
""" + "\033[0m"

SYSTEM_PROMPT = """Eres el Arquitecto de una Fábrica de Software Python Autónoma.
Tu misión principal es inventar y programar juegos de Python divertidos, creativos, variados y 100% jugables utilizando la librería `pygame`.

REGLAS E INSTRUCCIONES ESTRICTAS:
1. Lee atentamente el historial de proyectos que el usuario te proporcionará para evitar crear juegos redundantes o similares.
2. Todo juego debe importar `pygame`, inicializarse correctamente y tener un bucle principal de juego. Escribe código modular, robusto y con comentarios.
3. Para generar el proyecto, DEBES responder usando este formato de etiquetas XML estrictamente:

<project_id>NUMERO_nombre_proyecto</project_id>
<description>Una breve descripción de 1 línea del proyecto</description>

<file name="main.py">
```python
# Código de main.py completo aquí
```
</file>

<file name="README.md">
```markdown
# README
```
</file>

4. Puedes crear tantos archivos `<file>` como necesites, pero al menos un `main.py` es obligatorio.
5. NO respondas con charla fuera de las etiquetas XML para no gastar tokens inútilmente y ser rápido."""

def iniciar_servidor(thinking=True):
    global servidor_process
    if servidor_process is not None:
        servidor_process.terminate()
        servidor_process.wait()
        
    ruta_modelo_completa = os.path.join(CARPETA_MODELOS, modelo_actual)
    kwargs = json.dumps({"enable_thinking": thinking})
    comando = [
        RUTA_LLAMA_SERVER,
        "-m", ruta_modelo_completa,
        "-c", "8192", 
        "-ngl", "99",
        "--port", str(PUERTO),
        "--chat-template-kwargs", kwargs
    ]
    
    estado = "ACTIVADO" if thinking else "DESACTIVADO"
    print(f"\n\033[90m[+] Iniciando llama-server FABRICA (Modelo: {modelo_actual} | Thinking: {estado})...\033[0m")
    servidor_process = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    import urllib.request
    print("\033[90m    [!] Esperando a que el motor arranque...\033[0m")
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
             print("\n\033[91m❌ Error: El proceso colapsó.\033[0m")
             sys.exit(1)
        time.sleep(1)
    else:
        print("\n\033[91m❌ Error: Timeout al arrancar.\033[0m")
        sys.exit(1)
    print(f"\033[92m[+] Fábrica online y conectada.\033[0m\n")

def detener_servidor():
    global servidor_process
    if servidor_process is not None:
        print("\n\033[90m[-] Apagando el servidor...\033[0m")
        servidor_process.terminate()
        servidor_process.wait()
        servidor_process = None

def main():
    print(ASCII_ART)
    iniciar_servidor(thinking=False) 
    cliente = OpenAI(base_url=URL_BASE, api_key="local")
    
    base_scripts = os.path.join(WORKSPACE_DIR, "scripts_python")
    os.makedirs(base_scripts, exist_ok=True)
    historial_file = os.path.join(base_scripts, "scripts_historial.txt")
    
    try:
        while True:
            val = input("\n\033[93m¿Cuántos proyectos distintos quieres crear en esta tanda? (Ingresa número o 0 para salir): \033[0m").strip()
            if not val.isdigit() or int(val) <= 0:
                print("Finalizando ejecución.")
                break
                
            num_scripts = int(val)
            MAX_REINTENTOS = 3
            
            for iteracion in range(num_scripts):
                if not os.path.exists(historial_file):
                    with open(historial_file, 'w', encoding='utf-8') as f:
                        f.write("=== HISTORIAL DE PROGRAMAS CREADOS ===\n")
                
                with open(historial_file, 'r', encoding='utf-8') as f:
                    historial_actual = f.read()

                print(f"\n\033[96m[➔] Iniciando producción: Proyecto {iteracion + 1} de {num_scripts}...\033[0m")
                
                user_prompt = f"Inicia la producción. Aquí tienes el inventario actual de scripts_historial.txt. Inventa un programa NUEVO basándote en que no se repita con este listado u otorga el ID '1_app' si la lista está vacía:\n\n{historial_actual}\n\nRECUERDA: Define la estructura en bloques XML <file name=\"...\"> con formato Markdown puro para el código."
                chat_fabricacion = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
                
                proyecto_exitoso = False
                for reintento in range(MAX_REINTENTOS + 1):
                    try:
                        t0 = time.time()
                        t_first_token = None
                        think_tokens = 0
                        speak_tokens = 0
                        
                        stream = cliente.chat.completions.create(
                            model="qwen-local",
                            messages=chat_fabricacion,
                            temperature=0.7,
                            stream=True
                        )
                        
                        respuesta_completa = ""
                        for chunk in stream:
                            if t_first_token is None:
                                t_first_token = time.time()
                                
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                                think_tokens += 1
                                print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)
                            elif hasattr(delta, 'content') and delta.content:
                                speak_tokens += 1
                                print(f"\033[90m{delta.content}\033[0m", end="", flush=True)
                                respuesta_completa += delta.content

                        print("\n")
                        
                        ttft = (t_first_token - t0) if t_first_token else 0.0
                        dur_total = time.time() - t0
                        tps = (think_tokens + speak_tokens) / dur_total if dur_total > 0 else 0
                        print(f"\033[90m[⚡ TTFT: {ttft:.2f}s | 🧠 Think: {think_tokens} tk | 🗣️ Speak: {speak_tokens} tk ({tps:.1f} t/s)]\033[0m")
                        
                        # Parsing XML + Markdown
                        match_id = re.search(r'<project_id>(.*?)</project_id>', respuesta_completa, re.DOTALL | re.IGNORECASE)
                        match_desc = re.search(r'<description>(.*?)</description>', respuesta_completa, re.DOTALL | re.IGNORECASE)
                        
                        archivos_encontrados = []
                        for file_match in re.finditer(r'<file name=["\']?(.*?)["\']?>(.*?)</file>', respuesta_completa, re.DOTALL | re.IGNORECASE):
                            filename = file_match.group(1).strip()
                            content = file_match.group(2).strip()
                            
                            # Limpiar bloques markdown si existen (```python ... ```)
                            lines = content.split('\n')
                            if len(lines) >= 2 and lines[0].strip().startswith('```'):
                                # Eliminar la primera linea y la ultima si empiezan con ```
                                if lines[-1].strip().startswith('```'):
                                    content = '\n'.join(lines[1:-1])
                                else:
                                    content = '\n'.join(lines[1:])
                                    
                            archivos_encontrados.append((filename, content))
                            
                        if not match_id or not archivos_encontrados:
                            error_msg = ("Error de Parseo: No se encontraron las etiquetas XML "
                                         "<project_id> o <file>. Por favor, sigue estrictamente el formato.")
                            print(f"\033[91m[❌ ERROR PARSING] {error_msg}\033[0m")
                            chat_fabricacion.append({"role": "assistant", "content": respuesta_completa})
                            chat_fabricacion.append({"role": "user", "content": error_msg + " Corrige y reescribe completamente el proyecto."})
                            continue
                            
                        # Si parseo OK, creamos archivos temporalmente para revisar sintaxis
                        id_raw = match_id.group(1).split('-')[0].split(':')[0].strip() # Cortar si el modelo añade descripción extra 
                        id_nombre = re.sub(r'[^a-zA-Z0-9_\-]', '_', id_raw).lower()
                        id_nombre = re.sub(r'_+', '_', id_nombre)[:40].strip('_') # Colapsar múltiples _ y limitar a 40 chars
                        proyecto_dir = os.path.join(base_scripts, id_nombre)
                        os.makedirs(proyecto_dir, exist_ok=True)
                        
                        main_existe = False
                        main_path = ""
                        
                        for filename, content in archivos_encontrados:
                            filepath = os.path.join(proyecto_dir, filename)
                            # Prevenir path traversal vulnerabilidad por las dudas
                            if os.path.abspath(filepath).startswith(os.path.abspath(proyecto_dir)):
                                with open(filepath, "w", encoding='utf-8') as f:
                                    f.write(content)
                                if filename == "main.py":
                                    main_existe = True
                                    main_path = filepath
                        
                        if main_existe:
                            print(f"\033[36m[ℹ️] Ejecutando control de calidad sintáctico (py_compile) a main.py...\033[0m")
                            check_proc = subprocess.run([sys.executable, "-m", "py_compile", main_path], capture_output=True, text=True)
                            
                            if check_proc.returncode != 0: # Sintaxis tiene bugs
                                err_out = check_proc.stderr.strip()
                                # CONTEXT PRUNING: Recortar a max 20 líneas
                                err_lines = err_out.split('\n')
                                if len(err_lines) > 20:
                                    err_out = "\n".join(err_lines[-20:])
                                
                                err_msg = f"Tu compilación de main.py me ha devuelto este error sintáctico:\n```\n{err_out}\n```\nEntiende el error, arréglalo y vuelve a escribir las etiquetas completas <project_id>, <description> y <file name=\"...\"> con el código corregido."
                                print(f"\033[91m[❌ BUG SINTÁCTICO] Self-healing activado (Intento {reintento+1}/{MAX_REINTENTOS})\033[0m")
                                
                                chat_fabricacion.append({"role": "assistant", "content": respuesta_completa})
                                chat_fabricacion.append({"role": "user", "content": err_msg})
                                continue
                        else:
                            print("\033[33m[!] Advertencia: No se detectó main.py, saltando verificación de sintaxis.\033[0m")
                            
                        # Si todo esta OK, o si se saltó verificación
                        desc_corta = match_desc.group(1).strip() if match_desc else "Sin descripción especial"
                        with open(historial_file, "a", encoding='utf-8') as f:
                            f.write(f"- {id_nombre} : {desc_corta}\n")
                        
                        print(f"\033[92m[✅ ÉXITO] El proyecto '{id_nombre}' fue generado exitosamente tras {reintento} intentos de curación.\033[0m")
                        proyecto_exitoso = True
                        break # Salir del bucle de reintentos
                        
                    except Exception as loop_e:
                        print(f"\033[91m[!] Error en el ciclo LLM/Parseo: {loop_e}\033[0m")
                        break # Salir del bucle LLM en caso de error de red
                        
                if not proyecto_exitoso:
                     print(f"\033[91m[💀 ABORTADO] No se pudo generar el proyecto tras los reintentos permitidos.\033[0m")
                     
    except KeyboardInterrupt:
        print("\n\033[33m[!] Fabrica detenida manualmente.\033[0m")
    finally:
        detener_servidor()

if __name__ == "__main__":
    main()
