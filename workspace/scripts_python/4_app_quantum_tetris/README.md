# Quantum Tetris

Una variante futurista del clásico Tetris donde las piezas tienen propiedades cuánticas.

## Características
- **Superposición**: Las piezas rotadas tienen un 10% de probabilidad de entrar en un estado de superposición (visuales fantasma).
- **Colapso**: Al chocar o rotar, la pieza "colapsa" a un estado definido, cambiando su forma y color aleatoriamente.
- **Fusión**: Si una pieza superpuesta choca con otra, ambas se fusionan en un bloque blanco inestable.

## Cómo Jugar
- **Flechas Izquierda/Derecha**: Mover pieza.
- **Flecha Abajo**: Acelerar caída.
- **Flecha Arriba**: Rotar pieza (puede activar superposición).
- **Espacio**: Bajar pieza al instante.
- **R**: Reiniciar el juego tras Game Over.

## Requisitos
- Python 3.x
- Librería `pygame` (`pip install pygame`)

## Instrucciones de Ejecución
```bash
python main.py
```