# Organizador de Archivos Inteligente

## Descripción
Este script organiza automáticamente un directorio moviendo archivos a carpetas basadas en sus extensiones y nombres, creando una estructura jerárquica lógica.

## Características
- Clasificación por extensión (Código, Imágenes, Audio, Video, Documentos, Datos, etc.)
- Subclasificación inteligente para archivos de texto y código (Scripts, Notas, Config, etc.)
- Gestión de errores segura
- Interfaz por línea de comandos simple

## Cómo usar
1. Asegúrate de tener Python 3.x instalado.
2. Guarda el script como `main.py`.
3. Ejecuta el script en tu terminal:
   ```bash
   python main.py
   ```
4. Sigue las indicaciones para ingresar el directorio de origen y destino.

## Dependencias
- `os` (Estándar)
- `shutil` (Estándar)
- `datetime` (Estándar)
- `pathlib` (Estándar)