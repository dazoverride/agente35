import os
import struct
from pathlib import Path

class BinaryFileConverter:
    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"El archivo {path} no existe.")

    def get_file_info(self) -> dict:
        """Devuelve información básica sobre el archivo."""
        stat = self.path.stat()
        return {
            "nombre": self.path.name,
            "tamano_bytes": stat.st_size,
            "tamano_humano": self._format_size(stat.st_size),
            "extension": self.path.suffix.lower(),
            "tipo": self._detect_type()
        }

    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def _detect_type(self) -> str:
        ext = self.path.suffix.lower()
        if ext == '.txt':
            return 'Texto plano'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return 'Imagen'
        elif ext in ['.mp3', '.wav', '.ogg']:
            return 'Audio'
        elif ext in ['.mp4', '.avi', '.mov']:
            return 'Video'
        elif ext in ['.py', '.js', '.html', '.css']:
            return 'Código fuente'
        else:
            return 'Binario/Desconocido'

    def read_first_bytes(self, n: int = 10) -> str:
        """Lee los primeros N bytes y los convierte a hexadecimal legible."""
        try:
            with open(self.path, 'rb') as f:
                data = f.read(n)
            return data.hex()
        except Exception as e:
            return f"Error leyendo datos: {e}"

    def verify_magic_bytes(self) -> dict:
        """Verifica bytes mágicos comunes para identificar formato real."""
        try:
            with open(self.path, 'rb') as f:
                magic = f.read(16)
            
            results = {
                "PE (Windows Executable)": magic.startswith(b'MZ'),
                "PNG": magic.startswith(b'\x89PNG'),
                "JPEG": magic.startswith(b'\xff\xd8'),
                "ZIP": magic.startswith(b'PK'),
                "PDF": magic.startswith(b'%PDF'),
                "GIF": magic.startswith(b'GIF8'),
                "HTML": magic.startswith(b'<!') or magic.startswith(b'<?'),
                "TXT": magic.startswith(b'Text') or magic.startswith(b'Text00'),
                "Empty": len(magic) == 0
            }
            return results
        except Exception as e:
            return {"Error": str(e)}

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Conversor y Analizador de Ficheros Binarios')
    parser.add_argument('archivo', help='Ruta al archivo a analizar')
    parser.add_argument('-f', '--first', type=int, default=10, help='Número de bytes a leer para hex dump')
    args = parser.parse_args()

    try:
        conv = BinaryFileConverter(args.archivo)
        info = conv.get_file_info()
        print(f"--- Análisis de: {info['nombre']} ---")
        print(f"Tamaño: {info['tamano_humano']}")
        print(f"Tipo: {info['tipo']}")
        print()
        
        print(f"Primeros {args.first} bytes (Hex): {conv.read_first_bytes(args.first)}")
        print()
        
        print("Verificación de firma mágica:")
        magic_check = conv.verify_magic_bytes()
        for tipo, es in magic_check.items():
            if es:
                print(f"  ✓ {tipo}")
            elif tipo == "Empty":
                print(f"  ! Archivo vacío")
    except Exception as e:
        print(f"Error fatal: {e}")

if __name__ == "__main__":
    main()
