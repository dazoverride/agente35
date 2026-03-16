# Sintetizador de Voz y Texto (17_sintetizador_voz_texto)

## Descripción
Un asistente de voz interactivo que combina reconocimiento de voz (Speech-to-Text) y síntesis de voz (Text-to-Speech) en Python. Permite al usuario interactuar mediante comandos de voz o ingresar archivos de texto para su lectura.

## Características
- Reconocimiento de voz en español.
- Síntesis de voz con motor `pyttsx3`.
- Comandos de voz predefinidos (saludar, hora, fecha, ayuda, salir).
- Lectura de archivos de texto desde el sistema de archivos.
- Interfaz CLI sencilla.

## Requisitos
- Python 3.7+
- `speech_recognition` (reconocimiento de voz)
- `pyttsx3` (síntesis de voz)

## Instalación
```bash
pip install speech_recognition pyttsx3
```

## Uso
1. Ejecuta el script: `python 17_sintetizador_voz_texto.py`
2. Selecciona la opción 1 para escuchar comandos de voz.
3. Selecciona la opción 2 para leer un archivo de texto.
4. Usa los comandos de voz disponibles: "hola", "hora", "fecha", "ayuda", "adios".

## Notas
- El reconocimiento de voz requiere micrófono.
- La síntesis de voz usa la voz por defecto del sistema.
- Asegúrate de tener el micrófono conectado y funcionando.
