# Analizador de Patrones de Texto (ID: 28)

## Descripción
Herramienta CLI para analizar patrones ocultos en textos: detecta palabras repetidas, emails, URLs, fechas y estructura básica (oraciones/párrafos). Exporta resultados a JSON.

## Cómo ejecutar
1. Asegúrate de tener Python 3.x instalado.
2. Ejecuta: `python 28_analisis_patrones_texto/main.py`
3. Introduce un texto o 'fin' para terminar.

## Dependencias
- `re` (Regex)
- `json` (Estándar)
- `collections` (Estándar)

## Características
- Detección de entidades (email, URL, fechas)
- Conteo de palabras repetidas
- Análisis estructural (oraciones/párrafos)
- Exportación automática a JSON