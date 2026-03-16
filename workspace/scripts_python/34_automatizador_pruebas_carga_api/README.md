# Automatizador de Pruebas de Carga API

## Descripción
Este script simula una carga de trabajo controlada contra una API REST pública (JSONPlaceholder). Realiza solicitudes aleatorias a diferentes endpoints, registra tiempos de respuesta, códigos de estado y genera un informe detallado en formato JSON.

## Funcionalidades
- Simulación de tráfico HTTP GET aleatorio.
- Parámetros dinámicos (userId, postId) para variar las peticiones.
- Registro de latencia y estado por solicitud.
- Generación automática de reportes JSON con estadísticas agregadas.

## Requisitos
- Python 3.6+
- Librería: `requests`

## Instalación
```bash
pip install requests
```

## Uso
Ejecuta el script directamente:
```bash
python 34_automatizador_pruebas_carga_api.py
```

## Parámetros Configurables (dentro del código)
- `BASE_URL`: URL de la API objetivo.
- `NUM_REQUESTS`: Cantidad total de peticiones a simular.
- `DELAY_BASE`: Retraso máximo entre peticiones para evitar rate limiting.

## Salida
Genera un archivo JSON con la estructura:
- `fecha_inicio`, `fecha_fin`
- `total_solicitudes`, `exitos`, `fallos`
- `datos_muestral`: Lista detallada de cada solicitud realizada.
- Métricas de tiempo promedio.