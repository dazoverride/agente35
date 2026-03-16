import random
import os

# Meme Generator CLI Tool
# Genera memes aleatorios combinando plantillas de texto con imágenes de placeholder.

TEMPLATES = [
    "Top Text: {texto_superior}\nBottom Text: {texto_inferior}",
    "Image Text: {texto_central}",
    "Caption: {texto_cabecera}\n{texto_pie}"  
]

PALABRAS_RIMAS = [
    "banana", "pan", "man", "van", "can", "fan", "tan",
    "gato", "lato", "rato", "bato", "mato", "pato",
    "codigo", "negocio", "negocio", "ocio", "ocio", "radio"
]

def generar_texto_random():
    return random.choice(PALABRAS_RIMAS)

def crear_memes():
    os.makedirs("memes_generados", exist_ok=True)
    
    for i in range(5):
        t1 = generar_texto_random()
        t2 = generar_texto_random()
        
        template = random.choice(TEMPLATES)
        contenido = template.format(
            texto_superior=t1,
            texto_inferior=t2,
            texto_central=f"{t1} & {t2}",
            texto_cabecera=t1,
            texto_pie=t2
        )
        
        with open(f"memes_generados/meme_{i+1}.txt", "w") as f:
            f.write(contenido)
        
        print(f"Creado: memes_generados/meme_{i+1}.txt")

if __name__ == "__main__":
    print("Iniciando Fábrica de Memes...")
    crear_memes()
    print("¡Producción completada!")