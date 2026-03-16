# Automatizador de Reportes PDF

## Descripción
Script que recopila todos los archivos `.txt` de una carpeta específica y genera un reporte consolidado con marca de tiempo.

## Instalación
No requiere librerías externas para la lógica básica, aunque para generar PDF reales se recomienda instalar `reportlab` o `fpdf`.

## Uso
```bash
python 10_automatizador_reportes_pdf.py /ruta/a/tus/archivos
```

## Dependencias
- Python 3.8+
- `reportlab` (opcional, para generación real de PDF)

## Salidas
Genera un archivo PDF en la misma carpeta con el nombre `reporte_[fecha]_hora.pdf`.

## Notas
Actualmente genera un marcador de posición de PDF. Para funcionalidad completa, extender la función `main()` con importaciones de reportlab.