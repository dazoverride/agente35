import requests
import json
import time
import sys
import argparse

def obtener_rutas_api(url_base):
    """Obtiene la lista de rutas disponibles desde una API Swagger/OpenAPI básica."""
    try:
        response = requests.get(url_base)
        if response.status_code == 200:
            return response.json().get('paths', [])
        else:
            print(f"Error al conectar con {url_base}: Código {response.status_code}")
            sys.exit(1)
    except requests.RequestException as e:
        print(f"Error de red: {e}")
        sys.exit(1)

def testear_ruta(url_base, ruta):
    """Realiza una prueba GET simple a una ruta específica."""
    full_url = f"{url_base.rstrip('/')}{ruta.lstrip('/')}" if not ruta.startswith('/') else f"{url_base.rstrip('/')}{ruta}"
    try:
        response = requests.get(full_url, timeout=5)
        status = "OK" if response.status_code < 400 else "Error"
        return {"ruta": ruta, "status": status, "codigo": response.status_code, "tiempo_ms": response.elapsed.total_seconds() * 1000}
    except requests.RequestException as e:
        return {"ruta": ruta, "status": "Fallido", "codigo": 0, "tiempo_ms": 0, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Monitor de Rutas API: Prueba la salud de endpoints específicos o todo el inventario.")
    parser.add_argument("url", type=str, help="URL base de la API (ej: http://localhost:8000)")
    parser.add_argument("ruta", type=str, nargs="?", help="Ruta específica a probar. Si no se proporciona, prueba todas las rutas disponibles.")
    args = parser.parse_args()

    print(f"Escaneando API en: {args.url}")
    rutas_disponibles = obtener_rutas_api(args.url)
    print(f"Encontradas {len(rutas_disponibles)} rutas.")

    if args.ruta:
        # Modo: Probar una sola ruta específica
        if args.ruta not in rutas_disponibles:
            print(f"Advertencia: La ruta '{args.ruta}' no fue encontrada en la lista declarada de la API.")
        resultado = testear_ruta(args.url, args.ruta)
        print(json.dumps(resultado, indent=2))
    else:
        # Modo: Escanear todas las rutas
        print("\n--- Informe de Salud de API ---")
        resultados = []
        for ruta in rutas_disponibles:
            resultado = testear_ruta(args.url, ruta)
            resultados.append(resultado)
            print(f"[{resultado['status']}] {resultado['ruta']} (Código: {resultado['codigo']})")

        # Resumen final
        ok_count = sum(1 for r in resultados if r['codigo'] < 400)
        print(f"\nResumen: {ok_count}/{len(resultados)} rutas saludables.")

if __name__ == "__main__":
    main()
