# Minimizador de Consumo de Energía

Un script de diagnóstico rápido para monitorizar el uso de recursos del sistema (CPU, RAM, Disco) con fines de auditoría de eficiencia energética.

## Características
- **Ligero**: Utiliza `psutil` para obtener métricas instantáneas sin sobrecargar el sistema.
- **No Intrusivo**: Solo lee el estado actual; no altera ni reinicia procesos.
- **Salida Formateada**: Presenta los datos en una tabla clara para análisis rápido.

## Instalación
Asegúrate de tener instalado `psutil`:
```bash
pip install psutil
```

## Uso
Ejecuta el script directamente:
```bash
python 13_minimizador_consumo_energia/main.py
```

## Dependencias
- `psutil`
- `datetime` (biblioteca estándar)