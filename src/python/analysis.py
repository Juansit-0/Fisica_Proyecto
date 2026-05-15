"""
analysis.py — Análisis estadístico y físico de la simulación

Análisis de:
- Distribución radial de cargas
- Distancias mínimas entre partículas
- Estadísticas de convergencia
- Resumen del sistema

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import (setup_matplotlib, ensure_dirs, FIGURES_DIR,
                    L_DOMAIN, DPI, FIGURE_SIZE, MATPLOTLIB_STYLE)
from data_loader import (load_energy_log, load_initial_configuration,
                          load_final_configuration, get_positions_and_charges)


def compute_pairwise_distances(x, y):
    """Calcula todas las distancias entre pares de partículas."""
    n = len(x)
    distances = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            d = np.sqrt((x[i]-x[j])**2 + (y[i]-y[j])**2)
            distances.append(d)
    return np.array(distances)


def plot_distance_histogram():
    """Histograma de distancias entre pares: inicial vs final."""
    plt.rcParams.update(MATPLOTLIB_STYLE)
    
    df_i = load_initial_configuration()
    df_f = load_final_configuration()
    xi, yi, _ = get_positions_and_charges(df_i)
    xf, yf, _ = get_positions_and_charges(df_f)

    d_initial = compute_pairwise_distances(xi, yi)
    d_final = compute_pairwise_distances(xf, yf)

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    ax.hist(d_initial, bins=30, alpha=0.5, color='#FF6B6B', label='Inicial',
            density=True, edgecolor='white', linewidth=0.5)
    ax.hist(d_final, bins=30, alpha=0.5, color='#51CF66', label='Final',
            density=True, edgecolor='white', linewidth=0.5)

    ax.set_xlabel('Distancia entre pares', fontsize=13)
    ax.set_ylabel('Densidad', fontsize=13)
    ax.set_title('Distribución de Distancias — Inicial vs Final',
                 fontsize=15, fontweight='bold', pad=12)
    ax.legend(fontsize=11, framealpha=0.8, facecolor='#161B22', edgecolor='#30363D')
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    filepath = FIGURES_DIR / 'distance_histogram.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Histograma de distancias: {filepath}")


def plot_radial_distribution():
    """Distribución de distancias al centro del dominio."""
    plt.rcParams.update(MATPLOTLIB_STYLE)
    
    df_i = load_initial_configuration()
    df_f = load_final_configuration()
    xi, yi, _ = get_positions_and_charges(df_i)
    xf, yf, _ = get_positions_and_charges(df_f)

    r_initial = np.sqrt(xi**2 + yi**2)
    r_final = np.sqrt(xf**2 + yf**2)

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    ax.hist(r_initial, bins=20, alpha=0.5, color='#FF6B6B', label='Inicial',
            density=True, edgecolor='white', linewidth=0.5)
    ax.hist(r_final, bins=20, alpha=0.5, color='#51CF66', label='Final',
            density=True, edgecolor='white', linewidth=0.5)

    ax.set_xlabel('Distancia al centro', fontsize=13)
    ax.set_ylabel('Densidad', fontsize=13)
    ax.set_title('Distribución Radial — Distancia al Centro',
                 fontsize=15, fontweight='bold', pad=12)
    ax.legend(fontsize=11, framealpha=0.8, facecolor='#161B22', edgecolor='#30363D')
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    filepath = FIGURES_DIR / 'radial_distribution.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Distribución radial: {filepath}")


def print_summary_statistics():
    """Imprime resumen estadístico completo."""
    print("\n  ")
    print("  RESUMEN ESTADÍSTICO")
    print("  \n")

    df_energy = load_energy_log()
    df_f = load_final_configuration()
    xf, yf, qf = get_positions_and_charges(df_f)

    e_init = df_energy['energy'].iloc[0]
    e_final = df_energy['energy'].iloc[-1]
    reduction = (e_init - e_final) / abs(e_init) * 100

    d_final = compute_pairwise_distances(xf, yf)

    print(f"  Energía inicial:    {e_init:.6f}")
    print(f"  Energía final:      {e_final:.6f}")
    print(f"  Reducción:          {reduction:.2f}%")
    print(f"  Dist. mínima (fin): {d_final.min():.4f}")
    print(f"  Dist. media (fin):  {d_final.mean():.4f}")
    print(f"  Dist. máxima (fin): {d_final.max():.4f}")
    print(f"  Cargas +1:          {np.sum(qf > 0)}")
    print(f"  Cargas -1:          {np.sum(qf < 0)}")
    print(f"  Radio medio (fin):  {np.sqrt(xf**2 + yf**2).mean():.4f}")
    print()


def generate_analysis():
    """Pipeline principal de análisis."""
    print("\n  ")
    print("  GENERANDO ANÁLISIS ESTADÍSTICO")
    print("  \n")
    print_summary_statistics()
    plot_distance_histogram()
    plot_radial_distribution()


if __name__ == '__main__':
    setup_matplotlib()
    ensure_dirs()
    generate_analysis()
