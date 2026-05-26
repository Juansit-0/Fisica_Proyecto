"""
plot_heatmap.py — Mapas de calor del potencial eléctrico
========================================================

Genera mapas de calor de V(x, y) para la configuración final, calculando
el potencial eléctrico en una malla 2D y visualizándolo con un colormap
divergente (rojo para V>0, azul para V<0).

Física:
    V(r) = k Σ_i q_i / |r - r_i|

El potencial diverge cerca de las cargas puntuales, por lo que en la
visualización se usa:
  - Saturación por percentil (clipping) para acotar el rango de color.
  - Un epsilon visual (EPSILON_VIZ) que suaviza la divergencia.
  - Interpolación 'gouraud' en pcolormesh para evitar el efecto pixelado.

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator

from config import (setup_matplotlib, ensure_dirs, FIGURES_DIR,
                    COLOR_POSITIVE, COLOR_NEGATIVE,
                    L_DOMAIN, K_COULOMB, EPSILON_VIZ,
                    HEATMAP_RESOLUTION, CMAP_POTENTIAL,
                    DPI, FIGURE_SIZE)
from data_loader import load_final_configuration, get_positions_and_charges


def compute_potential_grid(x_charges, y_charges, q_charges,
                            resolution=HEATMAP_RESOLUTION,
                            epsilon=EPSILON_VIZ):
    """
    Calcula el potencial eléctrico V(x, y) en una malla 2D fina.

    V(r) = k Σ_i q_i / sqrt((x - x_i)² + (y - y_i)² + ε²)

    Vectorizado completamente con broadcasting:
        - X, Y tienen forma (resolution, resolution).
        - Las cargas se evalúan acumulando contribuciones uno a uno
          para mantener uso de memoria bajo.

    Args:
        x_charges, y_charges: arrays con las posiciones de las cargas.
        q_charges: valores de las cargas (típicamente ±1).
        resolution: puntos por eje en la malla del heatmap.
        epsilon: softening visual para acotar la divergencia 1/r.

    Returns:
        (X, Y, V): mallas 2D del dominio y los valores del potencial.
    """
    x_grid = np.linspace(-L_DOMAIN, L_DOMAIN, resolution)
    y_grid = np.linspace(-L_DOMAIN, L_DOMAIN, resolution)
    X, Y = np.meshgrid(x_grid, y_grid)

    V = np.zeros_like(X)
    for i in range(len(x_charges)):
        dx = X - x_charges[i]
        dy = Y - y_charges[i]
        r = np.sqrt(dx * dx + dy * dy + epsilon * epsilon)
        V += K_COULOMB * q_charges[i] / r

    return X, Y, V


def _build_potential_norm(V):
    """
    Construye una norma robusta para el colormap del potencial.

    - Si V tiene valores positivos y negativos: TwoSlopeNorm centrada en 0
      con un percentil para acotar saturación.
    - Si V es monosigno (p. ej. todas las cargas positivas): Normalize
      simple en el rango [vmin, vmax_percentil], sin forzar centrado.

    Retorna (norm, cmap_recomendado, v_abs_p) para uso en pcolormesh.
    """
    v_abs = np.abs(V)
    v_abs_nonzero = v_abs[v_abs > 0]
    if v_abs_nonzero.size == 0:
        # Sistema trivial sin cargas
        return mcolors.Normalize(vmin=-1.0, vmax=1.0), CMAP_POTENTIAL, 1.0

    v_p = float(np.percentile(v_abs_nonzero, 97))
    has_pos = bool(np.any(V > 0))
    has_neg = bool(np.any(V < 0))

    if has_pos and has_neg:
        norm = mcolors.TwoSlopeNorm(vmin=-v_p, vcenter=0.0, vmax=v_p)
        return norm, CMAP_POTENTIAL, v_p

    if has_pos and not has_neg:
        # V > 0 en todas partes (cargas positivas). Usar mitad cálida.
        v_min = float(np.percentile(V[V > 0], 3))
        norm = mcolors.Normalize(vmin=v_min, vmax=v_p)
        return norm, 'inferno', v_p

    # V < 0 en todas partes (cargas negativas)
    v_min = float(np.percentile(V[V < 0], 97))  # menos negativo
    norm = mcolors.Normalize(vmin=-v_p, vmax=v_min)
    return norm, 'inferno_r', v_p


def _style_axes(ax, l_dom, show_grid=True):
    """Aplica estilo común a los ejes de los mapas: ticks limpios y bordes."""
    ax.set_xlim(-l_dom, l_dom)
    ax.set_ylim(-l_dom, l_dom)
    ax.set_aspect('equal')
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)

    # Ticks razonables: ~9 valores por eje, no atados a la malla
    ax.xaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.tick_params(axis='both', labelsize=10)

    if show_grid:
        ax.grid(True, alpha=0.15, color='#888888', linewidth=0.4,
                linestyle='--')
    else:
        ax.grid(False)


def plot_potential_heatmap():
    """
    Genera mapa de calor del potencial eléctrico para la configuración final.

    Mejoras de calidad visual:
    - Malla fina (HEATMAP_RESOLUTION x HEATMAP_RESOLUTION).
    - Interpolación 'gouraud' para look orgánico.
    - Norma robusta para casos V monosigno.
    - Contornos equipotenciales superpuestos.
    """
    print("\n  ")
    print("  GENERANDO MAPA DE CALOR DEL POTENCIAL")
    print("  \n")

    df = load_final_configuration()
    x, y, q = get_positions_and_charges(df)

    print(f"  Resolución del heatmap: {HEATMAP_RESOLUTION}x{HEATMAP_RESOLUTION}")
    X, Y, V = compute_potential_grid(x, y, q,
                                       resolution=HEATMAP_RESOLUTION,
                                       epsilon=EPSILON_VIZ)

    norm, cmap_name, v_p = _build_potential_norm(V)
    V_clipped = np.clip(V, getattr(norm, 'vmin', V.min()),
                         getattr(norm, 'vmax', V.max()))

    print(f"  V_min = {V.min():.4f}, V_max = {V.max():.4f}")
    print(f"  Saturación al percentil 97: ±{v_p:.4f}")

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # 'gouraud' interpola triangularmente entre vértices => look suave/orgánico
    im = ax.pcolormesh(X, Y, V_clipped, cmap=cmap_name,
                        norm=norm, shading='gouraud')

    cbar = plt.colorbar(im, ax=ax, label='Potencial Eléctrico V(x, y)',
                         shrink=0.85, pad=0.02)
    cbar.ax.yaxis.label.set_color('#000000')
    cbar.ax.tick_params(colors='#000000', labelsize=10)

    # Contornos equipotenciales suaves para reforzar el detalle
    try:
        vmin_c = float(getattr(norm, 'vmin', V.min()))
        vmax_c = float(getattr(norm, 'vmax', V.max()))
        if isinstance(norm, mcolors.TwoSlopeNorm):
            levels = np.linspace(vmin_c, vmax_c, 17)
        else:
            levels = np.linspace(vmin_c, vmax_c, 11)
        ax.contour(X, Y, V_clipped, levels=levels, colors='#1D3557',
                    linewidths=0.5, alpha=0.35)
    except Exception:
        # Contornos son decorativos: si fallan no debe romper la figura
        pass

    # Posiciones de cargas
    pos_mask = q > 0
    neg_mask = q < 0
    if np.any(pos_mask):
        ax.scatter(x[pos_mask], y[pos_mask], c=COLOR_POSITIVE, s=55,
                    edgecolors='black', linewidths=1.0, zorder=10,
                    marker='o', label='+1')
    if np.any(neg_mask):
        ax.scatter(x[neg_mask], y[neg_mask], c=COLOR_NEGATIVE, s=55,
                    edgecolors='black', linewidths=1.0, zorder=10,
                    marker='s', label='−1')

    _style_axes(ax, L_DOMAIN, show_grid=True)
    ax.set_title('Mapa de Calor — Potencial Eléctrico V(x, y)',
                  fontsize=15, fontweight='bold', pad=12)

    if np.any(pos_mask) or np.any(neg_mask):
        ax.legend(loc='upper right', fontsize=9, framealpha=0.85,
                   facecolor='#FFFFFF', edgecolor='#333333')

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
