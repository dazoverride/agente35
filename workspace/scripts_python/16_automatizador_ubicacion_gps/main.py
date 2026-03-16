import json
import csv
from datetime import datetime
from typing import List, Dict, Optional

class GPSLogger:
    """Clase para registrar y gestionar logs de ubicación GPS."""
    
    def __init__(self, filename: str = "gps_logs.json"):
        self.filename = filename
        self.data: List[Dict] = []
        self._cargar_datos()

    def _cargar_datos(self):
        """Carga datos previos desde el archivo JSON si existe."""
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = []

    def guardar_datos(self):
        """Guarda los datos actuales en el archivo JSON."""
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def agregar_ubicacion(self, lat: float, lon: float, alt: Optional[float] = None, actividad: str = "Sin actividad"):
        """Agrega un nuevo registro de ubicación con timestamp."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "latitud": lat,
            "longitud": lon,
            "altitud": alt,
            "actividad": actividad
        }
        self.data.append(entry)
        self.guardar_datos()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Coordenadas {lat}, {lon} registradas.")

    def exportar_csv(self, output_file: str = "gps_export.csv"):
        """Exporta el historial de logs a un archivo CSV."""
        if not self.data:
            print("No hay datos para exportar.")
            return
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "latitud", "longitud", "altitud", "actividad"])
            writer.writeheader()
            writer.writerows(self.data)
        print(f"Datos exportados correctamente a {output_file}")

    def filtrar_por_actividad(self, actividad: str) -> List[Dict]:
        """Filtra registros por una actividad específica."""
        return [entry for entry in self.data if entry["actividad"] == actividad]


def main():
    """Función principal para interactuar con el logger GPS."""
    print("--- Sistema de Registro GPS Automatizado ---")
    logger = GPSLogger()
    
    while True:
        print("\nOpciones:")
        print("1. Registrar nueva ubicación")
        print("2. Ver historial reciente")
        print("3. Filtrar por actividad")
        print("4. Exportar a CSV")
        print("5. Salir")
        
        opcion = input("\nSelecciona una opción (1-5): ").strip()
        
        if opcion == "1":
            lat = float(input("Latitud: "))
            lon = float(input("Longitud: "))
            alt = float(input("Altitud (opcional, presiona Enter si no): ")) or None
            act = input("Actividad (ej: Caminando, Auto, Corriendo): ")
            logger.agregar_ubicacion(lat, lon, alt, act)
        
        elif opcion == "2":
            print("\nÚltimos 5 registros:")
            for i, entry in enumerate(logger.data[-5:], 1):
                print(f"{i}. {entry['timestamp']}: {entry['latitud']}, {entry['longitud']} - {entry['actividad']}")
        
        elif opcion == "3":
            act = input("Ingresa la actividad a filtrar: ")
            resultados = logger.filtrar_por_actividad(act)
            if resultados:
                print(f"\nEncontrados {len(resultados)} registros:")
                for entry in resultados:
                    print(entry)
            else:
                print("No se encontraron registros con esa actividad.")
        
        elif opcion == "4":
            logger.exportar_csv()
        
        elif opcion == "5":
            print("Cerrando sistema...")
            break
        
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
