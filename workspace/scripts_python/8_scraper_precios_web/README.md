# 8_scraper_precios_web

Un script en Python diseñado para extraer automáticamente una lista de productos y sus precios de un sitio web de ejemplo, y opcionalmente guardar los resultados en un archivo CSV.

## Características
- **Extracción de datos**: Utiliza `requests` y `BeautifulSoup` para parsear HTML.
- **Manejo de errores**: Incluye timeouts y manejo de excepciones básicos.
- **Exportación**: Opción para descargar los datos en formato `.csv`.

## Dependencias
- `requests`
- `beautifulsoup4`

## Cómo ejecutar
1. Instala las dependencias:
   ```bash
   pip install requests beautifulsoup4
   ```
2. Ejecuta el script:
   ```bash
   python 8_scraper_precios_web/main.py
   ```

> **Nota**: El script utiliza una URL de ejemplo (`https://www.ejemplo-precio-producto.com`). Para usarlo en producción, reemplaza `BASE_URL` con la URL real y ajusta los selectores CSS según la estructura del sitio objetivo.

## Limitaciones
- No incluye rotación de User-Agent avanzada o headless browser.
- No maneja JavaScript dinámico (solo HTML estático).
- Debe respetar los robots.txt y términos de servicio del sitio objetivo.