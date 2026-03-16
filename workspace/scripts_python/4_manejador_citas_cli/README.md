# Gestor de Citas CLI

Un script de Python interactivo en consola para gestionar citas y reuniones de manera eficiente sin necesidad de interfaces gráficas.

## Características
- **Agregar Citas**: Guarda título, descripción, fecha, hora y duración.
- **Listado Completo**: Muestra todas las citas ordenadas cronológicamente.
- **Filtrado por Fecha**: Consulta específica por una fecha concreta.
- **Gestión de Borrado**: Elimina citas individuales o todas las citas a la vez.
- **Persistencia de Datos**: Las citas se guardan automáticamente en un archivo JSON (`citas.json`), por lo que no se pierden al cerrar el programa.

## Instalación
No requiere instalaciones externas. Solo necesitas Python 3.6+.

## Uso
1. Clona o guarda el archivo `main.py`.
2. Ejecuta el script: `python main.py`
3. Sigue las instrucciones en pantalla para navegar por el menú.

## Estructura de Archivos
- `main.py`: Código fuente principal.
- `citas.json`: Archivo generado automáticamente donde se almacenan los datos.

## Ejemplo de Flujo
```
1. Agregar cita -> Ingresar datos -> Guardar
2. Listar citas -> Ver calendario
3. Filtrar por fecha -> Ver citas de un día
4. Eliminar -> Limpiar agenda
```
