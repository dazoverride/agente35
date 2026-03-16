import json
import os
from datetime import datetime
from pathlib import Path

class ReporteFinanciero:
    def __init__(self, nombre_archivo_input='transacciones.json'):
        self.archivo = nombre_archivo_input
        self.transacciones = self.cargar_datos()

    def cargar_datos(self):
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Error: El archivo JSON no es válido.")
                return []
        else:
            print(f"Archivo {self.archivo} no encontrado. Usando datos por defecto.")
            return self.get_datos_muestra()

    def get_datos_muestra(self):
        return [
            {"fecha": "2023-10-01", "tipo": "ingreso", "monto": 5000.00, "descripcion": "Venta servicios"},
            {"fecha": "2023-10-05", "tipo": "gasto", "monto": 1200.50, "descripcion": "Alquiler"},
            {"fecha": "2023-10-10", "tipo": "ingreso", "monto": 2500.00, "descripcion": "Venta productos"},
            {"fecha": "2023-10-15", "tipo": "gasto", "monto": 300.00, "descripcion": "Servicios nube"}
        ]

    def generar_reporte(self, fecha_inicio=None, fecha_fin=None):
        transacciones_filtradas = self.transacciones

        if fecha_inicio:
            transacciones_filtradas = [t for t in transacciones_filtradas if t['fecha'] >= fecha_inicio]
        if fecha_fin:
            transacciones_filtradas = [t for t in transacciones_filtradas if t['fecha'] <= fecha_fin]

        ingresos = sum(t['monto'] for t in transacciones_filtradas if t['tipo'] == 'ingreso')
        gastos = sum(t['monto'] for t in transacciones_filtradas if t['tipo'] == 'gasto')
        saldo = ingresos - gastos

        return {
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodo_inicio": fecha_inicio,
            "periodo_fin": fecha_fin,
            "ingresos_totales": ingresos,
            "gastos_totales": gastos,
            "saldo_neto": saldo,
            "detalles": transacciones_filtradas
        }

    def exportar_reporte(self, nombre_archivo_salida='reporte_financiero.json'):
        reporte = self.generar_reporte()
        with open(nombre_archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=4)
        print(f"Reporte generado exitosamente: {nombre_archivo_salida}")
        self.imprimir_resumen(reporte)

    def imprimir_resumen(self, reporte):
        print("\n=== RESUMEN FINANCIERO ===")
        print(f"Periodo: {reporte['periodo_inicio']} a {reporte['periodo_fin']}")
        print(f"Ingresos: ${reporte['ingresos_totales']:.2f}")
        print(f"Gastos: ${reporte['gastos_totales']:.2f}")
        print(f"Saldo Neto: ${reporte['saldo_neto']:.2f}")
        print("==========================\n")

def main():
    try:
        app = ReporteFinanciero()
        app.exportar_reporte()
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()