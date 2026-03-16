import requests

def buscar(query):
    # Usar el API oficial de Wikipedia que no bloquea scripts y no requiere API keys problemáticas
    api_url = "https://es.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "utf8": 1,
        "srsearch": query,
        "srlimit": 5
    }
    headers = {
        "User-Agent": "BotBuscadorLocal/1.0 (Python Experimento)"
    }
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("query", {}).get("search", [])
            
            if results:
                print(f"\nResultados (Wikipedia) para: {query}\n")
                for i, item in enumerate(results): 
                    title = item.get("title", "")
                    # Limpiando un poco el extracto HTML crudo del JSON
                    snippet = item.get("snippet", "").replace('<span class="searchmatch">', '').replace('</span>', '')
                    url = f"https://es.wikipedia.org/wiki/{title.replace(' ', '_')}"
                    
                    print(f"{i+1}. {title}")
                    print(f"   ► {snippet[:150]}...")
                    print(f"   ► URL: {url}\n")
            else:
                print("No se encontraron resultados en Wikipedia para esta búsqueda.")
        else:
            print(f"Error al conectar: Código de estado {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error al realizar la búsqueda: {e}")

if __name__ == "__main__":
    print("--- Buscador Básico (Wikipedia API) ---")
    print("Nota: Este script es seguro y no genera errores de Captcha.")
    
    while True:
        try:
            query = input("¿Qué deseas buscar? (o 'salir' para terminar): ").strip()
            if query.lower() == 'salir':
                print("Saliendo...")
                break
            if query:
                buscar(query)
            else:
                print("Por favor, ingresa un término de búsqueda.")
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nCancelado por el usuario.")
            break