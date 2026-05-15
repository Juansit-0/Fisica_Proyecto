#!/bin/bash
#===============================================================================
# run_all.sh — Script maestro de ejecución completa
#
# Ejecuta el pipeline completo del proyecto:
#   1. Compilar código Fortran
#   2. Ejecutar simulación (Fase 1: cargas positivas)
#   3. Ejecutar pipeline de visualización Python
#   4. Generar video
#   5. Ejecutar simulación (Fase 2: cargas mixtas)
#   6. Visualizar Fase 2
#
# Uso:
#   chmod +x run_all.sh
#   ./run_all.sh          # Pipeline completo
#   ./run_all.sh phase1   # Solo Fase 1 (cargas positivas)
#   ./run_all.sh phase2   # Solo Fase 2 (cargas mixtas)
#
# Autor: Proyecto Física II — Universidad Cooperativa de Colombia
#===============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}${NC}"
echo -e "${BLUE}  SIMULACIÓN DE CARGAS ELECTROSTÁTICAS           ${NC}"
echo -e "${BLUE}  Pipeline Completo                              ${NC}"
echo -e "${BLUE}${NC}"
echo ""

MODE=${1:-"all"}

run_phase() {
    local phase=$1
    local charge_mode=$2
    local desc=$3

    echo -e "${YELLOW} FASE ${phase}: ${desc} ${NC}"
    echo ""

    # Configurar modo de cargas
    python3 -c "
lines = open('data/input/simulation_params.txt').readlines()
lines[4] = '${charge_mode}\n'
open('data/input/simulation_params.txt', 'w').writelines(lines)
"

    # Limpiar datos previos
    make clean_data 2>/dev/null || true

    # Compilar
    echo -e "${BLUE}[1/4] Compilando Fortran...${NC}"
    make compile

    # Ejecutar simulación
    echo -e "${BLUE}[2/4] Ejecutando simulación...${NC}"
    make run_sim

    # Visualizar
    echo -e "${BLUE}[3/4] Generando visualizaciones...${NC}"
    make visualize

    # Video
    echo -e "${BLUE}[4/4] Generando video...${NC}"
    make video

    # Mover resultados a carpeta con nombre de fase
    mkdir -p "results/phase${phase}"
    cp results/figures/* "results/phase${phase}/" 2>/dev/null || true
    cp results/videos/* "results/phase${phase}/" 2>/dev/null || true

    echo -e "${GREEN}Fase ${phase} completada.${NC}"
    echo ""
}

case $MODE in
    "phase1")
        run_phase 1 1 "Solo cargas positivas (+1)"
        ;;
    "phase2")
        run_phase 2 2 "Cargas mixtas (+1 y -1)"
        ;;
    "all")
        run_phase 1 1 "Solo cargas positivas (+1)"
        run_phase 2 2 "Cargas mixtas (+1 y -1)"
        ;;
    *)
        echo -e "${RED}Modo no reconocido: $MODE${NC}"
        echo "Uso: ./run_all.sh [all|phase1|phase2]"
        exit 1
        ;;
esac

echo -e "${GREEN}${NC}"
echo -e "${GREEN}  PIPELINE COMPLETO FINALIZADO                    ${NC}"
echo -e "${GREEN}${NC}"
echo ""
echo "Resultados disponibles en:"
echo "  results/figures/  — Gráficas científicas"
echo "  results/videos/   — Videos de evolución"
echo "  results/phase1/   — Resultados Fase 1"
echo "  results/phase2/   — Resultados Fase 2"
echo ""
