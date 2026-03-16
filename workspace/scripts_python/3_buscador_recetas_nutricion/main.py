#!/usr/bin/env python3
"""
Buscador de recetas con filtro nutricional básico.
Permite buscar recetas por nombre y filtrar por rango de calorías.
"""

import json
import re
from typing import List, Dict, Optional

class Receta:
    def __init__(self, nombre: str, ingredientes: List[str], calorias: int, tiempo_coccion: int):
        self.nombre = nombre
        self.ingredientes = ingredientes
        self.calorias = calorias
        self.tiempo_coccion = tiempo_coccion

    def __str__(self):
        return f"{self.nombre} ({self.calorias} kcal) - {self.tiempo_coccion} min"

class BuscadorRecetas:
    def __init__(self):
        self.recetas: List[Receta] = [
            Receta("Ensalada César", ["lechuga", "pechuga pollo", "parmesano", "crutones"], 350, 15),
            Receta("Tacos de Carne", ["tortillas", "carne molida", "tomate", "cebolla", "cilantro"], 420, 25),
            Receta("Sopa de Lentejas", ["lentejas", "zanahoria", "caldo", "pan"], 280, 40),
            Receta("Pasta Carbonara", ["pasta", "huevos", "tocino", "queso pecorino", "pimienta"], 550, 20),
            Receta("Batido de Frutas", ["plátano", "fresa", "leche", "aceite de coco"], 180, 5)
        ]

    def buscar_por_nombre(self, nombre_busqueda: str) -> List[Receta]:
        """
        Busca recetas cuyo nombre contenga la cadena proporcionada.
        El matching es insensible a mayúsculas/minúsculas.
        """
        nombre_lower = nombre_busqueda.lower()
        resultados = []
        for receta in self.recetas:
            if nombre_lower in receta.nombre.lower():
                resultados.append(receta)
        return resultados

    def filtrar_por_calorias(self, recetas: List[Receta], max_calorias: int) -> List[Receta]:
        """
        Filtra una lista de recetas para incluir solo aquellas con menos o igual calorías al límite.
        """
        return [r for r in recetas if r.calorias <= max_calorias]

    def mostrar_resultados(self, recetas: List[Receta]):
        """
        Imprime los resultados en formato amigable.
        """
        if not recetas:
            print("No se encontraron recetas que coincidan con los criterios.")
            return

        print(f"\n--- Resultados ({len(recetas)} recetas) ---")
        for i, receta in enumerate(recetas, 1):
            print(f"{i}. {receta}")
        print()

def main():
    buscador = BuscadorRecetas()

    print("=== Buscador de Recetas Nutricionales ===")
    print("1. Buscar por nombre")
    print("2. Filtrar por calorías (máximo)")

    while True:
        print("\nSelecciona una opción (o 'salir' para terminar):")
        opcion = input().strip().lower()

        if opcion == "salir":
            break
        elif opcion == "1":
            print("¿Qué quieres buscar? (ej: pasta, pollo, ensalada)")
            nombre = input().strip()
            resultados = buscador.buscar_por_nombre(nombre)
            buscador.mostrar_resultados(resultados)
            if resultados:
                print("¿Quieres filtrar estos resultados por calorías? (s/n)")
                filtro = input().strip().lower()
                if filtro == "s":
                    try:
                        max_cals = int(input("Ingresa el límite máximo de calorías: "))
                        filtrados = buscador.filtrar_por_calorias(resultados, max_cals)
                        buscador.mostrar_resultados(filtrados)
                    except ValueError:
                        print("Por favor ingresa un número válido.")
        elif opcion == "2":
            try:
                max_cals = int(input("Ingresa el límite máximo de calorías para buscar todas las recetas: "))
                todas_filtradas = buscador.filtrar_por_calorias(buscador.recetas, max_cals)
                buscador.mostrar_resultados(todas_filtradas)
            except ValueError:
                print("Por favor ingresa un número válido.")
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()
