# Bot Nube Automatizada

## Descripción
Este script simula un bot de atención al cliente en la nube que gestiona múltiples clientes simultáneamente, procesando preguntas frecuentes y generando respuestas automáticas.

## Funcionalidades
- Simulación de múltiples clientes llegando al chat.
- Generación de respuestas aleatorias para preguntas frecuentes.
- Registro de tiempos de llegada y respuestas.
- Interfaz de texto simple para visualizar la simulación.

## Dependencias
- `requests` (opcional, no usado actualmente pero incluído por estándar)
- `datetime` (built-in)
- `random` (built-in)

## Cómo Ejecutar
1. Asegúrate de tener Python 3.x instalado.
2. Instala las dependencias si es necesario (aunque este script no las requiere):
   ```bash
   pip install requests
   ```
3. Ejecuta el script:
   ```bash
   python bot_nube_automatizada.py
   ```

## Notas
- El bot genera respuestas aleatorias para preguntas frecuentes.
- Los tiempos de espera entre preguntas son simulados.
- Puedes ajustar el número de clientes en el `main()` para probar diferentes escenarios.