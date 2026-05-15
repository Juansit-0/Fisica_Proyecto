#!/bin/bash
#===============================================================================
# Script para ejecutar la GUI Interactiva (usa entorno virtual)
#===============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

cd "$PROJECT_DIR"

echo "=========================================="
echo "  GUI INTERACTIVA - SIMULACIÓN DE CARGAS"
echo "=========================================="
echo ""

# Paso 1: Verificar entorno virtual
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  Entorno virtual no encontrado."
    echo "   Ejecuta primero: ./setup_venv.sh"
    echo ""
    read -p "¿Quieres configurar el entorno ahora? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        ./setup_venv.sh
    else
        echo "   Saliendo..."
        exit 1
    fi
fi

# Paso 2: Activar entorno virtual
echo "[1/2] Activando entorno virtual..."
source "$VENV_DIR/bin/activate"

# Paso 3: Iniciar GUI
echo "[2/2] Iniciando servidor Streamlit..."
echo ""
echo "  La GUI se abrirá en tu navegador."
echo "  Si no se abre automáticamente, visita:"
echo "  http://localhost:8501"
echo ""
echo "  Presiona Ctrl+C para detener el servidor."
echo ""
echo "=========================================="
echo ""

# Ejecutar la GUI
streamlit run src/python/gui_app.py --server.headless false
