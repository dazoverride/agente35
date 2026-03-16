# Sintetizador de Audio Generativo

Un script Python que genera ondas de audio sintéticas utilizando matemáticas básicas (senoides y modulación de frecuencia) y las guarda en formato WAV.

## ¿Qué hace?
Genera un archivo de audio WAV de baja latencia sin necesidad de instalar librerías de audio pesadas (como PyAudio o libros). Utiliza funciones matemáticas para crear tonos y efectos simples.

## Cómo ejecutarlo
```bash
python 27_sintetizador_audio_generativo.py
```

## Dependencias
- Python 3.x
- Librerías estándar: `math`, `struct`, `wave`

## Notas
- El archivo generado es de 16 bits, 44.1 kHz, mono.
- No incluye efectos avanzados de reverb o ecualización para mantener la simplicidad y modularidad.