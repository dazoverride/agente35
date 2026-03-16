import pyttsx3
import speech_recognition as sr
import os
from datetime import datetime

# Configuración del motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # Velocidad de habla
engine.setProperty('volume', 1.0)  # Volumen
engine.setProperty('pitch', 180)   # Tono

# Configuración del reconocimiento de voz
recognizer = sr.Recognizer()

# Lista de comandos de voz disponibles
comandos_voz = {
    'saludar': ['hola', 'hello', 'buenos días', 'buenas noches'],
    'hora': ['hora', 'qué hora es', 'time'],
    'fecha': ['fecha', 'hoy es', 'what is date'],
    'salir': ['adios', 'bye', 'cerrar', 'exit', 'salir'],
    'ayuda': ['ayuda', 'comandos', 'help']
}

def iniciar_sistema():
    print("🎤 Sistema de Asistente de Voz Activado.")
    print("📢 Habla con el sistema para interactuar.")
    print("⌨️  También puedes usar el teclado para escribir.")
    return recognizer

def hablar(texto):
    """Función para que el sistema hable."""
    print(f"🤖 Sistema: {texto}")
    engine.say(texto)
    engine.runAndWait()

def escuchar_comando(recognizer, mic):
    """Escucha y procesa comandos de voz."""
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("👂 Escuchando...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            try:
                texto = recognizer.recognize_google(audio, language='es-ES')
                texto = texto.lower().strip()
                return texto
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                return ""
    except Exception as e:
        print(f"Error al escuchar: {e}")
        return ""

def procesar_texto(texto):
    """Procesa el texto recibido y ejecuta la acción correspondiente."""
    for clave, lista_palabras in comandos_voz.items():
        if any(palabra in texto for palabra in lista_palabras):
            if clave == 'saludar':
                hablar("¡Hola! ¿En qué puedo ayudarte hoy?")
            elif clave == 'hora':
                hora_actual = datetime.now().strftime("%H:%M")
                hablar(f"Son las {hora_actual}")
            elif clave == 'fecha':
                fecha_actual = datetime.now().strftime("%d de %B del %Y")
                hablar(f"Hoy es {fecha_actual}")
            elif clave == 'salir':
                hablar("Hasta luego. ¡Que tengas un buen día!")
                return False
            elif clave == 'ayuda':
                hablar("Puedes decir: 'hola', 'hora', 'fecha', 'ayuda' o 'adios'. También puedes escribir en el teclado.")
            break
    return True

def leer_archivo():
    """Lee un archivo de texto desde el teclado."""
    archivo = input("📂 Ingresa la ruta del archivo de texto: ").strip()
    if not os.path.exists(archivo):
        print("❌ El archivo no existe.")
        return
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        print("📄 Contenido del archivo:")
        print(contenido)
        hablar("He leído el archivo. ¿Quieres que lo procese? (escribe 'procesar' o 'no')")
        respuesta = input().strip().lower()
        if respuesta == 'procesar':
            hablar("Procesando el texto...")
            # Aquí podrías agregar lógica para analizar o resumir el texto
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")

def main():
    recognizer = iniciar_sistema()
    mic = sr.Microphone()
    
    print("Iniciando sistema de voz...")
    hablar("Sistema iniciado. Puedo escuchar comandos de voz o leer archivos de texto.")
    
    while True:
        # Opción de voz o teclado
        opcion = input("🎤 (1) Escuchar voz  (2) Leer archivo  (3) Salir: ").strip()
        
        if opcion == '3':
            hablar("Cerrando sistema...")
            break
        elif opcion == '1':
            texto = escuchar_comando(recognizer, mic)
            if texto:
                procesar_texto(texto)
            else:
                hablar("No entendí. Intenta de nuevo.")
        elif opcion == '2':
            leer_archivo()
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
