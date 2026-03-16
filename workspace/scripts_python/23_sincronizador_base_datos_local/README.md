# 23_sincronizador_base_datos_local

## Descripción
Herramienta CLI para comparar dos copias de respaldo (dumps) de bases de datos locales, ya sean en formato JSON o SQLite (SQL), e identificar cambios (nuevos, eliminados o modificados registros).

## Características
- Soporte nativo para archivos JSON (comparación de estructura y datos).
- Soporte básico para archivos SQL/Dump (comparación de líneas de texto).
- Generación automática de reportes en formato Markdown.
- Detección automática de tipo de archivo basado en extensión.

## Dependencias
- Python 3.6+
- Librerías estándar de Python (`json`, `sqlite3`, `difflib`). No requiere instalación externa.

## Cómo usar
1. Asegúrate de tener dos archivos de respaldo (ej: `backup_v1.json`, `backup_v2.json`).
2. Ejecuta el script en la carpeta donde están los archivos:

   ```bash
   python3 23_sincronizador_base_datos_local.py backup_v1.json backup_v2.json
   ```

3. El script generará un archivo `diff_report.md` con los cambios detectados.

## Ejemplos
- Comparar versiones JSON: `python3 23_sincronizador_base_datos_local.py data_old.json data_new.json`
- Comparar dumps SQL: `python3 23_sincronizador_base_datos_local.py db_old.sql db_new.sql`
