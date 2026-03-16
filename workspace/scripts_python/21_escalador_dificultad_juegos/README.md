# Escalador de Dificultad para Juegos

## Descripción

Este script es una herramienta interactiva que permite gestionar la dificultad de un juego de preguntas y respuestas. Incluye un sistema para aumentar o disminuir la dificultad, ajustar la puntuación, y ver estadísticas del progreso.

## Características

- **Sistema de Dificultad:** Ajusta la dificultad del juego (Fácil, Medio, Difícil).
- **Niveles Dinámicos:** Cada nivel tiene preguntas, respuestas y puntuación asociada.
- **Persistencia de Datos:** Guarda y carga la configuración del juego en un archivo JSON.
- **Estadísticas:** Muestra el nivel actual, puntuación y configuración del juego.

## Instalación

No requiere instalación adicional. Asegúrate de tener Python 3.x instalado.

## Uso

1. Ejecuta el script:
   ```bash
   python 21_escalador_dificultad_juegos.py
   ```

2. Selecciona una opción del menú:
   - **Jugar:** Responde a las preguntas del nivel actual.
   - **Ajustar dificultad:** Cambia la dificultad del juego (up/down).
   - **Ver estadísticas:** Muestra el progreso y configuración del juego.
   - **Salir:** Cierra la aplicación.

## Dependencias

- `random` (no utilizado actualmente, disponible para futuras expansiones)
- `json`
- `os`

## Estructura de Archivos

- `21_escalador_dificultad_juegos.py`: Script principal.
- `configuracion_juego.json`: Archivo donde se guarda la configuración del juego.
