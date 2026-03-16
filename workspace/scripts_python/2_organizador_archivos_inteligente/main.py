import os
import shutil
import datetime
from pathlib import Path

def categorizar_archivo(ruta_archivo):
    """Determina la categoría basada en la extensión del archivo."""
    ext = Path(ruta_archivo).suffix.lower()
    categorias = {
        '.py': 'Código',
        '.txt': 'Documentos',
        '.md': 'Documentos',
        '.pdf': 'Documentos',
        '.jpg', '.jpeg', '.png', '.gif': 'Imágenes',
        '.mp4', '.avi', '.mov': 'Videos',
        '.mp3', '.wav': 'Audio',
        '.json': 'Datos',
        '.xml': 'Datos',
        '.csv': 'Datos'
    }
    return categorias.get(ext, 'Otro')

def obtener_subcategoria(ruta_archivo, categoria):
    """Obtiene una subcategoría más específica para archivos de texto o código."""
    if categoria not in ['Código', 'Documentos', 'Datos']:
        return None
    
    nombre = Path(ruta_archivo).name
    if '.py' in nombre:
        return 'Scripts' if 'main' in nombre else 'Módulos'
    elif '.txt' in nombre or '.md' in nombre:
        return 'Lectura' if 'readme' in nombre.lower() else 'Notas'
    elif '.json' in nombre:
        return 'Config' if 'config' in nombre.lower() else 'BaseDatos'
    return 'General'

def organizar_directorio(directorio_origen, directorio_destino):
    """Organiza archivos del origen al destino basado en categorías."""
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)
    
    for archivo in os.listdir(directorio_origen):
        ruta_completa = os.path.join(directorio_origen, archivo)
        
        if os.path.isfile(ruta_completa):
            categoria = categorizar_archivo(ruta_completa)
            subcategoria = obtener_subcategoria(ruta_completa, categoria)
            
            if subcategoria:
                directorio_final = os.path.join(directorio_destino, categoria, subcategoria)
                if not os.path.exists(directorio_final):
                    os.makedirs(directorio_final)
                shutil.move(ruta_completa, directorio_final)
                print(f"Movido: {archivo} -> {categoria}/{subcategoria}")
            else:
                print(f"No categorizado: {archivo}")

if __name__ == "__main__":
    print("Iniciando Organizador Inteligente de Archivos...")
    origen = input("Ingrese el directorio a organizar (o 'C:' para el sistema): ").strip()
    destino = input("Ingrese el directorio de destino: ").strip()
    
    if origen.lower() == 'c:':
        origen = os.getcwd()
    
    organizar_directorio(origen, destino)
    print("Organización completada.")