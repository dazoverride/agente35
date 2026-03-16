# Simulador de Ciberataque a Red (ID 26)

Un script de Python para simular escenarios de ataques DDoS y respuestas defensivas en una red de servidores ficticia.

## Descripción
Este programa simula una red de servidores y genera ataques distribuidos (DDoS) aleatorios con diferentes tipos (SYN, UDP, Amplificación). También incluye un módulo de defensa que bloquea un porcentaje aleatorio de los ataques.

## Características
- Generación de IPs aleatorias para atacantes y servidores.
- Simulación de múltiples tipos de ataques DDoS.
- Sistema de defensa básico que bloquea ataques.
- Registro de logs detallados con timestamps.
- Reporte final con estadísticas y últimos eventos.

## Cómo ejecutar
1. Asegúrate de tener Python 3 instalado.
2. Guarda el código como `main.py`.
3. Ejecuta en terminal:
   ```bash
   python main.py
   ```

## Dependencias
- `python` (versión 3.x)
- Librerías estándar (sin dependencias externas).

## Salida
Genera un reporte en consola con:
- Cantidad total de ataques.
- Cantidad de ataques bloqueados.
- Últimos 10 logs de eventos (ataques y defensas).
