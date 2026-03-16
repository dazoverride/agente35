#!/usr/bin/env python3
"""
14_sincronizador_carpeta_diff

Herramienta CLI para comparar dos carpetas localmente y mostrar diferencias.
Permite visualizar archivos únicos, modificados y comunes, pero no mueve archivos.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Set, Dict, List, Tuple

try:
    import difflib
except ImportError:
    difflib = None

class DiffSync:
    """Clase principal para gestionar la comparación de carpetas."""
    
    def __init__(self, src_path: str, dest_path: str):
        self.src = Path(src_path).resolve()
        self.dest = Path(dest_path).resolve()
        self.src_files: Set[Path] = set()
        self.dest_files: Set[Path] = set()
        self.results: Dict[str, List[str]] = {
            "solo_origen": [],
            "solo_destino": [],
            "ambos": [],
            "diferencias_contenido": []
        }
        self.dry_run = True  # Por defecto, solo visualizamos, no ejecutamos acciones

    def scan(self):
        """Recorre ambas carpetas y construye los sets de archivos."""
        if not self.src.exists():
            print(f"[ERROR] Carpeta origen no existe: {self.src}")
            sys.exit(1)
        if not self.dest.exists():
            print(f"[ERROR] Carpeta destino no existe: {self.dest}")
            sys.exit(1)

        for root, _, files in os.walk(self.src):
            for file in files:
                self.src_files.add(Path(root) / file)

        for root, _, files in os.walk(self.dest):
            for file in files:
                self.dest_files.add(Path(root) / file)

    def compare(self):
        """Realiza la lógica de comparación entre los dos sets de archivos."""
        self.scan()

        # 1. Archivos solo en origen
        self.results["solo_origen"] = list(self.src_files - self.dest_files)
        
        # 2. Archivos solo en destino
        self.results["solo_destino"] = list(self.dest_files - self.src_files)
        
        # 3. Archivos en ambos (comunes)
        self.results["ambos"] = list(self.src_files & self.dest_files)
        
        # 4. Comparación de contenido para archivos comunes
        self.results["diferencias_contenido"] = []
        for file_path in self.results["ambos"]:
            try:
                src_content = file_path.read_text(errors='ignore')
                dest_content = file_path.parent.joinpath(file_path.relative_to(self.dest.parent)).read_text(errors='ignore')
                
                # Evitar comparaciones vacías o idénticas para ahorrar memoria en archivos grandes
                if len(src_content) > 10000 or len(dest_content) > 10000:
                    continue 
                    
                if src_content != dest_content:
                    self.results["diferencias_contenido"].append(str(file_path.relative_to(self.dest.parent)))
            except Exception as e:
                self.results["diferencias_contenido"].append(f"{file_path.name} (Error: {str(e)})")

    def print_report(self):
        """Imprime un informe formateado de las diferencias encontradas."""
        print("="*60)
        print(f"Informe de Diferencias: {self.src.name} <-> {self.dest.name}")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        print(f"\n📁 ÚNICOS EN ORIGEN ({len(self.results['solo_origen'])}):")
        for f in self.results["solo_origen"]:
            print(f"  - {f}")
        if not self.results["solo_origen"]:
            print("  (Ninguno)")

        print(f"\n📁 ÚNICOS EN DESTINO ({len(self.results['solo_destino'])}):")
        for f in self.results["solo_destino"]:
            print(f"  - {f}")
        if not self.results["solo_destino"]:
            print("  (Ninguno)")

        print(f"\n📁 COMÚNES ({len(self.results['ambos'])}):")
        for f in self.results["ambos"]:
            print(f"  - {f}")
        if not self.results["ambos"]:
            print("  (Ninguno)")

        print(f"\n✏️  CON DIFERENCIAS DE CONTENIDO ({len(self.results['diferencias_contenido'])}):")
        for f in self.results["diferencias_contenido"]:
            print(f"  - {f}")
        if not self.results["diferencias_contenido"]:
            print("  (Todos los archivos comunes coinciden)")

        print("="*60)

    def sync_files(self):
        """Simulación de sincronización (en modo real copiaría archivos)."""
        print("\nMODO SIMULACIÓN (DRY RUN)")
        print("Si deseas ejecutar acciones reales, cambia 'self.dry_run = True' a 'False' antes de llamar a esta función.")
        
        # Ejemplo de qué haría (sin ejecutar por defecto)
        # for f in self.results["solo_origen"]:
        #     dest_path = self.dest / f.relative_to(self.src)
        #     dest_path.parent.mkdir(parents=True, exist_ok=True)
        #     dest_path.write_text(self.src / f).read_text()
        #     print(f"Copiando: {f} -> {dest_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python main.py <carpeta_origen> <carpeta_destino>")
        sys.exit(1)

    origen = sys.argv[1]
    destino = sys.argv[2]

    try:
        sync_tool = DiffSync(origen, destino)
        sync_tool.compare()
        sync_tool.print_report()
        # sync_tool.sync_files()  # Descomentar para probar la acción real
    except Exception as e:
        print(f"[ERROR] Ocurrió un error inesperado: {e}")
        sys.exit(1)