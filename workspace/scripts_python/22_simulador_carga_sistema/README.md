# 22_simulador_carga_sistema

## Descripción
Un simulador CLI que modela la carga de CPU y RAM de servicios ficticios en tiempo real, incluyendo fallos aleatorios y recuperación.

## Características
- Simulación en tiempo real de carga de recursos (CPU/RAM).
- Detección aleatoria de errores y estados inestables.
- Visualización gráfica de barras de progreso.
- Persistencia del estado final en JSON.

## Dependencias
- Python 3.6+

## Uso
```bash
# Iniciar simulación
python 22_simulador_carga_sistema/main.py

# Iniciar simulación cargando el estado de una ejecución anterior
python 22_simulador_carga_sistema/main.py --load
```

## Nota
Este script es una herramienta de demostración para visualizar cómo podría comportarse un sistema bajo carga variable y fallos aleatorios.