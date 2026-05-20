#!/bin/bash
# Script de instalación automática de Agente35 en Linux (Ubuntu/Debian)

echo "=================================================="
echo "🚀 INICIANDO INSTALACIÓN DE AGENTE35 EN VPS LINUX"
echo "=================================================="

# 1. Actualizar sistema e instalar dependencias básicas
echo "[1/4] Actualizando sistema e instalando dependencias (Python, Unzip, Screen)..."
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv wget unzip screen -y

# 2. Descargar e instalar llama.cpp precompilado para Ubuntu
echo "[2/4] Descargando llama.cpp (Motor de Inferencia)..."
if [ ! -d "llama-b9245-bin-ubuntu-x64" ]; then
    wget https://github.com/ggerganov/llama.cpp/releases/download/b9245/llama-b9245-bin-ubuntu-x64.tar.gz
    mkdir -p llama-b9245-bin-ubuntu-x64
    tar -xzf llama-b9245-bin-ubuntu-x64.tar.gz -C llama-b9245-bin-ubuntu-x64
    rm llama-b9245-bin-ubuntu-x64.tar.gz
    chmod +x llama-b9245-bin-ubuntu-x64/llama-server
    echo "✅ llama.cpp instalado."
else
    echo "✅ llama.cpp ya está instalado."
fi

# 3. Descargar el modelo de IA (Gemma 4B)
echo "[3/4] Descargando el cerebro de la IA (Gemma 4B)... Esto puede tardar varios minutos."
mkdir -p models
if [ ! -f "models/google_gemma-4-E4B-it-Q4_K_M.gguf" ]; then
    wget -O models/google_gemma-4-E4B-it-Q4_K_M.gguf https://huggingface.co/google/gemma-4-E4B-it-Q4_K_M.gguf?download=true
    echo "✅ Modelo descargado."
else
    echo "✅ El modelo ya existe en la carpeta models/."
fi

# 4. Crear el entorno virtual de Python y configurar dependencias
echo "[4/4] Configurando entorno virtual de Python..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install openai requests

echo "=================================================="
echo "🎉 INSTALACIÓN COMPLETADA CON ÉXITO 🎉"
echo "=================================================="
echo ""
echo "Para arrancar tu agente, simplemente ejecuta:"
echo "  source .venv/bin/activate"
echo "  python tests/llama_tools.py"
echo ""
echo "Recuerda: Si quieres que el agente siga corriendo al cerrar la consola SSH, usa screen:"
echo "  screen -S mi_agente"
echo "  python tests/llama_tools.py"
echo "  (Presiona Ctrl+A y luego D para dejarlo en segundo plano)"
