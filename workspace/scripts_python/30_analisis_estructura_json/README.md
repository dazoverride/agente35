# Analizador de Estructura JSON (ID 30)

## Descripción
Herramienta CLI que inspecciona archivos JSON para extraer estadísticas sobre su estructura interna, tipos de datos, anidamiento y claves únicas. Ideal para validar formatos de datos antes de procesarlos en pipelines de datos.

## Características
- Análisis recursivo profundo de la estructura JSON.
- Estadísticas globales: tipo de raíz, conteo de tipos (dict, list, str, int, etc.), longitud promedio de listas.
- Detección de claves únicas.
- Salida en formato legible en consola.

## Requisitos
- Python 3.6+
- Sin dependencias externas (solo librerías estándar).

## Instalación
No requiere instalación. Solo guardar el código en un archivo `.py`.

## Uso
```bash
python 30_analisis_estructura_json/main.py <ruta_al_archivo.json>
```

## Ejemplo
```bash
python 30_analisis_estructura_json/main.py datos_usuarios.json
```

## Salidas Esperadas
- Mensajes en consola con resumen estadístico.
- Representación JSON de la estructura recorrida (opcional, según configuración futura).
