# DESCRIPCION: Lee un rango específico de líneas de un archivo. Argumentos: <archivo> <linea_inicio> <linea_fin>
import sys
import os

if len(sys.argv) < 4:
    print("Uso: python leer_lineas.py <archivo> <linea_inicio> <linea_fin>")
    sys.exit(1)

archivo = sys.argv[1]
try:
    if not os.path.exists(archivo):
        print(f"Error: El archivo '{archivo}' no existe.")
        sys.exit(1)
        
    inicio = int(sys.argv[2]) - 1 # 0-indexed para el array
    fin = int(sys.argv[3])
    
    with open(archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
        
    if inicio < 0 or fin > len(lineas):
        print(f"Aviso: El archivo tiene {len(lineas)} líneas. Ajustando rango.")
        inicio = max(0, inicio)
        fin = min(len(lineas), fin)
        
    seleccion = lineas[inicio:fin]
    
    print(f"Mostrando {archivo} (Líneas {inicio+1} - {fin}):")
    print("-" * 40)
    for i, linea in enumerate(seleccion, inicio + 1):
        print(f"{i:4d} | {linea}", end='')
    print("\n" + "-" * 40)
        
except Exception as e:
    print(f"Error al leer líneas: {e}")
