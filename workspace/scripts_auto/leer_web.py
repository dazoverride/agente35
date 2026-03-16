# DESCRIPCION: Extrae el texto legible de una página web pública. Argumentos: <url>
import sys
import urllib.request
import re

if len(sys.argv) < 2:
    print("Uso: python leer_web.py <url>")
    sys.exit(1)

url = sys.argv[1]
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=10) as response:
        html = response.read().decode('utf-8', errors='ignore')
        
    # Limpieza básica de HTML
    texto = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r'<style.*?>.*?</style>', '', texto, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r'<[^>]+>', ' ', texto) # Eliminar otras etiquetas HTML
    texto = "\n".join(line.strip() for line in texto.splitlines() if line.strip())
    
    # Limitamos la salida para no saturar la memoria del LLM
    max_chars = 4000
    if len(texto) > max_chars:
        print(texto[:max_chars])
        print(f"\n\n...[Texto total de {len(texto)} caracteres truncado a {max_chars} por el sistema]...")
    else:
        print(texto)
except Exception as e:
    print(f"Error al leer la URL: {e}")
