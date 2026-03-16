# Generador de Reportes Financieros CLI

## Descripción
Herramienta de línea de comandos para analizar transacciones financieras almacenadas en formato JSON y generar reportes consolidados de ingresos, gastos y saldo neto.

## Dependencias
- Python 3.7+
- Sin dependencias externas (librerías estándar)

## Uso
1. Guarda un archivo `transacciones.json` con el formato:
   ```json
   [
     {"fecha": "YYYY-MM-DD", "tipo": "ingreso"|"gasto", "monto": 0.00, "descripcion": "texto"}
   ]
   ```
   O ejecuta el script sin el archivo para usar datos de prueba.

2. Ejecuta:
   ```bash
   python 19_generador_reportes_financieros_cli.py
   ```

3. El script generará un archivo `reporte_financiero.json` y mostrará un resumen en consola.

## Características
- Filtrado por rango de fechas (opcional).
- Cálculo automático de totales.
- Exportación a JSON estructurado.
- Manejo de errores básico.