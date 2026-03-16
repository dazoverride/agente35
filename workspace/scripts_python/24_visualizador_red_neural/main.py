import json
import matplotlib.pyplot as plt
import networkx as nx
import random
import datetime

# Configuración
NODOS_NEURONAS = 100
PESO_MAX = 1.0
PESO_MIN = -1.0

def generar_red_neural():
    """Genera una red neuronal aleatoria (Grafo) para visualización."""
    G = nx.Graph()
    
    # Crear nodos (neurona, capa oculta, etc.)
    for i in range(NODOS_NEURONAS):
        G.add_node(i, tipo=random.choice(['Input', 'Hidden', 'Output']))
    
    # Conectar nodos con pesos aleatorios
    for i in range(NODOS_NEURONAS):
        num_conexiones = random.randint(2, 5)
        posibles_conexiones = [n for n in G.nodes() if n != i]
        conexiones_elegidas = random.sample(posibles_conexiones, min(num_conexiones, len(posibles_conexiones)))
        
        for target in conexiones_elegidas:
            peso = random.uniform(PESO_MIN, PESO_MAX)
            G.add_edge(i, target, peso=peso)
    
    return G

def calcular_metricas_red(G):
    """Calcula métricas básicas de la red."""
    num_nodos = G.number_of_nodes()
    num_aristas = G.number_of_edges()
    centralidad = nx.degree_centrality(G)
    promedio_centralidad = sum(centralidad.values()) / num_nodos
    
    return {
        "num_nodos": num_nodos,
        "num_aristas": num_aristas,
        "promedio_centralidad": promedio_centralidad,
        "nodo_mas_central": max(centralidad, key=centralidad.get)
    }

def guardar_red(G, metricas, archivo_json="red_neural.json", archivo_mat="red_neural.json"):
    """Guarda la topología y métricas en archivos JSON."""
    con_json = open(archivo_json, "w")
    json.dump({"grafos": nx.node_link_data(G), "metricas": metricas}, con_json)
    con_json.close()
    
    with open(archivo_mat, "w") as f:
        json.dump(list(G.edges(data=True)), f)

def visualizar_red(G, metricas, archivo_mat="red_neural.json", archivo_pdf="visualizacion_red.pdf"):
    """Crea una visualización gráfica de la red neuronal."""
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, k=0.15, iterations=50)
    
    # Colores por tipo de nodo
    colores = {"Input": "blue", "Hidden": "gray", "Output": "red"}
    nodos = [colores.get(n[2], "black") for n in G.nodes(data=True)]
    
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color=nodos)
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    # Dibujar aristas con ancho basado en peso
    edge_collection = nx.draw_networkx_edges(G, pos, width=[abs(w) for (_, _, w) in G.edges(data="peso")])
    
    # Dibujar pesos de las aristas
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): f"{w:.2f}" for u, v, w in G.edges(data="peso")})
    
    plt.axis("off")
    plt.title(f"Red Neuronal Aleatoria - Nodos: {metricas['num_nodos']}, Aristas: {metricas['num_aristas']}")
    plt.savefig(archivo_pdf, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Gráfico guardado en {archivo_pdf}")

def main():
    print("=== Generador de Redes Neuronales Visuales ===")
    
    # Generar red
    G = generar_red_neural()
    
    # Calcular métricas
    metricas = calcular_metricas_red(G)
    
    # Guardar datos
    guardar_red(G, metricas)
    print(f"Datos guardados en red_neural.json")
    
    # Visualizar
    visualizar_red(G, metricas)
    print("Red generada y visualizada exitosamente.")

if __name__ == "__main__":
    main()