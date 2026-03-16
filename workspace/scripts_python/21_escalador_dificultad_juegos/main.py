import random
import json
import os

class EscaladorDificultad:
    def __init__(self, ruta_archivo):
        self.ruta = ruta_archivo
        self.juego_actual = None
        self.nivel_actual = 1
        self.puntuacion = 0
        self.carga_juego()

    def cargar_juego(self):
        """Carga la configuración del juego desde un archivo JSON o genera uno por defecto."""
        if os.path.exists(self.ruta):
            with open(self.ruta, 'r') as f:
                self.juego_actual = json.load(f)
        else:
            self.juego_actual = {
                "nombre": "Desafío de Lógica",
                "niveles": [
                    {"id": 1, "pregunta": "¿Cuánto es 2 + 2?", "respuesta": "4", "puntos": 10},
                    {"id": 2, "pregunta": "¿Capital de Francia?", "respuesta": "paris", "puntos": 20},
                    {"id": 3, "pregunta": "¿Elemento químico 'O'?", "respuesta": "oxigeno", "puntos": 30},
                    {"id": 4, "pregunta": "¿Año de llegada del hombre a la Luna?", "respuesta": "1969", "puntos": 40},
                    {"id": 5, "pregunta": "¿Quién pintó la Mona Lisa?", "respuesta": "leonardo", "puntos": 50}
                ],
                "dificultad": "facil"
            }
            self.guardar_juego()

    def guardar_juego(self):
        """Guarda la configuración del juego."""
        with open(self.ruta, 'w') as f:
            json.dump(self.juego_actual, f, indent=4)

    def ajustar_dificultad(self, direccion):
        """Aumenta o disminuye la dificultad y ajusta los niveles."""
        if direccion == 'up':
            if self.juego_actual["dificultad"] == "facil":
                self.juego_actual["dificultad"] = "medio"
                self.nivel_actual = 1
                self.puntuacion = 0
                print("Dificultad aumentada a: Medio. Reiniciando nivel.")
            elif self.juego_actual["dificultad"] == "medio":
                self.juego_actual["dificultad"] = "difícil"
                self.nivel_actual = 1
                self.puntuacion = 0
                print("Dificultad aumentada a: Difícil. Reiniciando nivel.")
            else:
                print("Ya estás en la dificultad máxima.")
        elif direccion == 'down':
            if self.juego_actual["dificultad"] == "facil":
                print("Ya estás en la dificultad mínima.")
            else:
                if self.juego_actual["dificultad"] == "medio":
                    self.juego_actual["dificultad"] = "facil"
                    self.nivel_actual = 1
                    self.puntuacion = 0
                    print("Dificultad reducida a: Fácil. Reiniciando nivel.")
                elif self.juego_actual["dificultad"] == "difícil":
                    self.juego_actual["dificultad"] = "medio"
                    self.nivel_actual = 1
                    self.puntuacion = 0
                    print("Dificultad reducida a: Medio. Reiniciando nivel.")
        self.guardar_juego()

    def jugar(self):
        """Juega el nivel actual."""
        if not self.juego_actual["niveles"]:
            print("No hay niveles disponibles.")
            return

        nivel = self.juego_actual["niveles"][self.nivel_actual - 1]
        print(f"\n--- Nivel {self.nivel_actual}: {nivel['pregunta']} ---")
        respuesta = input("Tu respuesta: ").strip().lower()

        if respuesta == nivel['respuesta'].lower():
            print("¡Correcto!")
            self.puntuacion += nivel['puntos']
            self.nivel_actual += 1
            if self.nivel_actual > len(self.juego_actual["niveles"]):
                print("¡Felicidades! Has completado todos los niveles.")
            else:
                input("Presiona Enter para continuar...")
        else:
            print(f"Incorrecto. La respuesta era: {nivel['respuesta']}")
            print(f"Puntuación actual: {self.puntuacion}")
            self.nivel_actual -= 1
            if self.nivel_actual <= 0:
                print("Game Over. Reiniciando...")
                self.nivel_actual = 1
                self.puntuacion = 0
                input("Presiona Enter para continuar...")

    def mostrar_estadisticas(self):
        """Muestra estadísticas del juego."""
        print(f"\n=== Estadísticas ===")
        print(f"Juego: {self.juego_actual['nombre']}")
        print(f"Dificultad: {self.juego_actual['dificultad']}")
        print(f"Nivel actual: {self.nivel_actual}/{len(self.juego_actual['niveles'])}")
        print(f"Puntuación total: {self.puntuacion}")
        print(f"Puntuación por nivel: {[n['puntos'] for n in self.juego_actual['niveles']]}")

    def menu(self):
        """Muestra el menú principal."""
        while True:
            print("\n=== Menú ===")
            print("1. Jugar")
            print("2. Ajustar dificultad (Arriba/Abajo)")
            print("3. Ver estadísticas")
            print("4. Salir")
            opcion = input("Selecciona una opción: ").strip()

            if opcion == '1':
                self.jugar()
            elif opcion == '2':
                print("¿Dificultad? (up/down): ")
                cambio = input().strip().lower()
                self.ajustar_dificultad(cambio)
            elif opcion == '3':
                self.mostrar_estadisticas()
            elif opcion == '4':
                print("Saliendo...")
                break
            else:
                print("Opción no válida.")

if __name__ == "__main__":
    juego_ruta = "configuracion_juego.json"
    escalador = EscaladorDificultad(juego_ruta)
    escalador.menu()
