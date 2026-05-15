#===============================================================================
# Makefile — Simulación de Cargas Electrostáticas
#
# Targets principales:
#   make compile     - Compilar el código Fortran
#   make run_sim     - Ejecutar la simulación
#   make visualize   - Ejecutar pipeline de visualización Python
#   make video       - Generar video de la evolución
#   make all         - Pipeline completo (compile + run + visualize + video)
#   make clean       - Limpiar archivos generados
#   make clean_data  - Limpiar solo datos de salida
#
# Autor: Proyecto Física II — Universidad Cooperativa de Colombia
#===============================================================================

# Compilador y flags
FC = gfortran
SDKROOT := $(shell xcrun --show-sdk-path 2>/dev/null)
export SDKROOT

# Flags de optimización de alto rendimiento (versión release)
# -Ofast: Máxima optimización posible (incluye todas las de -O3 y más)
# -march=native: Optimizar para la CPU actual
# -ffast-math: Aritmética de punto flotante optimizada (seguro para este problema)
# -funroll-loops: Desenrollar bucles
# -floop-interchange: Intercambiar bucles para mejor localidad de caché
# -finline-functions: Inlinear funciones
FFLAGS = -Ofast -march=native -funroll-loops -floop-interchange \
         -finline-functions -fno-signed-zeros -fno-trapping-math \
         -Wall -Wextra -std=f2008 -fall-intrinsics

# Versión de debug
FFLAGS_DEBUG = -g -fcheck=all -fbacktrace -Wall -Wextra -std=f2008 -fall-intrinsics

# Directorios
SRC_DIR = src/fortran
BUILD_DIR = build
BIN_DIR = bin
PYTHON_DIR = src/python
DATA_DIR = data/output

# Archivos fuente (orden de compilación por dependencias)
SRCS = $(SRC_DIR)/mod_constants.f90 \
       $(SRC_DIR)/mod_types.f90 \
       $(SRC_DIR)/mod_performance.f90 \
       $(SRC_DIR)/mod_energy.f90 \
       $(SRC_DIR)/mod_io.f90 \
       $(SRC_DIR)/mod_simulation.f90 \
       $(SRC_DIR)/main.f90

# Ejecutable
TARGET = $(BIN_DIR)/electrostatic_sim

# ============================================================================
# Targets principales
# ============================================================================

.PHONY: all compile run_sim visualize video clean clean_data dirs phase1 phase2

# Pipeline completo
all: dirs compile run_sim visualize video
	@echo ""
	@echo "  Pipeline completo ejecutado exitosamente."
	@echo ""

# Solo Fase 1: Cargas positivas
phase1: dirs compile
	@echo "  Configurando Fase 1: Solo cargas positivas..."
	@sed -i '' '5s/.*/1/' data/input/simulation_params.txt 2>/dev/null || \
	 python3 -c "lines=open('data/input/simulation_params.txt').readlines(); lines[4]='1\n'; open('data/input/simulation_params.txt','w').writelines(lines)"
	@$(MAKE) run_sim visualize video

# Solo Fase 2: Cargas mixtas
phase2: dirs compile
	@echo "  Configurando Fase 2: Cargas mixtas (+/-)..."
	@sed -i '' '5s/.*/2/' data/input/simulation_params.txt 2>/dev/null || \
	 python3 -c "lines=open('data/input/simulation_params.txt').readlines(); lines[4]='2\n'; open('data/input/simulation_params.txt','w').writelines(lines)"
	@$(MAKE) run_sim visualize video

# ============================================================================
# Compilación
# ============================================================================

dirs:
	@mkdir -p $(BUILD_DIR) $(BIN_DIR) $(DATA_DIR)/configurations results/figures results/frames results/videos

compile: dirs $(TARGET)
	@echo "  Compilacion exitosa."

$(TARGET): $(SRCS)
	@echo "  Compilando modulos Fortran..."
	$(FC) $(FFLAGS) -J$(BUILD_DIR) -o $(TARGET) $(SRCS)

# Compilación en modo debug
debug: dirs
	@echo "  Compilando en modo DEBUG..."
	$(FC) $(FFLAGS_DEBUG) -J$(BUILD_DIR) -o $(TARGET) $(SRCS)
	@echo "  Compilacion debug exitosa."

# ============================================================================
# Ejecución
# ============================================================================

run_sim: $(TARGET)
	@echo ""
	@echo "  Ejecutando simulacion..."
	@echo ""
	@cd $(CURDIR) && ./$(TARGET)

visualize:
	@echo ""
	@echo "  Ejecutando pipeline de visualizacion..."
	@echo ""
	python3 $(PYTHON_DIR)/run_visualization.py

video:
	@echo ""
	@echo "  Generando video..."
	@echo ""
	python3 $(PYTHON_DIR)/video_generator.py

# ============================================================================
# Limpieza
# ============================================================================

clean:
	@echo "  Limpiando archivos de compilacion..."
	rm -rf $(BUILD_DIR)/*.mod $(BUILD_DIR)/*.o $(TARGET)

clean_data:
	@echo "  Limpiando datos de salida..."
	rm -f $(DATA_DIR)/energy_log.csv
	rm -f $(DATA_DIR)/initial_config.csv
	rm -f $(DATA_DIR)/final_config.csv
	rm -rf $(DATA_DIR)/configurations/*
	rm -rf results/figures/*
	rm -rf results/frames/*
	rm -rf results/videos/*

clean_all: clean clean_data
	@echo "  Limpieza completa."
