# Automatizador de Ubicación GPS

## Descripción
Este script es una herramienta CLI para registrar, gestionar y exportar logs de ubicación GPS con soporte para actividades y altitud. Es ideal para rastrear rutas, auditorías de ubicación o pruebas de dispositivos móviles.

## Características
- Registro de coordenadas lat/lon con timestamp.
- Soporte para altitud y etiquetado de actividad.
- Persistencia de datos en formato JSON.
- Exportación a CSV para análisis externo.
- Filtrado de registros por tipo de actividad.

## Dependencias
No requiere librerías externas. Solo Python 3.x.

## Cómo ejecutar
Guarda el código en `main.py` y ejecuta:
```bash
python main.py
```

## Uso
1. Selecciona la opción 1 para registrar coordenadas.
2. Usa la opción 2 para ver los últimos registros.
3. Filtra por actividad con la opción 3.
4. Exporta todo el historial a CSV con la opción 4.

## Archivos generados
- `gps_logs.json`: Almacena todos los registros.
- `gps_export.csv`: Archivo de exportación en formato CSV.