import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict

DATA_FILE = "escalas_equipo.json"

class ManejadorEscalas:
    def __init__(self):
        self.escalas: List[Dict] = []
        self.personal: Dict[str, Dict] = {}
        self.cargar_datos()

    def cargar_datos(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.escalas = data.get('escalas', [])
                    self.personal = data.get('personal', {})
            except Exception as e:
                print(f"Error al cargar datos: {e}")
                self.escalas = []
                self.personal = {}
        else:
            self.escalas = []
            self.personal = {}

    def guardar_datos(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({'escalas': self.escalas, 'personal': self.personal}, f, indent=4, ensure_ascii=False)

    def agregar_miembro(self, nombre: str, rol: str):
        if nombre not in self.personal:
            self.personal[nombre] = {'rol': rol, 'asignaciones': []}
            self.guardar_datos()
            print(f"Miembro '{nombre}' agregado con rol '{rol}'.")
        else:
            print(f"El miembro '{nombre}' ya existe.")

    def crear_escala(self, nombre_equipo: str, duracion_dias: int, miembros: List[str]):
        fecha_inicio = datetime.now()
        nueva_escala = {
            'id': len(self.escalas) + 1,
            'nombre_equipo': nombre_equipo,
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': (fecha_inicio + timedelta(days=duracion_dias)).strftime('%Y-%m-%d'),
            'miembros': miembros,
            'estado': 'activa'
        }
        self.escalas.append(nueva_escala)
        for miembro in miembros:
            if miembro in self.personal:
                self.personal[miembro]['asignaciones'].append(nueva_escala['id'])
        self.guardar_datos()
        print(f"Escala '{nombre_equipo}' creada correctamente.")
        return nueva_escala

    def listar_escalas_activas(self):
        hoy = datetime.now().strftime('%Y-%m-%d')
        print("\n--- ESCALAS ACTIVAS ---")
        for escala in self.escalas:
            if escala['estado'] == 'activa' and escala['fecha_fin'] >= hoy:
                print(f"ID: {escala['id']} | Equipo: {escala['nombre_equipo']}")
                print(f"  Periodo: {escala['fecha_inicio']} a {escala['fecha_fin']}")
                print(f"  Miembros: {', '.join(escala['miembros'])}")
                print()

    def finalizar_escala(self, id_escala: int):
        for escala in self.escalas:
            if escala['id'] == id_escala:
                if escala['estado'] == 'activa':
                    escala['estado'] = 'finalizada'
                    self.guardar_datos()
                    print(f"Escala {id_escala} finalizada.")
                    return True
                else:
                    print("Esta escala ya no está activa.")
                    return False
        print("Escala no encontrada.")
        return False

def main():
    manejador = ManejadorEscalas()

    while True:
        print("\n=== GESTOR DE ESCALAS DE EQUIPO ===")
        print("1. Agregar miembro al personal")
        print("2. Crear nueva escala")
        print("3. Listar escalas activas")
        print("4. Finalizar escala")
        print("5. Salir")

        opcion = input("\nSeleccione una opción: ")

        if opcion == '1':
            nombre = input("Nombre del miembro: ")
            rol = input("Rol (ej. Lider, Operario): ")
            manejador.agregar_miembro(nombre, rol)

        elif opcion == '2':
            nombre = input("Nombre del equipo: ")
            dias = int(input("Duración en días: "))
            miembros = input("Lista de miembros (separados por coma): ").split(',')
            miembros = [m.strip() for m in miembros if m.strip()]
            if not miembros:
                print("Error: Debe ingresar al menos un miembro.")
                continue
            manejador.crear_escala(nombre, dias, miembros)

        elif opcion == '3':
            manejador.listar_escalas_activas()

        elif opcion == '4':
            id_escala = input("Ingrese el ID de la escala a finalizar: ")
            if id_escala.isdigit():
                manejador.finalizar_escala(int(id_escala))

        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
