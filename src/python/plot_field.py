"""
plot_field.py — Visualización del campo eléctrico
==================================================

Genera dos tipos de visualización del campo eléctrico E(x, y):
    1. Quiver plot: flechas que indican dirección y magnitud relativa.
    2. Heatmap de |E(x, y)| con las posiciones de las cargas superpuestas.

Física:
    E(r) = k Σ_i q_i (r - r_i) / |r - r_i|³

El campo apunta DESDE las cargas positivas y HACIA las negativas. La
magnitud diverge cerca de las cargas, por lo que en la visualización se
usa un softening visual y saturación por percentil para mantener una
escala de color útil.

Mejoras de calidad visual:
    - Malla fina (HEATMAP_RESOLUTION x HEATMAP_RESOLUTION) para el heatmap.
    - QUIVER_RESOLUTION independiente para que las flechas sean legibles.
    - Interpolación 'gouraud' en pcolormesh => look orgánico, sin píxeles.
    - Norma logarítmica robusta para magnitudes que abarcan órdenes.
    - Ticks limpios con MaxNLocator (no atados a la malla).

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator

from config import (setup_matplotlib, ensure_dirs, FIGURES_DIR,
                    COLOR_POSITIVE, COLOR_NEGATIVE,
                    L_DOMAIN, K_COULOMB, EPSILON_VIZ,
                    HEATMAP_RESOLUTION, QUIVER_RESOLUTION,
                    CMAP_FIELD, DPI, FIGURE_SIZE)
from data_loader import load_final_configuration, get_positions_and_charges


def compute_electric_field(x_charges, y_charges, q_charges,
                            resolution=HEATMAP_RESOLUTION,
                            epsilon=EPSILON_VIZ,
                            margin_factor=1.0):
    """
    Calcula el campo eléctrico E(x, y) en una malla 2D.

    E(r) = k Σ_i q_i (r - r_i) / |r - r_i|³

    Args:
        x_charges, y_charges: posiciones de las cargas.
        q_charges: valores de las cargas.
        resolution: puntos por eje.
        epsilon: softening visual para acotar divergencias 1/r³.
        margin_factor: 1.0 = dominio completo, <1 reduce los bordes.

    Returns:
        (X, Y, Ex, Ey): mallas y componentes del campo.
    """
    extent = L_DOMAIN * margin_factor
    x_grid = np.linspace(-extent, extent, resolution)
    y_grid = np.linspace(-extent, extent, resolution)
    X, Y = np.meshgrid(x_grid, y_grid)

    Ex = np.zeros_like(X)
    Ey = np.zeros_like(Y)

    for i in range(len(x_charges)):
        dx = X - x_charges[i]
        dy = Y - y_charges[i]
        r2 = dx * dx + dy * dy + epsilon * epsilon
        r3 = r2 * np.sqrt(r2)
        coeff = K_COULOMB * q_charges[i] / r3
        Ex += coeff * dx
        Ey += coeff * dy

    return X, Y, Ex, Ey


def _style_axes(ax, l_dom, show_grid=True):
    """Aplica el mismo estilo de ejes que en plot_heatmap (consistencia)."""
    ax.set_xlim(-l_dom, l_dom)
    ax.set_ylim(-l_dom, l_dom)
    ax.set_aspect('equal')
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.tick_params(axis='both', labelsize=10)
    if show_grid:
        ax.grid(True, alpha=0.15, color='#888888', linewidth=0.4,
                linestyle='--')


def _safe_log_norm(values):
    """
    LogNorm robusta: filtra ceros y aplana valores por encima del p95
    para que un solo píxel cerca de una carga no domine la escala.
    """
    v = values[values > 0]
    if v.size == 0:
        return mcolors.Normalize(vmin=1e-6, vmax=1.0)
    vmin = float(np.percentile(v, 5))
    vmax = float(np.percentile(v, 95))
    if vmax <= vmin:
        vmax = vmin * 10.0
    return mcolors.LogNorm(vmin=max(vmin, 1e-6), vmax=vmax)


def plot_quiver_field():
    """
    Genera quiver plot del campo eléctrico con flechas dirección/magnitud.

    Las flechas se normalizan en longitud (solo dirección) y se colorean
    según la magnitud |E|, usando una escala logarítmica.
    """
    print("  Calculando campo eléctrico (quiver)...")

    df = load_final_configuration()
    x, y, q = get_positions_and_charges(df)

    # Quiver con resolución dedicada (flechas legibles)
    X, Y, Ex, Ey = compute_electric_field(x, y, q,
                                            resolution=QUIVER_RESOLUTION,
                                            epsilon=EPSILON_VIZ,
                                            margin_factor=0.96)
    E_mag = np.sqrt(Ex ** 2 + Ey ** 2)
    E_safe = np.maximum(E_mag, 1e-10)
    Ex_n = Ex / E_safe
    Ey_n = Ey / E_safe

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    quiv = ax.quiver(X, Y, Ex_n, Ey_n, E_mag,
                      cmap=CMAP_FIELD, scale=32, width=0.0035, alpha=0.9,
                      norm=_safe_log_norm(E_mag))

    cbar = plt.colorbar(quiv, ax=ax, label='|E| (magnitud, escala log)',
                         shrink=0.85, pad=0.02)
    cbar.ax.yaxis.label.set_color('#000000')
    cbar.ax.tick_params(colors='#000000', labelsize=10)

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

    _style_axes(ax, L_DOMAIN, show_grid=True)
    ax.set_title('Campo Eléctrico — Vectores E(x, y)',
                  fontsize=15, fontweight='bold', pad=12)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.85,
               facecolor='#FFFFFF', edgecolor='#333333')

    plt.tight_layout()
    filepath = FIGURES_DIR / 'electric_field_quiver.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                 facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Quiver plot guardado: {filepath}")


def plot_field_magnitude_heatmap():
    """
    Genera mapa de calor de |E(x, y)| con malla fina e interpolación
    'gouraud' para evitar el efecto pixelado.
    """
    print("  Calculando magnitud del campo eléctrico...")

    df = load_final_configuration()
    x, y, q = get_positions_and_charges(df)

    print(f"  Resolución del heatmap: {HEATMAP_RESOLUTION}x{HEATMAP_RESOLUTION}")
    X, Y, Ex, Ey = compute_electric_field(x, y, q,
                                            resolution=HEATMAP_RESOLUTION,
                                            epsilon=EPSILON_VIZ)
    E_mag = np.sqrt(Ex ** 2 + Ey ** 2)
    norm = _safe_log_norm(E_mag)

    # Recortar valores fuera de la norma para que pcolormesh no se queje
    E_clipped = np.clip(E_mag, norm.vmin, norm.vmax)

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    im = ax.pcolormesh(X, Y, E_clipped, cmap=CMAP_FIELD,
                        norm=norm, shading='gouraud')

    cbar = plt.colorbar(im, ax=ax, label='|E(x, y)|  (escala log)',
                         shrink=0.85, pad=0.02)
    cbar.ax.yaxis.label.set_color('#000000')
    cbar.ax.tick_params(colors='#000000', labelsize=10)

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

    _style_axes(ax, L_DOMAIN, show_grid=True)
    ax.set_title('Magnitud del Campo Eléctrico |E(x, y)|',
                  fontsize=15, fontweight='bold', pad=12)
    if np.any(pos_mask) or np.any(neg_mask):
        ax.legend(loc='upper right', fontsize=9, framealpha=0.85,
                   facecolor='#FFFFFF', edgecolor='#333333')

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
