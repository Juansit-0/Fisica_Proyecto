#!/bin/bash
#===============================================================================
# Script para configurar el entorno virtual de Python
#===============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "=========================================="
echo "  CONFIGURANDO ENTORNO VIRTUAL"
echo "=========================================="
echo ""

# Paso 1: Crear entorno virtual
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/3] Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
    echo "  ✅ Entorno virtual creado en: $VENV_DIR"
else
    echo "[1/3] Entorno virtual ya existe. Saltando..."
fi

echo ""

# Paso 2: Activar entorno virtual e instalar dependencias
echo "[2/3] Instalando dependencias..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/src/python/requirements_gui.txt"

echo ""
echo "[3/3] ✅ Instalación completada!"
echo ""
echo "=========================================="
echo "  Para activar el entorno manualmente:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "  Para ejecutar la GUI:"
echo "  ./run_gui.sh"
echo "=========================================="
