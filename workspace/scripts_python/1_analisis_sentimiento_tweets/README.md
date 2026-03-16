# Analizador de Sentimiento Básico

Un script Python que analiza el sentimiento de un texto utilizando un diccionario de palabras clave.

## ¿Qué hace?
- Lee un texto de entrada.
- Detecta palabras positivas y negativas predefinidas.
- Considera signos de puntuación para ponderar la intensidad.
- Clasifica el sentimiento final como Positivo, Negativo o Neutro.

## Cómo usarlo
1. Ejecuta el script directamente:
   ```bash
   python 1_analisis_sentimiento_tweets.py
   ```
2. O importa la función `analizar_sentimiento` en tu propio código:
   ```python
   from 1_analisis_sentimiento_tweets import analizar_sentimiento
   resultado = analizar_sentimiento("Tu texto aquí")
   print(resultado['sentimiento'])
   ```

## Dependencias
- `re` (Regular expressions - estándar en Python)
- `collections` (Counter - estándar en Python)

## Nota
El diccionario de palabras (`PALABRAS_POSITIVAS`, `PALABRAS_NEGATIVAS`) es básico y puede expandirse según las necesidades del proyecto.