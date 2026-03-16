import datetime
import os
import json
from pathlib import Path

class ManejadorCitas:
    def __init__(self, archivo_citas="citas.json"):
        self.archivo = archivo_citas
        self.citas = self.cargar_citas()

    def cargar_citas(self):
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def guardar_citas(self):
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump(self.citas, f, indent=4, ensure_ascii=False)

    def agregar_cita(self, titulo, descripcion, fecha, hora, duracion_minutos):
        nueva_cita = {
            "id": len(self.citas) + 1,
            "titulo": titulo,
            "descripcion": descripcion,
            "fecha": fecha,
            "hora": hora,
            "duracion_minutos": int(duracion_minutos)
        }
        self.citas.append(nueva_cita)
        self.guardar_citas()
        print(f"Cita '{titulo}' agregada correctamente.")

    def listar_citas(self, filtro_fecha=None):
        if filtro_fecha:
            citas_filtradas = [c for c in self.citas if c['fecha'] == filtro_fecha]
        else:
            # Ordenar por fecha y hora
            citas_filtradas = sorted(self.citas, key=lambda x: (x['fecha'], x['hora']))
        
        if not citas_filtradas:
            print("No se encontraron citas.")
            return
        
        print(f"\n--- LISTA DE CITAS ({len(citas_filtradas)} encontradas) ---")
        for cita in citas_filtradas:
            inicio = f"{cita['fecha']} {cita['hora']}"
            fin_hora = self.calcular_fin_cita(cita)
            print(f"ID: {cita['id']} | {cita['titulo']}")
            print(f"  Hora: {inicio} - {fin_hora}")
            if cita['descripcion']:
                print(f"  Detalles: {cita['descripcion'][:50]}...")
            print("-" * 30)

    def borrar_cita(self, id_cita):
        for i, cita in enumerate(self.citas):
            if cita['id'] == id_cita:
                del self.citas[i]
                self.guardar_citas()
                print(f"Cita ID {id_cita} eliminada.")
                return
        print(f"No se encontró una cita con ID {id_cita}.")

    def calcular_fin_cita(self, cita):
        from datetime import timedelta
        try:
            inicio = datetime.datetime.strptime(f"{cita['fecha']} {cita['hora']}", "%Y-%m-%d %H:%M")
            fin = inicio + timedelta(minutes=cita['duracion_minutos'])
            return fin.strftime("%H:%M")
        except ValueError:
            return "Error en formato de fecha/hora"

    def borrar_todas_citas(self):
        if self.citas:
            self.citas = []
            self.guardar_citas()
            print("Todas las citas han sido borradas.")
        else:
            print("No hay citas para borrar.")

def main():
    manager = ManejadorCitas()

    while True:
        print("\n=== GESTOR DE CITAS CLI ===")
        print("1. Agregar nueva cita")
        print("2. Listar todas las citas")
        print("3. Listar citas de una fecha específica")
        print("4. Eliminar una cita por ID")
        print("5. Borrar todas las citas")
        print("0. Salir")
        
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            print("\n--- AGREGAR CITA ---")
            titulo = input("Título: ").strip()
            descripcion = input("Descripción (opcional): ").strip()
            fecha = input("Fecha (YYYY-MM-DD, ej: 2023-12-31): ").strip()
            hora = input("Hora (HH:MM, ej: 14:30): ").strip()
            duracion = input("Duración en minutos: ").strip()
            manager.agregar_cita(titulo, descripcion, fecha, hora, duracion)
        
        elif opcion == "2":
            manager.listar_citas()
        
        elif opcion == "3":
            fecha = input("Ingresa la fecha para filtrar (YYYY-MM-DD): ").strip()
            manager.listar_citas(filtro_fecha=fecha)
        
        elif opcion == "4":
            id_cita = input("Ingresa el ID de la cita a eliminar: ").strip()
            manager.borrar_cita(id_cita)
        
        elif opcion == "5":
            confirmacion = input("¿Estás seguro de que quieres borrar TODAS las citas? (si/no): ").strip().lower()
            if confirmacion == "si":
                manager.borrar_todas_citas()
            else:
                print("Operación cancelada.")
        
        elif opcion == "0":
            print("Cerrando gestor de citas. ¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Inténtalo de nuevo.")

if __name__ == "__main__":
    main()
