"""
plot_field.py — Visualización del campo eléctrico

Genera dos tipos de visualización del campo eléctrico E(x,y):
1. Quiver plot: flechas indicando dirección y magnitud
2. Heatmap de |E(x,y)| con posiciones de cargas superpuestas

Física:
    E(r) = k Σ_i q_i (r - r_i) / |r - r_i|³

El campo apunta DESDE las cargas positivas y HACIA las negativas.

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from config import (setup_matplotlib, ensure_dirs, FIGURES_DIR,
                    COLOR_POSITIVE, COLOR_NEGATIVE,
                    L_DOMAIN, K_COULOMB, EPSILON_SOFT,
                    GRID_RESOLUTION, CMAP_FIELD, DPI, FIGURE_SIZE)
from data_loader import load_final_configuration, get_positions_and_charges


def compute_electric_field(x_charges, y_charges, q_charges, resolution=50):
    """
    Calcula el campo eléctrico E(x,y) en una grilla 2D.
    
    E(r) = k Σ_i q_i (r - r_i) / |r - r_i|³
    
    Args:
        x_charges, y_charges: posiciones de las cargas
        q_charges: valores de las cargas
        resolution: puntos por eje (menor que heatmap para flechas legibles)
        
    Returns:
        X, Y: meshgrid
        Ex, Ey: componentes del campo eléctrico
    """
    x_grid = np.linspace(-L_DOMAIN * 0.95, L_DOMAIN * 0.95, resolution)
    y_grid = np.linspace(-L_DOMAIN * 0.95, L_DOMAIN * 0.95, resolution)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    Ex = np.zeros_like(X)
    Ey = np.zeros_like(Y)
    
    for i in range(len(x_charges)):
        dx = X - x_charges[i]
        dy = Y - y_charges[i]
        r = np.sqrt(dx**2 + dy**2 + EPSILON_SOFT**2)
        r3 = r**3
        
        Ex += K_COULOMB * q_charges[i] * dx / r3
        Ey += K_COULOMB * q_charges[i] * dy / r3
    
    return X, Y, Ex, Ey


def plot_quiver_field():
    """
    Genera quiver plot del campo eléctrico con flechas.
    """
    print("  Calculando campo eléctrico (quiver)...")
    
    df = load_final_configuration()
    x, y, q = get_positions_and_charges(df)
    
    # Resolución menor para quiver (flechas legibles)
    X, Y, Ex, Ey = compute_electric_field(x, y, q, resolution=25)
    
    # Magnitud del campo
    E_mag = np.sqrt(Ex**2 + Ey**2)
    
    # Normalizar flechas para visualización uniforme
    # (solo mostramos dirección, el color indica magnitud)
    E_mag_safe = np.maximum(E_mag, 1e-10)
    Ex_norm = Ex / E_mag_safe
    Ey_norm = Ey / E_mag_safe
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    
    # Quiver plot con color por magnitud
    quiv = ax.quiver(X, Y, Ex_norm, Ey_norm, E_mag,
                     cmap=CMAP_FIELD, scale=30, width=0.003,
                     norm=mcolors.LogNorm(vmin=E_mag[E_mag > 0].min(),
                                           vmax=np.percentile(E_mag, 95)),
                     alpha=0.85)
    
    cbar = plt.colorbar(quiv, ax=ax, label='|E| (magnitud)',
                        shrink=0.85, pad=0.02)
    cbar.ax.yaxis.label.set_color('#000000')
    cbar.ax.tick_params(colors='#000000')
    
    # Posiciones de cargas
    pos_mask = q > 0
    neg_mask = q < 0
    
    if np.any(pos_mask):
        ax.scatter(x[pos_mask], y[pos_mask], c=COLOR_POSITIVE, s=70,
                   edgecolors='black', linewidths=1.2, zorder=10,
                   marker='o', label='+1')
    if np.any(neg_mask):
        ax.scatter(x[neg_mask], y[neg_mask], c=COLOR_NEGATIVE, s=70,
                   edgecolors='black', linewidths=1.2, zorder=10,
                   marker='s', label='−1')
    
    ax.set_xlim(-L_DOMAIN, L_DOMAIN)
    ax.set_ylim(-L_DOMAIN, L_DOMAIN)
    ax.set_aspect('equal')
    ax.set_xlabel('x', fontsize=13)
    ax.set_ylabel('y', fontsize=13)
    ax.set_title('Campo Eléctrico — Vectores E(x,y)',
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
    filepath = FIGURES_DIR / 'electric_field_quiver.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Quiver plot guardado: {filepath}")


def plot_field_magnitude_heatmap():
    """
    Genera mapa de calor de la magnitud |E(x,y)| del campo eléctrico.
    """
    print("  Calculando magnitud del campo eléctrico...")
    
    df = load_final_configuration()
    x, y, q = get_positions_and_charges(df)
    
    X, Y, Ex, Ey = compute_electric_field(x, y, q, resolution=GRID_RESOLUTION)
    
    E_mag = np.sqrt(Ex**2 + Ey**2)
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    
    # Heatmap con escala logarítmica (el campo varía varios órdenes)
    e_percentile = np.percentile(E_mag, 98)
    E_clipped = np.clip(E_mag, E_mag[E_mag > 0].min(), e_percentile)
    
    im = ax.pcolormesh(X, Y, E_clipped, cmap=CMAP_FIELD,
                       norm=mcolors.LogNorm(vmin=E_clipped.min(),
                                             vmax=E_clipped.max()),
                       shading='auto')
    
    cbar = plt.colorbar(im, ax=ax, label='|E(x,y)| (log scale)',
                        shrink=0.85, pad=0.02)
    cbar.ax.yaxis.label.set_color('#000000')
    cbar.ax.tick_params(colors='#000000')
    
    # Posiciones de cargas
    pos_mask = q > 0
    neg_mask = q < 0
    
    if np.any(pos_mask):
        ax.scatter(x[pos_mask], y[pos_mask], c=COLOR_POSITIVE, s=40,
                   edgecolors='black', linewidths=0.8, zorder=10,
                   marker='o', label='+1')
    if np.any(neg_mask):
        ax.scatter(x[neg_mask], y[neg_mask], c=COLOR_NEGATIVE, s=40,
                   edgecolors='black', linewidths=0.8, zorder=10,
                   marker='s', label='−1')
    
    ax.set_xlim(-L_DOMAIN, L_DOMAIN)
    ax.set_ylim(-L_DOMAIN, L_DOMAIN)
    ax.set_aspect('equal')
    ax.set_xlabel('x', fontsize=13)
    ax.set_ylabel('y', fontsize=13)
    ax.set_title('Magnitud del Campo Eléctrico |E(x,y)|',
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
    filepath = FIGURES_DIR / 'electric_field_magnitude.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Heatmap de |E| guardado: {filepath}")


def generate_field_plots():
    """Pipeline principal de campo eléctrico."""
    print("\n  ")
    print("  GENERANDO VISUALIZACIÓN DEL CAMPO ELÉCTRICO")
    print("  \n")
    
    plot_quiver_field()
    plot_field_magnitude_heatmap()


if __name__ == '__main__':
    setup_matplotlib()
    ensure_dirs()
    generate_field_plots()
