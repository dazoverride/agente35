# Compilador de Lenguaje Simple (DSL)

## Descripción
Un compilador interpretador básico escrito en Python que procesa un lenguaje de dominio específico (DSL) para operaciones simples de programación como variables, funciones básicas, impresión y operaciones aritméticas.

## Características
- **Tokenización**: Desglosa el código fuente en tokens (identificadores, números, operadores).
- **Gestión de Variables**: Soporta declaración y asignación de variables numéricas y de cadena.
- **Funciones**: Permite definir funciones simples (aunque la ejecución de su cuerpo es simulada en esta demo).
- **Importación**: Simula la importación de módulos.
- **Salida y Errores**: Devuelve la salida estándar y una lista de errores de sintaxis.

## Dependencias
- Python 3.x
- No requiere librerías externas (solo `sys`, `os`, `typing`).

## Cómo usar
1. Guarda el código en un archivo llamado `main.py`.
2. Ejecuta el script directamente:
   ```bash
   python main.py
   ```
3. El script incluirá un bloque de código de prueba (`test_code`) en su interior. Puedes modificar `test_code` para probar otras combinaciones de instrucciones del DSL.

## Sintaxis del DSL (Ejemplos)
- `var nombre = "Hola";` (Declaración de variable)
- `print "Texto";` (Imprimir texto)
- `var x = 10 + 5;` (Asignación con operación)
- `func miFuncion() { ... }` (Definición de función)
- `import math;` (Importar módulo)

## Notas
Este compilador es una demostración educativa de cómo funciona la tokenización y el análisis léxico. No es un compilador completo para producción, ya que la ejecución de bloques complejos (como el cuerpo de funciones) está simulada.