import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from tests.llama_test import ejecutar_bateria, CARPETA_MODELOS

def main():
    modelos_a_probar = [
        "Qwen_Qwen3.5-4B-Q8_0.gguf",
        "google_gemma-4-E4B-it-Q4_K_M.gguf"
    ]
    
    # Verificamos si existen
    modelos_disponibles = [f for f in os.listdir(CARPETA_MODELOS) if f.endswith(".gguf")]
    modelos_finales = [m for m in modelos_a_probar if m in modelos_disponibles]
    
    if not modelos_finales:
        print("No se encontraron los modelos para la prueba rápida.")
        return

    prompts = [
        "Explica de forma muy breve y sencilla, en un solo párrafo corto, qué es un agujero negro."
    ]

    print("🚀 INICIANDO PRUEBA RÁPIDA DE COMPARACIÓN (GPU) 🚀")
    print("Modelos a evaluar:", modelos_finales)
    
    for modelo in modelos_finales:
        print(f"\n{'='*80}")
        print(f"🧪 EVALUANDO MODELO: {modelo}")
        print(f"{'='*80}")
        ejecutar_bateria(prompts, mod_thinking_activado=False, modelo_archivo=modelo)

    print("\n✅ PRUEBA RÁPIDA COMPLETADA.")

if __name__ == "__main__":
    main()
