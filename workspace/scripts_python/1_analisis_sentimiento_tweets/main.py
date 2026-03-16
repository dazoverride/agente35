#!/usr/bin/env python3
"""
Analizador de Sentimiento Básico para Texto
Utiliza un diccionario de palabras clave para determinar si el texto es positivo, negativo o neutro.
"""

import re
from collections import Counter

# Diccionario básico de palabras clave (puedes expandirlo)
PALABRAS_POSITIVAS = {
    'bueno', 'excelente', 'genial', 'fantastico', 'amable', 'feliz', 'contento', 'rico', 'rapido',
    'facil', 'claro', 'correcto', 'perfecto', 'gran', 'grande', 'sano', 'limpio', 'seguro', 'gratis'
}

PALABRAS_NEGATIVAS = {
    'malo', 'pobre', 'terrible', 'horrible', 'feo', 'triste', 'enojado', 'lento', 'difficult',
    'error', 'problema', 'roto', 'sucio', 'peligroso', 'pago', 'costoso', 'complejo', 'confuso'
}

PUNCTUACIONES_DE_ENFASIS = {'.', '!', '?', '!!', '...'}

def limpiar_texto(texto):
    """Convierte el texto a minúsculas y elimina caracteres no alfabéticos."""
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúñü ]', '', texto)
    return texto

def analizar_sentimiento(texto):
    """
    Analiza el sentimiento del texto dado.
    Retorna un diccionario con puntajes y la clasificación final.
    """
    texto_limpio = limpiar_texto(texto)
    palabras = texto_limpio.split()
    
    contador_positivo = 0
    contador_negativo = 0
    palabras_encontradas = []
    
    for palabra in palabras:
        if palabra in PALABRAS_POSITIVAS:
            contador_positivo += 1
            palabras_encontradas.append(f"{palabra}+")
        elif palabra in PALABRAS_NEGATIVAS:
            contador_negativo += 1
            palabras_encontradas.append(f"{palabra}-")
    
    # Lógica de ponderación simple: signos de exclamación o interrogación multiplican el impacto
    multiplicador = 1
    for p in texto:
        if p in PUNCTUACIONES_DE_ENFASIS:
            multiplicador += 0.5
    
    score_positivo = contador_positivo * multiplicador
    score_negativo = contador_negativo * multiplicador
    
    total_score = score_positivo - score_negativo
    
    if total_score > 0.5:
        clasificacion = "Positivo"
    elif total_score < -0.5:
        clasificacion = "Negativo"
    else:
        clasificacion = "Neutro"
    
    return {
        'texto_analizado': texto,
        'palabras_positivas': contador_positivo,
        'palabras_negativas': contador_negativo,
        'palabras_clave_encontradas': palabras_encontradas,
        'puntuacion_neta': round(total_score, 2),
        'sentimiento': clasificacion
    }

def main():
    # Pruebas de ejemplo
    casos_prueba = [
        "Este software es excelente y muy fácil de usar.",
        "Me encanta la velocidad, ¡es increíble!",
        "El servicio fue malo, el sistema se rompió y no ayuda.",
        "El clima hoy es normal, ni muy frío ni muy caliente.",
        "¡Qué horror! El precio es terrible y la calidad es pésima.",
        "Todo está bien, aunque un poco costoso.",
        "Gracias por tu ayuda, eres muy amable.",
        "Tengo muchos problemas con la instalación, es muy confuso."
    ]
    
    print(f"{'='*60}")
    print(f"{'ANALIZADOR DE SENTIMIENTO AUTÓNOMO':^60}")
    print(f"{'='*60}\n")
    
    for caso in casos_prueba:
        print(f"\nTexto: \"{caso}\"")
        resultado = analizar_sentimiento(caso)
        print(f"  Sentimiento detectado: {resultado['sentimiento']}")
        print(f"  Palabras positivas: {resultado['palabras_positivas']}")
        print(f"  Palabras negativas: {resultado['palabras_negativas']}")
        print(f"  Puntuación neta: {resultado['puntuacion_neta']}")
        if resultado['palabras_clave_encontradas']:
            print(f"  Palabras clave: {', '.join(resultado['palabras_clave_encontradas'])}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main()
