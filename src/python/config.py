"""
config.py — Configuración centralizada del pipeline de visualización

Centraliza rutas, parámetros de estilo y constantes de visualización
para garantizar consistencia en todas las gráficas del proyecto.

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import os
from pathlib import Path

# ============================================================================
# Rutas del proyecto
# ============================================================================

# Raíz del proyecto (relativo a src/python/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Directorios de datos
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
CONFIG_DIR = OUTPUT_DIR / "configurations"

# Directorios de resultados
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
FRAMES_DIR = RESULTS_DIR / "frames"
VIDEOS_DIR = RESULTS_DIR / "videos"

# Archivos de datos principales
ENERGY_LOG = OUTPUT_DIR / "energy_log.csv"
INITIAL_CONFIG = OUTPUT_DIR / "initial_config.csv"
FINAL_CONFIG = OUTPUT_DIR / "final_config.csv"

# ============================================================================
# Parámetros de visualización
# ============================================================================

# Resolución de gráficas
DPI = 200
FIGURE_SIZE = (10, 8)
FIGURE_SIZE_WIDE = (14, 6)
FIGURE_SIZE_SQUARE = (8, 8)

# Colores del proyecto (basados en el PDF del proyecto)
COLOR_POSITIVE = '#E63946'    # Rojo vibrante para cargas +1
COLOR_NEGATIVE = '#457B9D'    # Azul profundo para cargas -1
COLOR_BACKGROUND = '#FFFFFF'  # Blanco para fondo
COLOR_ACCENT = '#1D3557'      # Azul oscuro para acentos
COLOR_ENERGY = '#E76F51'      # Naranja coral para curvas de energía
COLOR_GRID = '#A8DADC'        # Azul claro para grillas

# Paleta de colores para mapas de calor
CMAP_POTENTIAL = 'RdBu_r'     # Divergente: rojo(+) a azul(-)
CMAP_FIELD = 'inferno'        # Secuencial: campo eléctrico magnitud
CMAP_DENSITY = 'viridis'      # Secuencial: densidad

# Tamaño de marcadores en scatter plots
MARKER_SIZE = 80
MARKER_EDGE_COLOR = 'white'
MARKER_EDGE_WIDTH = 0.8

# Parámetros del dominio y simulación (se cargan desde simulation_params.txt)
# Valores por defecto (se sobreescriben si el archivo existe)
L_DOMAIN = 10.0
GRID_RESOLUTION = 50  # Puntos por eje para mapas de calor
N_PARTICLES = 50
DELTA_MOVE = 0.25
MAX_ITER = 500000
CHARGE_MODE = 1
SAVE_EVERY = 100
PRINT_EVERY = 10000
SEED_VALUE = 0

# Parámetros de campo eléctrico/potencial
K_COULOMB = 1.0
EPSILON_SOFT = 1.0e-2


def load_simulation_parameters():
    """
    Carga los parámetros de simulación desde el mismo archivo que usa Fortran
    para garantizar consistencia entre Fortran y Python.
    """
    import csv
    from pathlib import Path
    
    param_file = INPUT_DIR / "simulation_params.txt"
    
    if not param_file.exists():
        print(f"[WARNING] Archivo de parámetros no encontrado: {param_file}")
        print("[WARNING] Usando valores por defecto.")
        return
    
    try:
        with open(param_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if len(lines) >= 9:
            global N_PARTICLES, L_DOMAIN, DELTA_MOVE, MAX_ITER, CHARGE_MODE
            global SAVE_EVERY, PRINT_EVERY, SEED_VALUE, GRID_RESOLUTION
            
            N_PARTICLES = int(lines[0])
            L_DOMAIN = float(lines[1])
            DELTA_MOVE = float(lines[2])
            MAX_ITER = int(lines[3])
            CHARGE_MODE = int(lines[4])
            SAVE_EVERY = int(lines[5])
            PRINT_EVERY = int(lines[6])
            SEED_VALUE = int(lines[7])
            GRID_RESOLUTION = int(lines[8])
            
            print(f"   Parámetros cargados desde: {param_file}")
            print(f"    N particulas: {N_PARTICLES}")
            print(f"    L dominio: {L_DOMAIN}")
            print(f"    Delta movimiento: {DELTA_MOVE}")
            print(f"    Resolucion malla: {GRID_RESOLUTION}")
            
    except Exception as e:
        print(f"[WARNING] Error al leer parámetros: {e}")
        print("[WARNING] Usando valores por defecto.")


# Cargar los parámetros al importar config.py
load_simulation_parameters()

# ============================================================================
# Parámetros de video
# ============================================================================
# VALOR ANTERIOR: VIDEO_FPS = 66.2 (muy alto, videos demasiado cortos)
# NUEVO VALOR: VIDEO_FPS = 4.0 (velocidad más lenta para ver más detalle)
VIDEO_FPS = 4.0
VIDEO_QUALITY = 8  # 0-10, mayor = mejor calidad

# ============================================================================
# Estilo de matplotlib
# ============================================================================
MATPLOTLIB_STYLE = {
    'figure.facecolor': '#FFFFFF',
    'axes.facecolor': '#FFFFFF',
    'axes.edgecolor': '#333333',
    'axes.labelcolor': '#000000',
    'text.color': '#000000',
    'xtick.color': '#000000',
    'ytick.color': '#000000',
    'grid.color': '#CCCCCC',
    'grid.alpha': 0.5,
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
}


def setup_matplotlib():
    """Configura matplotlib con estilo oscuro profesional."""
    import matplotlib
    matplotlib.use('Agg')  # Backend no interactivo
    import matplotlib.pyplot as plt
    plt.rcParams.update(MATPLOTLIB_STYLE)


def ensure_dirs():
    """Crea directorios de salida si no existen."""
    for d in [FIGURES_DIR, FRAMES_DIR, VIDEOS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
