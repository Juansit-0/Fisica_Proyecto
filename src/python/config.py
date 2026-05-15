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
COLOR_BACKGROUND = '#1D3557'  # Azul oscuro para fondo
COLOR_ACCENT = '#F1FAEE'      # Blanco cremoso para acentos
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

# Parámetros del dominio (debe coincidir con Fortran)
L_DOMAIN = 10.0

# Parámetros de campo eléctrico/potencial
GRID_RESOLUTION = 100  # Puntos por eje para mapas de calor
K_COULOMB = 1.0
EPSILON_SOFT = 1.0e-2

# ============================================================================
# Parámetros de video
# ============================================================================
VIDEO_FPS = 15
VIDEO_QUALITY = 8  # 0-10, mayor = mejor calidad

# ============================================================================
# Estilo de matplotlib
# ============================================================================
MATPLOTLIB_STYLE = {
    'figure.facecolor': '#0D1117',
    'axes.facecolor': '#161B22',
    'axes.edgecolor': '#30363D',
    'axes.labelcolor': '#C9D1D9',
    'text.color': '#C9D1D9',
    'xtick.color': '#8B949E',
    'ytick.color': '#8B949E',
    'grid.color': '#21262D',
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
