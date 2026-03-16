# 20_analisis_red_social_nodos

## Descripción
Herramienta CLI avanzada para analizar estructuras de redes sociales basadas en grafos. Permite calcular métricas como centralidad de grado, densidad de la red, detectar componentes conexos y encontrar el camino más corto entre nodos.

## Instalación
No requiere dependencias externas. Solo Python 3.6+.

## Uso
1. Asegúrate de tener un archivo JSON con la estructura:
   ```json
   {
     "aristas": [
       ["usuario_A", "usuario_B"],
       ["usuario_B", "usuario_C"]
     ]
   }
   ```
   (El campo "nodos" es opcional, se infieren de las aristas).

2. Ejecutar reporte general:
   ```bash
   python main.py red_social.json reporte
   ```

3. Buscar camino más corto:
   ```bash
   python main.py red_social.json camino usuario_A usuario_C
   ```

## Características
- Análisis de centralidad para identificar nodos más influyentes.
- Detección automática de comunidades desconectadas.
- Búsqueda de caminos óptimos (BFS).
- Salida en consola formateada.