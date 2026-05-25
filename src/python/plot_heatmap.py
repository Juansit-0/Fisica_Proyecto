"""
plot_heatmap.py — Mapas de calor del potencial eléctrico

Genera mapas de calor de V(x,y) para la configuración final,
calculando el potencial eléctrico en una grilla 2D y visualizándolo
con colormap divergente (rojo para V>0, azul para V<0).

Física:
    V(r) = k Σ_i q_i / |r - r_i|

El potencial diverge cerca de las cargas puntuales, por lo que
se usa saturación (clipping) para visualización.

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from config import (setup_matplotlib, ensure_dirs, FIGURES_DIR,
                    COLOR_POSITIVE, COLOR_NEGATIVE, MARKER_EDGE_COLOR,
                    L_DOMAIN, K_COULOMB, EPSILON_SOFT,
                    GRID_RESOLUTION, CMAP_POTENTIAL, DPI, FIGURE_SIZE)
from data_loader import load_final_configuration, get_positions_and_charges


def compute_potential_grid(x_charges, y_charges, q_charges, resolution=100):
    """
    Calcula el potencial eléctrico V(x,y) en una grilla 2D.
    
    V(r) = k Σ_i q_i / sqrt((x-x_i)² + (y-y_i)² + ε²)
    
    Args:
        x_charges, y_charges: posiciones de las cargas
        q_charges: valores de las cargas
        resolution: puntos por eje
        
    Returns:
        X, Y: meshgrid
        V: potencial en cada punto de la grilla
    """
    # Crear grilla
    x_grid = np.linspace(-L_DOMAIN, L_DOMAIN, resolution)
    y_grid = np.linspace(-L_DOMAIN, L_DOMAIN, resolution)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    # Calcular potencial (vectorizado con broadcasting)
    V = np.zeros_like(X)
    
    for i in range(len(x_charges)):
        dx = X - x_charges[i]
        dy = Y - y_charges[i]
        r = np.sqrt(dx**2 + dy**2 + EPSILON_SOFT**2)
        V += K_COULOMB * q_charges[i] / r
    
    return X, Y, V


def plot_potential_heatmap():
    """
    Genera mapa de calor del potencial eléctrico para la configuración final.
    """
    print("\n  ")
    print("  GENERANDO MAPA DE CALOR DEL POTENCIAL")
    print("  \n")
    
    # Cargar configuración final
    df = load_final_configuration()
    x, y, q = get_positions_and_charges(df)
    
    # Calcular potencial
    print("  Calculando potencial eléctrico en grilla...")
    X, Y, V = compute_potential_grid(x, y, q, resolution=GRID_RESOLUTION)
    
    # Saturar valores extremos para visualización
    # (el potencial diverge cerca de las cargas)
    v_percentile = np.percentile(np.abs(V), 95)
    V_clipped = np.clip(V, -v_percentile, v_percentile)
    
    print(f"  V_min = {V.min():.2f}, V_max = {V.max():.2f}")
    print(f"  Saturación al percentil 95: ±{v_percentile:.2f}")
    
    # === Gráfica ===
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    
    # Mapa de calor con colormap divergente
    norm = mcolors.TwoSlopeNorm(vmin=-v_percentile, vcenter=0, vmax=v_percentile)
    im = ax.pcolormesh(X, Y, V_clipped, cmap=CMAP_POTENTIAL,
                       norm=norm, shading='auto')
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, label='Potencial Eléctrico V(x,y)',
                        shrink=0.85, pad=0.02)
    cbar.ax.yaxis.label.set_color('#000000')
    cbar.ax.tick_params(colors='#000000')
    
    # Superponer posiciones de cargas
    pos_mask = q > 0
    neg_mask = q < 0
    
    if np.any(pos_mask):
        ax.scatter(x[pos_mask], y[pos_mask], c=COLOR_POSITIVE, s=50,
                   edgecolors='black', linewidths=1.0, zorder=10,
                   marker='o', label='+1')
    if np.any(neg_mask):
        ax.scatter(x[neg_mask], y[neg_mask], c=COLOR_NEGATIVE, s=50,
                   edgecolors='black', linewidths=1.0, zorder=10,
                   marker='s', label='−1')
    
    ax.set_xlim(-L_DOMAIN, L_DOMAIN)
    ax.set_ylim(-L_DOMAIN, L_DOMAIN)
    ax.set_aspect('equal')
    ax.set_xlabel('x', fontsize=13)
    ax.set_ylabel('y', fontsize=13)
    ax.set_title('Mapa de Calor — Potencial Eléctrico V(x,y)',
                 fontsize=15, fontweight='bold', pad=12)
    
    # Configurar ticks de malla basados en GRID_RESOLUTION
    grid_spacing = (2.0 * L_DOMAIN) / (GRID_RESOLUTION - 1)
    ticks = np.arange(-L_DOMAIN, L_DOMAIN + grid_spacing, grid_spacing)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.grid(True, alpha=0.15, color='#CCCCCC', linewidth=0.3, linestyle='-')
    ax.legend(loc='upper right', fontsize=7, framealpha=0.8,
              facecolor='#FFFFFF', edgecolor='#333333')
    
    # Rotar etiquetas del eje X para evitar superposicion y reducir tamaño de fuente
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
    
    plt.tight_layout()
    filepath = FIGURES_DIR / 'potential_heatmap.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Mapa de calor del potencial guardado: {filepath}")


def generate_heatmaps():
    """Pipeline principal de mapas de calor."""
    plot_potential_heatmap()


if __name__ == '__main__':
    setup_matplotlib()
    ensure_dirs()
    generate_heatmaps()
