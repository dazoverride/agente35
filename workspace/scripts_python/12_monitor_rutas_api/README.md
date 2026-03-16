# Monitor de Rutas API

Un script ligero para probar la disponibilidad y el estado de endpoints de una API REST.

## ¿Qué hace?
1. **Descarga el inventario**: Intenta leer el archivo de rutas (generalmente de Swagger/OpenAPI) de la API base.
2. **Prueba de salud**: Ejecuta solicitudes GET rápidas a cada ruta declarada.
3. **Reporte**: Muestra un resumen de códigos de estado y tiempos de respuesta.

## Instalación
No requiere dependencias externas, pero necesita `requests`.
```bash
pip install requests
```

## Uso
```bash
# Probar una ruta específica
python 12_monitor_rutas_api.py http://localhost:8000 /users

# Escanear todas las rutas disponibles
python 12_monitor_rutas_api.py http://localhost:8000
```

## Dependencias
- `requests`
