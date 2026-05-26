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

# ============================================================================
# Límites fijos para gráficas de convergencia de energía
# ============================================================================
# Estos límites se aplican a TODAS las gráficas U(t) — tanto la individual
# (plot_energy.py) como la de comparación batch (plot_batch_comparison.py).
# Se fijan para que la curvatura y la estabilización final del sistema se
# vean siempre con la misma escala, facilitando comparar visualmente
# distintas simulaciones.
#
# Modificar aquí si se cambia el régimen físico (otro N, otro modo de carga).
ENERGY_PLOT_X_MIN = 0
ENERGY_PLOT_X_MAX = 852.8  # rango fijo de movimientos aceptados (52 × 16.4)

# --- Eje Y modo REPULSIÓN (CHARGE_MODE=1, solo cargas +1) ---
# Energía siempre positiva, rango ajustado a la convergencia típica.
ENERGY_PLOT_Y_MIN = 120
ENERGY_PLOT_Y_MAX = 200

# --- Eje Y modo MIXTO (CHARGE_MODE=2, atracción + repulsión) ---
# La energía puede ser muy negativa (dipolos cercanos atraen). Se usa
# un rango fijo más amplio para no cortar la curva.
ENERGY_PLOT_Y_MIN_MIXED = -500
ENERGY_PLOT_Y_MAX_MIXED = 100

# Pasos de la rejilla en estas gráficas
# X: 50 separaciones de 16.4 en 16.4 cubren 0 → 820.
ENERGY_PLOT_X_MAJOR_STEP = 16.4
ENERGY_PLOT_X_MINOR_STEP = 4.1
ENERGY_PLOT_Y_MAJOR_STEP = 10
ENERGY_PLOT_Y_MAJOR_STEP_MIXED = 50    # paso mayor para modo mixto
ENERGY_PLOT_Y_MINOR_SUBDIV = 5         # número de subdivisiones por major

# Si está en modo mixto y los datos exceden el rango fijo, autoescala
# a un rango redondeado al múltiplo de Y_MAJOR_STEP_MIXED más cercano
# para que las etiquetas queden limpias.
ENERGY_PLOT_Y_AUTOFIT_MIXED = True

# ============================================================================
# Parámetros de mapas de calor (independientes de la simulación)
# ============================================================================
# HEATMAP_RESOLUTION controla SOLO la calidad visual de los mapas de calor
# del potencial V(x,y) y de la magnitud |E(x,y)|.
# No debe confundirse con GRID_RESOLUTION (malla de la simulación Fortran).
# Valor alto = imagen suave/orgánica pero más lenta de calcular.
HEATMAP_RESOLUTION = 400

# Resolución de las flechas en el quiver del campo eléctrico.
# Se mantiene más baja que HEATMAP_RESOLUTION para que las flechas
# sean legibles individualmente.
QUIVER_RESOLUTION = 28

# Softening visual para suavizar las divergencias del potencial cerca
# de las cargas en los mapas de calor. Físicamente equivale a tratar
# cada carga puntual como un blob de radio EPSILON_VIZ a nivel gráfico,
# evitando "spikes" de 1 píxel que distorsionan la escala de color.
# No altera la simulación: solo se usa en render de heatmaps.
EPSILON_VIZ = 0.15


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
        
        # Carga tolerante: con 8+ líneas leemos lo que haya. Si falta
        # GRID_RESOLUTION (línea 9), se mantiene el default global.
        if len(lines) >= 8:
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
            if len(lines) >= 9:
                GRID_RESOLUTION = int(lines[8])

            print(f"   Parámetros cargados desde: {param_file}")
            print(f"    N particulas: {N_PARTICLES}")
            print(f"    L dominio: {L_DOMAIN}")
            print(f"    Delta movimiento: {DELTA_MOVE}")
            print(f"    Modo de carga: {CHARGE_MODE} "
                   f"({'repulsión' if CHARGE_MODE == 1 else 'mixto'})")
            print(f"    Resolucion malla: {GRID_RESOLUTION}")
            
    except Exception as e:
        print(f"[WARNING] Error al leer parámetros: {e}")
        print("[WARNING] Usando valores por defecto.")


# Cargar los parámetros al importar config.py
load_simulation_parameters()

# ============================================================================
# Parámetros de video
# ============================================================================
# Estrategia: duración fija, frames objetivo, FPS derivado.
# Si la simulación produce más configuraciones que VIDEO_TARGET_FRAMES,
# se hace subsampling uniforme. Si produce menos, se interpolan posiciones
# entre configuraciones consecutivas para que el video se vea fluido.
VIDEO_DURATION_S = 5.0     # Duración objetivo del video (segundos)
VIDEO_TARGET_FRAMES = 150  # Número total de frames a renderizar
VIDEO_FPS = VIDEO_TARGET_FRAMES / VIDEO_DURATION_S  # = 30 fps
VIDEO_QUALITY = 9          # 0-10, mayor = mejor calidad
VIDEO_FRAME_SIZE = (960, 960)  # ancho x alto, fijo => sin warnings ffmpeg
VIDEO_FRAME_DPI = 120

# Modo de cubrimiento cuando hay menos configuraciones que TARGET_FRAMES:
#   'nearest' — cada frame muestra la configuración real más cercana.
#               Las cargas saltan en pasos discretos entre celdas de la
#               malla (respeta el snap-to-grid de la simulación).
#               Recomendado para conservar el "look" original del video.
#   'linear'  — interpolación lineal entre configuraciones vecinas.
#               Movimiento suave pero las posiciones intermedias quedan
#               fuera de la malla discreta.
VIDEO_INTERPOLATION_MODE = 'nearest'

# Mostrar la cuadrícula completa GRID_RESOLUTION en los frames del video.
# Si True, se dibujan ~GRID_RESOLUTION líneas por eje, idéntico al
# "look" original del video. Si False, se usa MaxNLocator (eje limpio
# como en los heatmaps).
VIDEO_SHOW_FULL_GRID = True

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
