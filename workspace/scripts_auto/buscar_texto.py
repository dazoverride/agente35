# DESCRIPCION: Busca una cadena de texto en los archivos de un directorio y subdirectorios. Argumentos: <texto_a_buscar> <directorio>
import sys
import os

if len(sys.argv) < 3:
    print("Uso: python buscar_texto.py <texto_a_buscar> <directorio>")
    sys.exit(1)

texto_buscado = sys.argv[1]
directorio = sys.argv[2]
resultados = []

try:
    if not os.path.exists(directorio):
        print(f"Error: El directorio '{directorio}' no existe.")
        sys.exit(1)
        
    for root, _, files in os.walk(directorio):
        # Evitar buscar en carpetas inútiles para el usuario, ocultas o entornos virtuales
        if any(part.startswith('.') for part in root.split(os.sep)) or '__pycache__' in root or 'node_modules' in root:
            continue
            
        for file in files:
            # Filtro básico: Archivos legibles
            if file.endswith(('.py', '.txt', '.md', '.json', '.html', '.js', '.css', '.ini', '.csv')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for i, linea in enumerate(f, 1):
                            if texto_buscado.lower() in linea.lower():
                                resultados.append(f"{filepath}:{i}: {linea.strip()}")
                except Exception:
                    pass

    if resultados:
        print(f"Búsqueda finalizada. Encontrados {len(resultados)} resultados.")
        for r in resultados[:50]: # Límite de resultados
            print(r)
        if len(resultados) > 50:
            print(f"\n...Y {len(resultados) - 50} resultados más mostrados.")
    else:
        print(f"No se encontró '{texto_buscado}' en {directorio}")
        
except Exception as e:
    print(f"Error al buscar: {e}")
