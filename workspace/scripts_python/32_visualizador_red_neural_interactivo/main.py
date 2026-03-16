import sys
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import random
from collections import defaultdict

@dataclass
class Neuron:
    id: str
    activation: float
    hidden: bool = False

@dataclass
class Synapse:
    from_neuron: str
    to_neuron: str
    weight: float
    bias: float
    activation_function: str  # 'sigmoid', 'relu', 'linear'

class VisualizadorRedNeural:
    def __init__(self):
        self.neurons: Dict[str, Neuron] = {}
        self.synapses: List[Synapse] = []
        self.metrics: Dict[str, float] = {}
        self.colors: Dict[str, Tuple[int, int, int]] = {
            'input': (0, 128, 255),
            'hidden': (255, 100, 50),
            'output': (255, 255, 0)
        }
    
    def add_neuron(self, neuron_id: str, hidden: bool = False):
        self.neurons[neuron_id] = Neuron(id=neuron_id, activation=0.0, hidden=hidden)
    
    def add_synapse(self, from_n: str, to_n: str, weight: float, bias: float, activation: str):
        self.synapses.append(Synapse(from_n, to_n, weight, bias, activation))
    
    def calculate_metrics(self):
        if not self.neurons or not self.synapses:
            return
        
        # Density: ratio of existing connections to max possible
        n_nodes = len(self.neurons)
        max_edges = n_nodes * (n_nodes - 1)  # Fully connected directed
        density = len(self.synapses) / max_edges if max_edges > 0 else 0
        
        # Average degree
        in_degrees = defaultdict(int)
        out_degrees = defaultdict(int)
        for s in self.synapses:
            out_degrees[s.from_neuron] += 1
            in_degrees[s.to_neuron] += 1
        
        avg_in = sum(in_degrees.values()) / n_nodes if n_nodes > 0 else 0
        avg_out = sum(out_degrees.values()) / n_nodes if n_nodes > 0 else 0
        
        # Clustering coefficient (simplified: local density)
        clusters = 0
        for node in self.neurons:
            neighbors = [s.to_neuron for s in self.synapses if s.from_neuron == node]
            if len(neighbors) > 1:
                # Check how many connections exist between neighbors
                connections = sum(1 for s in self.synapses if s.from_neuron in neighbors and s.to_neuron in neighbors)
                clusters += connections
        
        self.metrics = {
            'nodes': n_nodes,
            'edges': len(self.synapses),
            'density': round(density, 4),
            'avg_in_degree': round(avg_in, 4),
            'avg_out_degree': round(avg_out, 4),
            'clustering_coefficient': round(clusters / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0, 4)
        }
    
    def generate_topology(self, layers: int, nodes_per_layer: int):
        """Genera una topología de red neuronal aleatoria completa."""
        self.neurons.clear()
        self.synapses.clear()
        self.metrics.clear()
        
        prev_layer = 0
        layer_id = 0
        
        for layer in range(layers):
            for i in range(nodes_per_layer):
                neuron_id = f"L{layer}_{i}"
                self.add_neuron(neuron_id, hidden=(layer > 0 and layer < layers - 1))
                
                # Connect to next layer if exists
                if layer < layers - 1:
                    for next_i in range(nodes_per_layer):
                        weight = random.uniform(-1.0, 1.0)
                        bias = random.uniform(-0.5, 0.5)
                        func = random.choice(['sigmoid', 'relu', 'linear'])
                        self.add_synapse(f"L{layer}_{i}", f"L{layer+1}_{next_i}", weight, bias, func)
            layer_id += 1
        
        self.calculate_metrics()
    
    def visualize_ascii(self):
        if not self.metrics:
            print("No hay topología generada.")
            return
        
        print("=" * 60)
        print("VISUALIZADOR DE RED NEURAL - ESTRUCTURA Y MÉTRICAS")
        print("=" * 60)
        
        print(f"\n📊 MÉTRICAS ESTRUCTURALES:")
        print(f"   Nodos: {self.metrics['nodes']}")
        print(f"   Conexiones (Edges): {self.metrics['edges']}")
        print(f"   Densidad: {self.metrics['density']}")
        print(f"   Grado In Promedio: {self.metrics['avg_in_degree']}")
        print(f"   Grado Out Promedio: {self.metrics['avg_out_degree']}")
        print(f"   Coeficiente de Agrupamiento: {self.metrics['clustering_coefficient']}")
        
        print(f"\n🧠 TOPOLOGÍA VISUAL (ASCII ART):")
        print("   (Capas: Input -> Hidden -> Output)")
        
        # Group neurons by layer
        layers_map = defaultdict(list)
        for n_id, n in self.neurons.items():
            layer = n_id.split('_')[0]  # Extract L0, L1, etc.
            layers_map[layer].append(n_id)
        
        if not layers_map:
            print("   [Sin nodos]")
            return
        
        # Print layers vertically
        max_layer = max(len(l) for l in layers_map.values())
        for row in range(max_layer):
            line = ""
            for layer, nodes in layers_map.items():
                if row < len(nodes):
                    color = self.colors['hidden'] if any(self.neurons[n].hidden for n in nodes) else self.colors['input'] if layer == '0' else self.colors['output']
                    symbol = '●' if layer == '0' or layer == str(max_layer-1) else '○'
                    line += f" {symbol} "
                else:
                    line += "   "
            print(f"   {line}")
        
        # Print sample connections
        print(f"\n   🔗 CONEXIONES DE EJEMPLO (Primeras 10):")
        count = 0
        for s in self.synapses:
            if count >= 10:
                break
            print(f"   {s.from_neuron} -> {s.to_neuron} [w={s.weight:.2f}, f={s.activation_function}]")
            count += 1
        
        if len(self.synapses) > 10:
            print(f"   ... y {len(self.synapses) - 10} más.")
    
    def export_json(self, filename: str = "red_neural_topology.json"):
        data = {
            'neurons': [{
                'id': n.id,
                'activation': n.activation,
                'hidden': n.hidden
            } for n in self.neurons.values()],
            'synapses': [{
                'from': s.from_neuron,
                'to': s.to_neuron,
                'weight': s.weight,
                'bias': s.bias,
                'activation': s.activation_function
            } for s in self.synapses],
            'metrics': self.metrics
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"\n✅ Topología exportada a {filename}")


def main():
    print("🚀 Iniciando Visualizador de Red Neurale Interactivo...")
    print("╔" + "═" * 58 + "╗")
    print("║  TOOL 32: GENERADOR DE TOPOLOGÍAS Y MÉTRICAS CLI    ║")
    print("╚" + "═" * 58 + "╝")
    
    viz = VisualizadorRedNeural()
    
    # Default: Generar una red 2-4-2 (2 input, 4 hidden, 2 output)
    layers = 3
    nodes_per_layer = [2, 4, 2]
    
    # Expand to uniform for simplicity in this demo
    uniform_nodes = max(nodes_per_layer)
    viz.generate_topology(layers, uniform_nodes)
    
    viz.visualize_ascii()
    
    # Offer export
    try:
        export_choice = input("\n¿Deseas exportar la topología a JSON? (s/n): ").strip().lower()
        if export_choice == 's':
            viz.export_json("red_neural_topology.json")
    except KeyboardInterrupt:
        print("\n👋 Sesión finalizada.")
        sys.exit(0)

if __name__ == "__main__":
    main()
