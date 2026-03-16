#!/usr/bin/env python3
"""
Sincronizador de bases de datos locales.
Este script compara dos archivos SQL (dump) o JSON de una base de datos local
y genera un informe de diferencias (nuevos, eliminados, modificados registros).
"""

import json
import sqlite3
import sys
import os
from difflib import unified_diff
from datetime import datetime

def detectar_diferencias_json(f1_path, f2_path, output_file="diff_report.md"):
    """
    Compara dos archivos JSON y genera un reporte de diferencias.
    """
    if not os.path.exists(f1_path) or not os.path.exists(f2_path):
        print(f"Error: Faltan archivos. Verifica {f1_path} y {f2_path}")
        return False

    try:
        with open(f1_path, 'r', encoding='utf-8') as f1:
            data1 = json.load(f1)
        with open(f2_path, 'r', encoding='utf-8') as f2:
            data2 = json.load(f2)
    except json.JSONDecodeError:
        print("Error: Archivos no son JSON válido.")
        return False

    # Normalización simple de claves para comparación
    def normalizar_objeto(obj):
        if isinstance(obj, dict):
            return {k: normalizar_objeto(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [normalizar_objeto(i) for i in obj]
        else:
            return obj

    datos1 = normalizar_objeto(data1)
    datos2 = normalizar_objeto(data2)

    report_lines = []
    report_lines.append(f"# Reporte de Diferencias: {os.path.basename(f1_path)} vs {os.path.basename(f2_path)}")
    report_lines.append(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("---")

    # Comparación simple de claves y valores de nivel 1 (puede expandirse para recursión profunda)
    keys1 = set(datos1.keys())
    keys2 = set(datos2.keys())

    # Claves eliminadas
    eliminadas = keys1 - keys2
    if eliminadas:
        report_lines.append("## 🔴 Eliminados (en v1)")
        for k in eliminadas:
            report_lines.append(f"- {k}")
        report_lines.append("")

    # Claves nuevas
    nuevas = keys2 - keys1
    if nuevas:
        report_lines.append("## 🟢 Nuevos (en v2)")
        for k in nuevas:
            report_lines.append(f"- {k}")
        report_lines.append("")

    # Claves modificadas
    comunes = keys1 & keys2
    modificados = {}
    for k in comunes:
        if datos1[k] != datos2[k]:
            modificados[k] = {"v1": datos1[k], "v2": datos2[k]}

    if modificados:
        report_lines.append("## 🟡 Modificados")
        for k, v in modificados.items():
            report_lines.append(f"- **{k}**: '{v['v1']}' -> '{v['v2']}'")
        report_lines.append("")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"Reporte generado exitosamente en: {output_file}")
    return True

def sincronizar_sql_dump(src, dst, output_file="diff_report.md"):
    """
    Intenta comparar dos archivos de dump de SQLite (formato sqlite3). 
    Nota: Comparar dumps binarios directamente es complejo sin parsear SQL.
    Esta función intenta leer el archivo como texto y buscar líneas SQL comunes.
    """
    if not os.path.exists(src) or not os.path.exists(dst):
        print(f"Error: Archivos SQL no encontrados.")
        return False

    try:
        with open(src, 'r', encoding='utf-8', errors='ignore') as f1, \
               open(dst, 'r', encoding='utf-8', errors='ignore') as f2:
            lines1 = set(f1.readlines())
            lines2 = set(f2.readlines())
    except Exception as e:
        print(f"Error al leer archivos: {e}")
        return False

    eliminadas = lines1 - lines2
    nuevas = lines2 - lines1

    report_lines = []
    report_lines.append(f"# Reporte de Diferencias SQL: {os.path.basename(src)} vs {os.path.basename(dst)}")
    report_lines.append(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("---")

    if eliminadas:
        report_lines.append("## 🔴 Líneas eliminadas")
        report_lines.append(f"Cantidad: {len(eliminadas)}")
        report_lines.append("")

    if nuevas:
        report_lines.append("## 🟢 Líneas nuevas")
        report_lines.append(f"Cantidad: {len(nuevas)}")
        report_lines.append("")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"Reporte SQL generado en: {output_file}")
    return True

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 23_sincronizador_base_datos_local.py <archivo1> <archivo2> [output_report]")
        print("Ejemplo: python3 23_sincronizador_base_datos_local.py backup_v1.json backup_v2.json")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "diff_report.md"

    # Intentar detectar si son JSON o SQL basado en extensión
    ext1 = os.path.splitext(file1)[1].lower()
    ext2 = os.path.splitext(file2)[1].lower()

    if ext1 in ['.json'] and ext2 in ['.json']:
        detectar_diferencias_json(file1, file2, output)
    elif ext1 in ['.sql', '.sqlite', '.db'] and ext2 in ['.sql', '.sqlite', '.db']:
        sincronizar_sql_dump(file1, file2, output)
    else:
        print("Extensión no soportada para comparación automática. Por favor usa .json o .sql/.sqlite")
        sys.exit(1)

if __name__ == "__main__":
    main()
