import random
import time
import requests
from datetime import datetime

class BotNubeAutomatizada:
    """Simula un bot de atención al cliente que atiende múltiples 'clientes' simultáneamente
    gestionando filas, respuestas aleatorias y tiempos de espera."""
    
    def __init__(self):
        self.preguntas_frecuentes = [
            "¿Cuál es la política de devoluciones?",
            "¿Cómo puedo cambiar mi contraseña?",
            "¿Tienen ofertas disponibles?",
            "¿Cómo contacto soporte técnico?",
            "¿Qué métodos de pago aceptan?"
        ]
        self.respuestas_frecuentes = [
            "Nuestra política de devoluciones es de 30 días.",
            "Puede cambiar su contraseña desde la configuración de perfil.",
            "Sí, tenemos ofertas especiales esta semana.",
            "El soporte técnico está disponible 24/7 por este mismo chat.",
            "Aceptamos tarjetas de crédito, débito y PayPal."
        ]
        
    def generar_respuesta(self, pregunta):
        """Genera una respuesta aleatoria basada en la pregunta del usuario."""
        if pregunta.lower() in [p.lower() for p in self.preguntas_frecuentes]:
            return random.choice(self.respuestas_frecuentes)
        else:
            return "Lo siento, no estoy seguro de entender su pregunta. Por favor, reformule."

    def simular_atencion(self, num_clientes=5):
        """Simula la atención a múltiples clientes simultáneamente."""
        print(f"Iniciando simulación de atención a {num_clientes} clientes...")
        print("=" * 50)
        
        for i in range(1, num_clientes + 1):
            print(f"\n--- Cliente {i} ---")
            print(f"Tiempo de llegada: {datetime.now().strftime('%H:%M:%S')}")
            
            # Simular preguntas del cliente
            for _ in range(random.randint(2, 4)):
                pregunta = random.choice(self.preguntas_frecuentes)
                print(f"Cliente {i}: {pregunta}")
                
                respuesta = self.generar_respuesta(pregunta)
                print(f"Bot: {respuesta}")
                
                # Simular tiempo de espera entre preguntas
                time.sleep(random.uniform(0.5, 1.5))
        
        print("\n" + "=" * 50)
        print("Simulación finalizada.")
        print("Total de clientes atendidos: " + str(num_clientes))

if __name__ == "__main__":
    bot = BotNubeAutomatizada()
    bot.simular_atencion(10)
