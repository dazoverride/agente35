import re
import json
from collections import Counter

def main():
    print("=== Analizador de Patrones de Texto ===")
    print("Este script detecta patrones regulares, palabras repetidas y estructura en textos.")
    
    texto = input("Introduce el texto a analizar (o 'fin' para salir): ")
    
    if texto.lower() == 'fin':
        return
    
    # Análisis de palabras repetidas
    palabras = re.findall(r'\b\w+\b', texto.lower())
    contador = Counter(palabras)
    repetidas = {palabra: count for palabra, count in contador.items() if count > 1}
    
    # Búsqueda de patrones (emails, URLs, fechas)
    emails = re.findall(r'[\w\.-]+@\w+\.\w+', texto)
    urls = re.findall(r'https?://\S+', texto)
    fechas = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', texto)
    
    # Estructura: oraciones y párrafos
    oraciones = len(re.findall(r'[^.!?]+[.!?]+', texto))
    parrafos = len(re.findall(r'\n\s*', texto)) + 1
    
    # Salida JSON
    resultado = {
        "palabras_repetidas": repetidas,
        "emails_encontrados": emails,
        "urls_encontradas": urls,
        "fechas_encontradas": fechas,
        "num_oraciones": oraciones,
        "num_parrafos": parrafos,
        "longitud_total": len(texto)
    }
    
    print("\n--- Resumen del Análisis ---")
    print(f"Oraciones: {oraciones}")
    print(f"Párrafos: {parrafos}")
    print(f"Emails encontrados: {len(emails)}")
    print(f"URLs encontradas: {len(urls)}")
    print(f"Patrones de fecha: {len(fechas)}")
    print(f"Palabras repetidas: {len(repetidas)}")
    
    # Exportar a JSON
    with open('analisis_patrones.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)
    print("\nResultados guardados en 'analisis_patrones.json'")

if __name__ == "__main__":
    main()