#!/usr/bin/env python3
"""
20_analisis_red_social_nodos.py
Herramienta CLI para analizar redes sociales basadas en nodos y aristas.
Calcula centralidad, densidad y detecta comunidades simples.
"""

import json
import sys
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Any

class GraphAnalyzer:
    def __init__(self):
        self.graph: Dict[str, List[str]] = defaultdict(list)
        self.edges: List[Tuple[str, str]] = []

    def add_edge(self, source: str, target: str):
        """Agrega una arista no dirigida entre dos nodos."""
        self.graph[source].append(target)
        self.graph[target].append(source)
        self.edges.append((source, target))

    def load_from_json(self, file_path: str) -> bool:
        """Carga la red desde un archivo JSON con formato: {"nodos": [], "aristas": []}"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for source, target in data.get('aristas', []):
                self.add_edge(source, target)
            return True
        except FileNotFoundError:
            print(f"Error: El archivo {file_path} no se encontró.")
            return False
        except json.JSONDecodeError:
            print(f"Error: El archivo {file_path} no es un JSON válido.")
            return False

    def bfs_shortest_path(self, start: str, end: str) -> List[str]:
        """Encuentra el camino más corto usando BFS."""
        if start not in self.graph or end not in self.graph:
            return None
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            current, path = queue.popleft()
            if current == end:
                return path
            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def calculate_degree_centrality(self) -> Dict[str, float]:
        """Calcula la centralidad de grado para todos los nodos."""
        centrality = {}
        num_nodes = len(self.graph)
        for node in self.graph:
            centrality[node] = len(self.graph[node]) / (num_nodes - 1) if num_nodes > 1 else 0
        return centrality

    def calculate_density(self) -> float:
        """Calcula la densidad de la red (aristas posibles / aristas reales)."""
        num_nodes = len(self.graph)
        num_edges = len(self.edges)
        if num_nodes <= 1:
            return 0.0
        max_edges = (num_nodes * (num_nodes - 1)) / 2
        return num_edges / max_edges

    def detect_components(self) -> List[List[str]]:
        """Encuentra componentes conexos usando DFS."""
        visited = set()
        components = []

        def dfs(node: str, component: List[str]):
            visited.add(node)
            component.append(node)
            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, component)

        for node in self.graph:
            if node not in visited:
                component = []
                dfs(node, component)
                components.append(component)
        return components

    def print_report(self):
        """Imprime un resumen analítico de la red."""
        print("\n=== REPORTE DE RED SOCIAL ===")
        print(f"Total Nodos: {len(self.graph)}")
        print(f"Total Aristas: {len(self.edges)}")
        print(f"Densidad: {self.calculate_density():.4f}")
        print("\n--- Centralidad de Grado (Top 5) ---")
        centrality = sorted(self.calculate_degree_centrality().items(), key=lambda x: x[1], reverse=True)
        for node, score in centrality[:5]:
            print(f"{node}: {score:.4f}")
        print("\n--- Componentes Conexos ---")
        components = self.detect_components()
        for i, comp in enumerate(components):
            print(f"Componente {i+1}: {len(comp)} nodos -> {comp}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <archivo.json> [modo]")
        print("Modos: 'reporte' (default), 'camino <origen> <destino>')")
        sys.exit(1)

    analyzer = GraphAnalyzer()
    archivo = sys.argv[1]
    modo = sys.argv[2] if len(sys.argv) > 2 else "reporte"

    if not analyzer.load_from_json(archivo):
        sys.exit(1)

    if modo == "reporte":
        analyzer.print_report()
    elif modo == "camino":
        if len(sys.argv) < 4:
            print("Falta origen y destino para el modo camino.")
            sys.exit(1)
        origen = sys.argv[2]
        destino = sys.argv[3]
        camino = analyzer.bfs_shortest_path(origen, destino)
        if camino:
            print(f"Camino más corto: {' -> '.join(camino)}")
        else:
            print(f"No existe un camino entre {origen} y {destino}.")
    else:
        print(f"Modo '{modo}' no reconocido.")
        sys.exit(1)