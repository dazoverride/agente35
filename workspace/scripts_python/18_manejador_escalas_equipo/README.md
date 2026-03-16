# 18_manejador_escalas_equipo

## Descripción
Una herramienta CLI para gestionar escalas de trabajo y personal de un equipo, con persistencia de datos en JSON.

## Características
- Registro de miembros del personal con roles.
- Creación de escalas con nombre, duración y asignación de miembros.
- Listado de escalas activas basadas en la fecha actual.
- Finalización de escalas.
- Persistencia de datos en `escalas_equipo.json`.

## Instalación
No requiere dependencias externas. Ejecutable directamente con Python 3.

## Uso
1. Clona o ejecuta el script.
2. Selecciona opciones del menú principal:
   - Agregar miembro al personal.
   - Crear nueva escala.
   - Listar escalas activas.
   - Finalizar escala.
   - Salir.

## Ejemplo de uso
```bash
python 18_manejador_escalas_equipo/main.py
```

## Estructura de datos
- `escalas`: Lista de diccionarios con información de cada escala.
- `personal`: Diccionario con nombres como claves y roles/asignaciones como valores.
