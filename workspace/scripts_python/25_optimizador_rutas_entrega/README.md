# Optimizador de Rutas de Entrega

## Descripción
Herramienta CLI que optimiza rutas de entrega utilizando el algoritmo de "Vecino Más Cercano" para minimizar la distancia total recorrida desde un centro de distribución hacia múltiples puntos de entrega.

## Dependencias
- `json` (incluida en Python)
- `csv` (incluida en Python)
- `math` (incluida en Python)

## Uso
1. **Preparar datos**: Crea un archivo `entregas.json` con el siguiente formato:
   ```json
   {
     "entregas": [
       {"id": 1, "coordenadas": "40.4168,-3.7038", "cliente": "Cliente A"},
       {"id": 2, "coordenadas": "40.4200,-3.7100", "cliente": "Cliente B"},
       {"id": 3, "coordenadas": "40.4100,-3.6900", "cliente": "Cliente C"}
     ]
   }
   ```

2. **Ejecutar el script**:
   ```bash
   python 25_optimizador_rutas_entrega.py
   ```

3. **Resultado**: Se generará un archivo `ruta_optimizada.csv` con el orden sugerido de entrega y la distancia acumulada.

## Notas
- Las coordenadas se asumen en un sistema cartesiano simplificado (lat/lon aproximadas).
- El algoritmo es heurístico y no garantiza la solución óptima global, pero funciona bien para instancias pequeñas a medianas.