# 14_sincronizador_carpeta_diff

## Descripción
Herramienta CLI en Python para comparar el contenido y la estructura de dos carpetas locales. Identifica archivos únicos en cada lado y detecta diferencias en el contenido de los archivos comunes.

## Características
- Comparación recursiva de carpetas.
- Detección de archivos exclusivos (solo origen / solo destino).
- Detección de archivos comunes con contenido diferente.
- Modo seguro por defecto (visualización sin modificar archivos).
- Manejo de errores en lectura de archivos.

## Dependencias
- Python 3.7+
- Librerías estándar: `pathlib`, `os`, `sys`, `datetime`, `difflib`

## Cómo usar
1. Clona o guarda el archivo `main.py`.
2. Abre una terminal en la carpeta del proyecto.
3. Ejecuta:
   ```bash
   python main.py <carpeta_origen> <carpeta_destino>
   ```

## Ejemplo
```bash
python main.py /home/user/documentos/proyecto_a /home/user/documentos/proyecto_b
```

## Salidas
- Lista de archivos solo presentes en la carpeta de origen.
- Lista de archivos solo presentes en la carpeta de destino.
- Lista de archivos comunes.
- Lista de archivos comunes que tienen contenido diferente.

## Notas
- Por defecto, el script no mueve ni copia archivos. Solo informa sobre las diferencias.
- Los archivos muy grandes (>10KB) pueden ser omitidos en la comparación de contenido para optimizar memoria.