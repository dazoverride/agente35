import json
import sys
import os
from collections import Counter, defaultdict

def analizar_estructura_json(ruta_archivo):
    """
    Analiza la estructura profunda de un archivo JSON.
    Retorna estadísticas sobre tipos de datos, anidamiento y claves únicas.
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {"error": f"El archivo no es un JSON válido: {e}", "estructura": None}
    except FileNotFoundError:
        return {"error": "Archivo no encontrado", "estructura": None}

    # Función recursiva para analizar tipos y conteo
    def recursivo_analisis(obj, profundidad=0):
        info_obj = {"tipo": type(obj).__name__, "profundidad": profundidad, "clave": None}
        
        if isinstance(obj, dict):
            info_obj["clave"] = list(obj.keys())[0] if len(obj) == 1 else "multiple"
            info_obj["es_dict"] = True
            info_obj["num_claves"] = len(obj)
            for key, value in obj.items():
                recursivo_analisis(value, profundidad + 1)
        elif isinstance(obj, list):
            info_obj["es_list"] = True
            info_obj["longitud"] = len(obj)
            for item in obj:
                recursivo_analisis(item, profundidad + 1)
        elif isinstance(obj, (str, int, float, bool, type(None))):
            info_obj["es_primitivo"] = True
            if isinstance(obj, str):
                info_obj["es_cadena"] = True
            elif isinstance(obj, int):
                info_obj["es_entero"] = True
            elif isinstance(obj, float):
                info_obj["es_float"] = True
            elif isinstance(obj, bool):
                info_obj["es_bool"] = True
            elif obj is None:
                info_obj["es_none"] = True
        
        return info_obj

    # Análisis completo
    estructura_completa = recursivo_analisis(data)
    
    # Estadísticas globales
    tipos_contador = Counter()
    max_profundidad = 0
    claves_unicas = set()
    longitud_listas = []
    
    def extraer_estadisticas(obj):
        nonlocal max_profundidad
        if isinstance(obj, dict):
            tipos_contador['dict'] += 1
            claves_unicas.update(obj.keys())
            for key, value in obj.items():
                if isinstance(value, list):
                    longitud_listas.append(len(value))
                extraer_estadisticas(value)
        elif isinstance(obj, list):
            tipos_contador['list'] += 1
            longitud_listas.append(len(obj))
            for item in obj:
                extraer_estadisticas(item)
        else:
            tipos_contador[type(obj).__name__] += 1
            if isinstance(obj, dict) or isinstance(obj, list):
                max_profundidad = max(max_profundidad, 1)

    extraer_estadisticas(data)
    
    estadisticas = {
        "tipo_raiz": type(data).__name__,
        "total_claves_unicas": len(claves_unicas),
        "longitud_promedio_listas": sum(longitud_listas) / len(longitud_listas) if longitud_listas else 0,
        "profundidad_estimada": max_profundidad + 1,
        "distribucion_tipos": dict(tipos_contador)
    }

    return {"estructura": estructura_completa, "estadisticas": estadisticas}

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <ruta_archivo.json>")
        sys.exit(1)

    archivo = sys.argv[1]
    resultado = analizar_estructura_json(archivo)

    if "error" in resultado:
        print(f"ERROR: {resultado['error']}")
        sys.exit(1)

    print(f"=== Análisis de Estructura JSON: {os.path.basename(archivo)} ===")
    print(f"Tipo de raíz: {resultado['estadisticas']['tipo_raiz']}")
    print(f"Total de claves únicas: {resultado['estadisticas']['total_claves_unicas']}")
    print(f"Longitud promedio de listas: {resultado['estadisticas']['longitud_promedio_listas']:.2f}")
    print(f"Profundidad estimada: {resultado['estadisticas']['profundidad_estimada']}")
    print("\nDistribución de tipos:")
    for tipo, count in resultado['estadisticas']['distribucion_tipos'].items():
        print(f"  - {tipo}: {count}")
    
    # Mostrar ejemplo de la estructura profunda (solo primera clave si existe)
    if resultado['estructura']:
        print("\nEjemplo de recorrido (primer elemento):")
        print(json.dumps(resultado['estructura'], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
