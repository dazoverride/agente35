import json
import csv
import math
from typing import List, Dict, Tuple

def calcular_distancia(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calcula la distancia euclidiana entre dos puntos (lat, lon) aproximada."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

class OptimizadorRutas:
    def __init__(self):
        self.entregas: List[Dict] = []
        self.puntos_delivery: Dict[int, Tuple[float, float]] = {}
        self.centro_distribucion: Tuple[float, float] = (0.0, 0.0)

    def cargar_entregas(self, archivo: str) -> None:
        """Carga entregas desde un archivo JSON."""
        with open(archivo, 'r') as f:
            data = json.load(f)
        self.entregas = data.get('entregas', [])
        self.puntos_delivery = {
            int(d['id']): tuple(map(float, d['coordenadas'].split(','))) 
            for d in self.entregas if 'coordenadas' in d
        }
        if self.puntos_delivery:
            self.centro_distribucion = tuple(map(float, self.entregas[0]['coordenadas'].split(',')))

    def algoritmo_vecina_mas_cercana(self) -> List[List[int]]:
        """Algoritmo de vecino más cercano para ordenar paradas."""
        if not self.entregas:
            return []
        
        ruta = [self.centro_distribucion]  # Inicio en el centro
        entregas_pendientes = list(range(1, len(self.entregas) + 1))
        ruta_final = []
        
        while entregas_pendientes:
            actual = ruta[-1]
            # Si no hay entregas pendientes, volver al centro (o finalizar)
            if not entregas_pendientes:
                break
            
            # Buscar la entrega más cercana a la actual
            mas_cercana = None
            min_dist = float('inf')
            
            for id_entrega in entregas_pendientes:
                if id_entrega in self.puntos_delivery:
                    dist = calcular_distancia(actual, self.puntos_delivery[id_entrega])
                    if dist < min_dist:
                        min_dist = dist
                        mas_cercana = id_entrega
            
            if mas_cercana:
                ruta.append(self.puntos_delivery[mas_cercana])
                ruta_final.append(mas_cercana)
                entregas_pendientes.remove(mas_cercana)
            else:
                # Si no hay más entregas cercanas, volver al centro para reiniciar
                ruta.append(self.centro_distribucion)
                ruta_final.append(-1)  # Indicador de vuelta al centro
                entregas_pendientes = list(range(1, len(self.entregas) + 1))
                
        return ruta_final

    def generar_reporte_ruta(self, ruta: List[int], archivo_salida: str) -> None:
        """Genera un reporte CSV con la ruta optimizada."""
        with open(archivo_salida, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Orden', 'ID Entrega', 'Latitud', 'Longitud', 'Distancia Acumulada'])
            
            distancia_acumulada = 0.0
            for i, id_entrega in enumerate(ruta):
                if id_entrega != -1 and id_entrega in self.puntos_delivery:
                    lat, lon = self.puntos_delivery[id_entrega]
                    if i == 0:
                        dist = calcular_distancia(self.centro_distribucion, (lat, lon))
                    else:
                        prev_id = ruta[i-1]
                        if prev_id == -1:  # Vuelta al centro
                            lat_c, lon_c = self.centro_distribucion
                            dist = calcular_distancia((lat_c, lon_c), (lat, lon))
                        else:
                            dist = calcular_distancia(self.puntos_delivery[prev_id], (lat, lon))
                    distancia_acumulada += dist
                    writer.writerow([i, id_entrega, lat, lon, round(distancia_acumulada, 2)])
                elif id_entrega == -1:
                    writer.writerow([i, 'Centro', self.centro_distribucion[0], self.centro_distribucion[1], round(distancia_acumulada, 2)])

    def ejecutar(self, archivo_entrada: str, archivo_salida: str) -> None:
        """Ejecuta el proceso completo."""
        self.cargar_entregas(archivo_entrada)
        if not self.entregas:
            print("No hay entregas para procesar.")
            return
        
        ruta = self.algoritmo_vecina_mas_cercana()
        print(f"Ruta optimizada generada con {len(ruta)} paradas.")
        self.generar_reporte_ruta(ruta, archivo_salida)
        print(f"Reporte guardado en: {archivo_salida}")

if __name__ == "__main__":
    # Ejemplo de uso
    try:
        # Asumiendo un archivo 'entregas.json' con formato: {"entregas": [{"id": 1, "coordenadas": "40.4168,-3.7038"}, ...]}
        optimizador = OptimizadorRutas()
        optimizador.ejecutar("entregas.json", "ruta_optimizada.csv")
    except FileNotFoundError:
        print("Error: El archivo de entregas 'entregas.json' no se encuentra.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")