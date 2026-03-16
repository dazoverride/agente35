# Automatizador de Sincronización Cloud (CLI)

## Descripción
Este script es una herramienta CLI que monitorea una carpeta local específica y sincroniza automáticamente los archivos nuevos o modificados con un directorio remoto (simulado en este ejemplo). Utiliza hashes MD5 para detectar cambios eficientemente sin reenviar archivos idénticos.

## Características
- Detección de cambios basada en hash MD5.
- Registro de acciones (subidas y actualizaciones) en un archivo JSON local.
- Filtrado de archivos del sistema y logs propios.
- Interfaz de línea de comandos simple.

## Dependencias
- Python 3.6+
- Librerías estándar (pathlib, json, hashlib, datetime, os, shutil).

## Instalación
No requiere instalación externa. Solo asegúrate de tener Python instalado.

## Uso
1. Asegúrate de tener una carpeta `datos_locale` en tu directorio de ejecución (se creará si no existe).
2. Edita el archivo `config_sincronizacion.json` generado para especificar:
   - `local_folder`: Ruta local a monitorear.
   - `remote_folder`: URL o ruta remota de destino.
3. Ejecuta el script:
   ```bash
   python 33_automatizador_sincronizacion_cloud/main.py
   ```

## Notas
- Actualmente, la conexión remota está simulada. Para producción, integra con APIs de cloud storage (AWS S3, Google Drive, Azure Blob) o FTP/SFTP.
- Los logs se guardan en `logs_sincronizacion.json`.