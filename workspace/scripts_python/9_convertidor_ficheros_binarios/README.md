# 9_convertidor_ficheros_binarios

Un utilitario en Python para inspeccionar archivos binarios, detectar sus firmas mágicas y mostrar información técnica sin depender de librerías externas pesadas.

## Características
- **Información básica**: Tamaño en bytes y humanos, extensión y tipo detectado.
- **Hex Dump**: Visualización de los primeros N bytes en formato hexadecimal.
- **Detección de firmas mágicas**: Identifica si el archivo es realmente un JPEG, PNG, ZIP, PDF, ejecutable Windows, etc., revisando sus bytes iniciales.
- **Modular**: Clases limpias y separación de responsabilidades.

## Requisitos
- Python 3.6+
- `pathlib` (incluido en estándar)
- `argparse` (incluido en estándar)

## Uso
```bash
python 9_convertidor_ficheros_binarios <ruta_archivo>
```

### Ejemplos
```bash
python 9_convertidor_ficheros_binarios imagen.jpg
python 9_convertidor_ficheros_binarios programa.exe -f 32
```

## Salida de ejemplo
```
--- Análisis de: foto.jpg ---
Tamaño: 2.45 MB
Tipo: Imagen

Primeros 10 bytes (Hex): 89504e470d0a1a0a...

Verificación de firma mágica:
  ✓ PNG
  ✓ JPEG
```

### Notas
- No modifica los archivos originales.
- Es ideal para debugging o auditoría rápida de archivos descargados.