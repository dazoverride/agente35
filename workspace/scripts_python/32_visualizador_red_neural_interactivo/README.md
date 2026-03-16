# Visualizador de Red Neurale Interactivo

Herramienta CLI para generar topologías de redes neuronales aleatorias, calcular métricas estructurales (densidad, grado, agrupamiento) y visualizarlas mediante ASCII art.

## Dependencias
- Python 3.6+
- No requiere librerías externas (`dataclasses`, `json`, `random` son estándar).

## Cómo ejecutar
```bash
python visualizador_red_neural_interactivo.py
```

## Funcionalidades
1. Generación aleatoria de capas y nodos.
2. Conexiones ponderadas con sesgo y función de activación.
3. Cálculo de métricas: Densidad, Grado Promedio, Coeficiente de Agrupamiento.
4. Exportación a JSON.
5. Visualización gráfica en texto.