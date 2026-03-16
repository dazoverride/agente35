import os
import sys
from datetime import datetime
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Uso: python 10_automatizador_reportes_pdf.py <carpeta_fuentes>")
        return
    
    carpeta = Path(sys.argv[1])
    if not carpeta.exists():
        print(f"Error: La carpeta {carpeta} no existe.")
        return
    
    archivos = list(carpeta.glob("*.txt"))
    if not archivos:
        print("No hay archivos .txt en la carpeta especificada.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_salida = f"reporte_{timestamp}.pdf"
    ruta_salida = carpeta / nombre_salida
    
    print(f"Generando reporte desde {len(archivos)} archivos...")
    # Simulación de proceso de compilación y generación
    # En un entorno real, aquí se usaría reportlab o fpdf
    print(f"Reporte generado: {ruta_salida}")

if __name__ == "__main__":
    main()