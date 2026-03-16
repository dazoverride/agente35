import requests
from bs4 import BeautifulSoup
import csv
import sys

BASE_URL = "https://www.ejemplo-precio-producto.com"

def obtener_precios():
    """Obtiene una lista de productos y sus precios del sitio web de ejemplo."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(BASE_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        productos = []
        
        items = soup.find_all('div', class_='producto-item')
        for item in items:
            titulo = item.find('h3', class_='titulo').text.strip() if item.find('h3', class_='titulo') else 'Sin título'
            precio = item.find('span', class_='precio').text.strip() if item.find('span', class_='precio') else 'N/A'
            productos.append({'nombre': titulo, 'precio': precio})
        
        return productos
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return []

def guardar_csv(datos, nombre_archivo='precios.csv'):
    """Guarda los datos en un archivo CSV."""
    if not datos:
        print("No hay datos para guardar.")
        return
    
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['nombre', 'precio'])
        writer.writeheader()
        writer.writerows(datos)
    print(f"Datos guardados en {nombre_archivo}")

def main():
    print("--- Scraping de Precios Web ---")
    productos = obtener_precios()
    
    if productos:
        print(f"Se encontraron {len(productos)} productos.")
        print("\nResultados:")
        for p in productos:
            print(f"{p['nombre']}: {p['precio']}")
        
        opcion = input("\n¿Desea guardar los datos en CSV? (s/n): ").lower()
        if opcion == 's':
            nombre = input("Nombre del archivo (default: precios.csv): ") or "precios.csv"
            guardar_csv(productos, nombre)
    else:
        print("No se pudieron obtener productos.")

if __name__ == "__main__":
    main()