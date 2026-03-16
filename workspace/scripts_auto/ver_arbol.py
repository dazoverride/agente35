# DESCRIPCION: Muestra la estructura de directorios y archivos. Argumentos: <directorio> [max_profundidad (opcional, por defecto 3)]
import sys
import os

if len(sys.argv) < 2:
    print("Uso: python ver_arbol.py <directorio> [max_profundidad]")
    sys.exit(1)

dir_path = sys.argv[1]
max_prof = int(sys.argv[2]) if len(sys.argv) > 2 else 3

def print_tree(startpath, max_depth):
    if not os.path.exists(startpath):
        print(f"Error: El directorio '{startpath}' no existe.")
        return
        
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        if level > max_depth:
            del dirs[:]
            continue
            
        # Ocultar carpetas no deseadas o de cachés
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'db', 'models', 'workspace']]
        
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        
        for f in files[:20]: # Límite de archivos mostrados por carpeta para no saturar 
            print(f"{subindent}{f}")
        if len(files) > 20:
            print(f"{subindent}... y {len(files)-20} archivos más")

try:
    print(f"Árbol de directorios para: {dir_path} (Profundidad Máx: {max_prof})\n")
    print_tree(dir_path, max_prof)
except Exception as e:
    print(f"Error al generar el árbol: {e}")
