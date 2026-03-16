# Buscador de Recetas Nutricionales

Un script en Python para buscar y filtrar recetas basándose en su nombre y contenido calórico.

## Características
- **Base de datos integrada**: Incluye 5 recetas de ejemplo con sus ingredientes y calorías.
- **Búsqueda flexible**: Busca recetas por nombre usando coincidencia parcial.
- **Filtrado nutricional**: Permite filtrar resultados por un límite máximo de calorías.
- **Interfaz de línea de comando**: Fácil de ejecutar desde la terminal.

## Requisitos
- Python 3.6+

## Instalación
No requiere instalación de librerías externas. Simplemente ejecuta el script.

## Uso
1. Asegúrate de tener Python instalado.
2. Guarda el código en un archivo llamado `main.py`.
3. Ejecuta el script:
   ```bash
   python main.py
   ```
4. Sigue las instrucciones en pantalla para buscar recetas o filtrar por calorías.

## Ejemplos de uso
- Buscar "pasta" y luego filtrar por menos de 400 calorías.
- Ver todas las recetas con menos de 300 calorías.

## Estructura del código
- `Receta`: Clase que almacena los datos de una receta.
- `BuscadorRecetas`: Clase que gestiona la base de datos y las operaciones de búsqueda/filtrado.
- `main`: Función principal que maneja la interacción con el usuario.