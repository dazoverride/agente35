import random
import math

def generar_sintetizador_frecuencia():
    """
    Genera una onda sinusoidal pura con frecuencia variable.
    """
    frecuencia = 440  # Hz (Nota La4)
    amplitud = 0.5
    sample_rate = 44100
    duracion = 0.5  # segundos
    
    muestras = int(sample_rate * duracion)
    onda = []
    for i in range(muestras):
        t = i / sample_rate
        valor = amplitud * math.sin(2 * math.pi * frecuencia * t)
        onda.append(int(valor * 32767)) # Convertir a rango 16-bit
    
    return onda, sample_rate

def aplicar_efecto_modulacion(onda, tasa_modulacion, frecuencia_modulacion):
    """
    Aplica una modulación de frecuencia (FM) simple.
    """
    nueva_onda = []
    for i, valor in enumerate(onda):
        frecuencia_instantanea = frecuencia_modulacion + tasa_modulacion * math.sin(2 * math.pi * frecuencia_modulacion * i / 44100)
        t = i / 44100
        valor_modulado = 0.5 * math.sin(2 * math.pi * frecuencia_instantanea * t)
        nueva_onda.append(int(valor_modulado * 32767))
    return nueva_onda

def guardar_audio(onda, sample_rate, nombre_archivo="sintesis_generativa.wav"):
    """
    Guarda el audio generado en formato WAV básico.
    Nota: Requiere la librería 'wave' y 'struct'.
    """
    try:
        with wave.open(nombre_archivo, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16 bits
            wav_file.setframerate(sample_rate)
            
            for muestra in onda:
                # Asegurar que la muestra esté en rango de 16 bits signed
                if muestra > 32767: muestra = 32767
                if muestra < -32767: muestra = -32767
                wav_file.writeframes(struct.pack('h', muestra))
        print(f"Audio guardado exitosamente en: {nombre_archivo}")
    except Exception as e:
        print(f"Error al guardar audio: {e}")

def main():
    print("Iniciando Sintetizador de Audio Generativo...")
    
    # Generar onda base
    onda_base, sr = generar_sintetizador_frecuencia()
    
    # Aplicar modulación para crear un efecto más complejo
    onda_procesada = aplicar_efecto_modulacion(onda_base, 50, 10)  # Tasa y frecuencia de modulación
    
    # Guardar resultado
    guardar_audio(onda_procesada, sr, "output_sintetizador_generativo.wav")
    print("Proceso completado.")

if __name__ == "__main__":
    main()
