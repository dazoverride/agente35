import random
import datetime

# Base de datos simulada de respuestas para el bot
respuestas_generales = [
    "¡Claro que sí! Dime más sobre ello.",
    "Interesante punto. ¿Podrías explicarme más al respecto?",
    "¡Eso suena genial! Cuéntame más.",
    "Entiendo lo que dices. ¿Y qué piensas que sigue?",
    "¡Exacto! Estoy de acuerdo contigo.",
    "¡Vaya! No lo sabía, cuéntame cómo lo descubriste.",
    "¡Qué buena pregunta! Pienso que la respuesta es...", "¡Genial! ¡Seguimos así!",
    "¡Me encanta saber esto! ¿Has probado también...?"
]

respuestas_de_acuerdo = [
    "¡Totalmente de acuerdo!",
    "¡Así es! Yo también lo pienso.",
    "¡Exactamente! Es lo que he estado pensando.",
    "¡Por supuesto! ¡Es totalmente cierto!"
]

respuestas_preguntas = [
    "¡Qué buena pregunta! Estoy seguro de que la respuesta es...",
    "¡Excelente pregunta! He estado pensando en eso también.",
    "¡Qué interesante! La verdad es que no estoy seguro, pero podría ser..."
]

saludos = ["hola", "hola", "buenos días", "buenas", "qué tal", "hola", "hola", "buenas"]

comentarios = ["genial", "interesante", "vaya", "qué bueno", "interesante", "vaya"]

def responder_bot(mensaje_usuario):
    mensaje_usuario = mensaje_usuario.lower()
    
    # Saludos
    if mensaje_usuario in saludos:
        return f"¡Hola! ¿Cómo estás hoy? ¿En qué puedo ayudarte?"
    
    # Comentarios
    if any(comentario in mensaje_usuario for comentario in comentarios):
        return random.choice(respuestas_generales)
    
    # Preguntas
    if mensaje_usuario.endswith("?") or "¿" in mensaje_usuario:
        return random.choice(respuestas_preguntas)
    
    # Acuerdos
    if any(termino in mensaje_usuario for termino in ["sí", "si", "claro", "exacto", "totalmente"]):
        return random.choice(respuestas_de_acuerdo)
    
    # Respuesta por defecto
    return random.choice(respuestas_generales)

def main():
    print("="*50)
    print("  BIENVENIDO AL SIMULADOR DE BOT CHAT")
    print("="*50)
    print("Escribe 'salir' para terminar la conversación.")
    print("-"*50)
    
    while True:
        try:
            user_input = input("Tú: ").strip()
            if user_input.lower() == "salir":
                print("Bot: ¡Hasta luego! Que tengas un buen día.")
                break
            
            bot_response = responder_bot(user_input)
            print(f"Bot: {bot_response}")
            print("-"*50)
            
        except KeyboardInterrupt:
            print("\nBot: ¡Hasta pronto!")
            break

if __name__ == "__main__":
    main()
