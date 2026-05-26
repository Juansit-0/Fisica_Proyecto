"""
phet_sandbox.py — Laboratorio Interactivo Tipo PhET "Charges and Fields"
=========================================================================
Módulo interactivo inspirado en la simulación PhET "Charges and Fields"
(https://phet.colorado.edu/en/simulations/charges-and-fields).

Permite al usuario colocar cargas puntuales +1 y -1 en un dominio 2D,
visualizar en tiempo real:
- Mapa de potencial eléctrico V(x, y).
- Vectores del campo eléctrico E(x, y).
- Líneas equipotenciales.
- Sensores puntuales de V y E.
- Distancia entre dos puntos.

Diseño:
- Estado persistente en st.session_state.
- Render con matplotlib (mismo estilo del resto del proyecto).
- Reutiliza constantes físicas y colores de config.py.

Física implementada (idénticas al núcleo Fortran):
    V(r) = k * Σ_i q_i / |r - r_i|
    E(r) = k * Σ_i q_i * (r - r_i) / |r - r_i|³

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator

from config import (
    COLOR_POSITIVE, COLOR_NEGATIVE, MARKER_EDGE_COLOR,
    L_DOMAIN, K_COULOMB, EPSILON_SOFT, EPSILON_VIZ,
    CMAP_POTENTIAL, CMAP_FIELD,
    DPI, FIGURE_SIZE_SQUARE,
    MATPLOTLIB_STYLE,
)


#===============================================================================
# FÍSICA: cálculos vectorizados de V y E
#===============================================================================

def compute_V_at_points(charges_df: pd.DataFrame,
                         xp: np.ndarray, yp: np.ndarray,
                         epsilon: float = EPSILON_SOFT) -> np.ndarray:
    """
    Potencial eléctrico V en arreglos arbitrarios de puntos.

    V(r) = k * Σ_i q_i / sqrt((x - x_i)² + (y - y_i)² + ε²)

    El parámetro epsilon controla el softening:
        - EPSILON_SOFT (default): fiel a la simulación física, para
          sensores numéricos y métricas como U.
        - EPSILON_VIZ: epsilon mayor, solo para heatmaps, evita spikes
          de un píxel cerca de las cargas que distorsionan la escala.
    """
    V = np.zeros_like(xp, dtype=float)
    if len(charges_df) == 0:
        return V
    for _, row in charges_df.iterrows():
        dx = xp - float(row['x'])
        dy = yp - float(row['y'])
        r = np.sqrt(dx * dx + dy * dy + epsilon * epsilon)
        V += K_COULOMB * float(row['q']) / r
    return V


def compute_E_at_points(charges_df: pd.DataFrame,
                         xp: np.ndarray, yp: np.ndarray,
                         epsilon: float = EPSILON_SOFT):
    """
    Campo eléctrico E en arreglos de puntos. Devuelve (Ex, Ey).

    E(r) = k * Σ_i q_i * (r - r_i) / |r - r_i|³

    epsilon: ver docstring de compute_V_at_points.
    """
    Ex = np.zeros_like(xp, dtype=float)
    Ey = np.zeros_like(yp, dtype=float)
    if len(charges_df) == 0:
        return Ex, Ey
    for _, row in charges_df.iterrows():
        dx = xp - float(row['x'])
        dy = yp - float(row['y'])
        r2 = dx * dx + dy * dy + epsilon * epsilon
        r3 = r2 * np.sqrt(r2)
        coeff = K_COULOMB * float(row['q']) / r3
        Ex += coeff * dx
        Ey += coeff * dy
    return Ex, Ey


def compute_grid(charges_df: pd.DataFrame, l_dom: float, resolution: int,
                  epsilon: float = EPSILON_VIZ):
    """Construye malla 2D y evalúa V, Ex, Ey en cada nodo.

    Por defecto usa EPSILON_VIZ porque esta función alimenta los
    heatmaps. Para precisión física exacta, pasar epsilon=EPSILON_SOFT.
    """
    x_grid = np.linspace(-l_dom, l_dom, resolution)
    y_grid = np.linspace(-l_dom, l_dom, resolution)
    X, Y = np.meshgrid(x_grid, y_grid)
    V = compute_V_at_points(charges_df, X, Y, epsilon=epsilon)
    Ex, Ey = compute_E_at_points(charges_df, X, Y, epsilon=epsilon)
    return X, Y, V, Ex, Ey


def _build_phet_norm(V):
    """Norma robusta para V: TwoSlopeNorm si hay signos mixtos, si no
    Normalize lineal. Evita el crash con vcenter fuera de [vmin, vmax].
    Devuelve (norm, cmap_name)."""
    v_abs = np.abs(V)
    v_nz = v_abs[v_abs > 0]
    if v_nz.size == 0:
        return mcolors.Normalize(vmin=-1.0, vmax=1.0), CMAP_POTENTIAL

    v_p = float(np.percentile(v_nz, 95))
    has_pos = bool(np.any(V > 0))
    has_neg = bool(np.any(V < 0))

    if has_pos and has_neg:
        return (mcolors.TwoSlopeNorm(vmin=-v_p, vcenter=0.0, vmax=v_p),
                CMAP_POTENTIAL)
    if has_pos:
        v_lo = float(np.percentile(V[V > 0], 5))
        return mcolors.Normalize(vmin=v_lo, vmax=v_p), 'inferno'
    v_hi = float(np.percentile(V[V < 0], 95))
    return mcolors.Normalize(vmin=-v_p, vmax=v_hi), 'inferno_r'


#===============================================================================
# RENDER: figura matplotlib integrando todas las capas opcionales
#===============================================================================

#===============================================================================
# RENDER: curvas de nivel del potencial (vistas 2D y 3D)
#===============================================================================

def render_potential_contours_2d(charges_df: pd.DataFrame,
                                   l_dom: float,
                                   resolution: int = 250,
                                   n_levels: int = 20,
                                   show_labels: bool = True,
                                   filled: bool = True):
    """
    Vista 2D de las curvas equipotenciales V(x, y).

    Estilo equivalente al usado en libros y slides de física básica:
        - `contourf` opcional con cmap divergente (RdBu_r) para
          visualizar el signo del potencial.
        - `contour` superpuesto con líneas negras y etiquetas numéricas,
          formando las curvas de nivel propiamente dichas.
        - Cargas marcadas con su color convencional (+ rojo, − azul).

    Devuelve una figura de matplotlib.
    """
    plt.rcParams.update(MATPLOTLIB_STYLE)
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SQUARE)

    if len(charges_df) == 0:
        ax.set_xlim(-l_dom, l_dom)
        ax.set_ylim(-l_dom, l_dom)
        ax.set_aspect('equal')
        ax.text(0.5, 0.5, 'Añade al menos una carga para ver V(x, y)',
                 ha='center', va='center', transform=ax.transAxes,
                 fontsize=11, color='#555555', style='italic')
        return fig

    X, Y, V, _, _ = compute_grid(charges_df, l_dom, resolution,
                                    epsilon=EPSILON_VIZ)
    norm, cmap_name = _build_phet_norm(V)
    vmin = float(getattr(norm, 'vmin', V.min()))
    vmax = float(getattr(norm, 'vmax', V.max()))
    V_clipped = np.clip(V, vmin, vmax)
    levels = np.linspace(vmin, vmax, n_levels)

    if filled:
        cf = ax.contourf(X, Y, V_clipped, levels=levels, cmap=cmap_name,
                          norm=norm, alpha=0.85, extend='both')
        cbar = plt.colorbar(cf, ax=ax, label='Potencial V(x, y)',
                             shrink=0.85, pad=0.02)
        cbar.ax.yaxis.label.set_color('#000000')
        cbar.ax.tick_params(colors='#000000', labelsize=9)

    cs = ax.contour(X, Y, V_clipped, levels=levels,
                     colors='#111111', linewidths=0.8, alpha=0.75)
    if show_labels:
        ax.clabel(cs, inline=True, fontsize=7, fmt='%.2f')

    # Cargas
    pos = charges_df[charges_df['q'] > 0]
    neg = charges_df[charges_df['q'] < 0]
    if len(pos) > 0:
        ax.scatter(pos['x'], pos['y'], c=COLOR_POSITIVE, s=180,
                    edgecolors=MARKER_EDGE_COLOR, linewidths=1.5,
                    zorder=10, marker='o', label=f'+1 ({len(pos)})')
    if len(neg) > 0:
        ax.scatter(neg['x'], neg['y'], c=COLOR_NEGATIVE, s=180,
                    edgecolors=MARKER_EDGE_COLOR, linewidths=1.5,
                    zorder=10, marker='s', label=f'−1 ({len(neg)})')

    rect = plt.Rectangle((-l_dom, -l_dom), 2 * l_dom, 2 * l_dom,
                          fill=False, edgecolor='#58A6FF',
                          linewidth=1.5, linestyle='--', alpha=0.6)
    ax.add_patch(rect)
    margin = l_dom * 0.05
    ax.set_xlim(-l_dom - margin, l_dom + margin)
    ax.set_ylim(-l_dom - margin, l_dom + margin)
    ax.set_aspect('equal')
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.tick_params(axis='both', labelsize=9)
    ax.set_title('Curvas Equipotenciales V(x, y) — vista 2D',
                  fontsize=13, fontweight='bold', pad=10)
    ax.grid(True, alpha=0.2, color='#888888', linewidth=0.4, linestyle='--')
    if len(pos) + len(neg) > 0:
        ax.legend(loc='upper right', fontsize=9, framealpha=0.85,
                   facecolor='#FFFFFF', edgecolor='#333333')

    plt.tight_layout()
    return fig


def render_potential_surface_3d(charges_df: pd.DataFrame,
                                  l_dom: float,
                                  resolution: int = 90,
                                  n_levels: int = 18,
                                  show_projection: bool = True):
    """
    Vista 3D interactiva del potencial como superficie z = V(x, y).

    Implementado con Plotly para permitir rotación, zoom y hover con el
    ratón dentro de Streamlit. Sobre la superficie se proyectan las
    curvas de nivel en el plano inferior (estilo libro de física).

    Devuelve una `plotly.graph_objects.Figure`.
    """
    import plotly.graph_objects as go

    if len(charges_df) == 0:
        fig = go.Figure()
        fig.add_annotation(text="Añade al menos una carga para ver V(x, y)",
                             showarrow=False, x=0.5, y=0.5,
                             xref='paper', yref='paper',
                             font=dict(size=14, color='#555555'))
        return fig

    X, Y, V, _, _ = compute_grid(charges_df, l_dom, resolution,
                                    epsilon=EPSILON_VIZ)
    # Recortar para que un par de spikes cerca de las cargas no aplaste
    # la superficie. Saturación al percentil 97 simétrica.
    v_abs = np.abs(V)
    v_p = float(np.percentile(v_abs[v_abs > 0], 97)) if np.any(v_abs > 0) else 1.0
    has_pos = bool(np.any(V > 0))
    has_neg = bool(np.any(V < 0))
    if has_pos and has_neg:
        z_clip = np.clip(V, -v_p, v_p)
        cmid = 0.0
        cmin, cmax = -v_p, v_p
        colorscale = 'RdBu_r'
    elif has_pos:
        z_clip = np.clip(V, 0, v_p)
        cmid = None
        cmin, cmax = 0.0, v_p
        colorscale = 'Inferno'
    else:
        z_clip = np.clip(V, -v_p, 0)
        cmid = None
        cmin, cmax = -v_p, 0.0
        colorscale = 'Inferno_r'

    surface_kwargs = dict(
        x=X, y=Y, z=z_clip,
        colorscale=colorscale, cmin=cmin, cmax=cmax,
        colorbar=dict(title='V(x, y)', thickness=15, len=0.75),
        showscale=True, opacity=0.97,
        lighting=dict(ambient=0.55, diffuse=0.7, specular=0.2,
                       roughness=0.85, fresnel=0.1),
    )
    if cmid is not None:
        surface_kwargs['cmid'] = cmid

    surface = go.Surface(**surface_kwargs)

    data = [surface]

    # Proyección de las curvas de nivel en el "piso" del cubo 3D
    if show_projection:
        z_floor = cmin - 0.05 * (cmax - cmin)
        proj = go.Surface(
            x=X, y=Y, z=np.full_like(z_clip, z_floor),
            surfacecolor=z_clip,
            colorscale=colorscale, cmin=cmin, cmax=cmax,
            showscale=False, opacity=0.85,
            contours=dict(
                z=dict(show=True, start=cmin, end=cmax,
                        size=(cmax - cmin) / max(n_levels, 1),
                        color='#111111', width=2),
            ),
        )
        data.append(proj)

    # Marcadores 3D de las cargas en su altura física V(carga)
    pos = charges_df[charges_df['q'] > 0]
    neg = charges_df[charges_df['q'] < 0]
    if len(pos) > 0:
        zp = compute_V_at_points(charges_df,
                                  pos['x'].astype(float).values,
                                  pos['y'].astype(float).values,
                                  epsilon=EPSILON_VIZ * 2.0)
        zp = np.clip(zp, cmin, cmax)
        data.append(go.Scatter3d(
            x=pos['x'], y=pos['y'], z=zp,
            mode='markers', name=f'+1 ({len(pos)})',
            marker=dict(color=COLOR_POSITIVE, size=6,
                         line=dict(color='black', width=1)),
        ))
    if len(neg) > 0:
        zn = compute_V_at_points(charges_df,
                                  neg['x'].astype(float).values,
                                  neg['y'].astype(float).values,
                                  epsilon=EPSILON_VIZ * 2.0)
        zn = np.clip(zn, cmin, cmax)
        data.append(go.Scatter3d(
            x=neg['x'], y=neg['y'], z=zn,
            mode='markers', name=f'−1 ({len(neg)})',
            marker=dict(color=COLOR_NEGATIVE, size=6, symbol='square',
                         line=dict(color='black', width=1)),
        ))

    fig = go.Figure(data=data)
    fig.update_layout(
        title=dict(text='Superficie del Potencial V(x, y) — vista 3D',
                     x=0.5, font=dict(size=14)),
        scene=dict(
            xaxis_title='x',
            yaxis_title='y',
            zaxis_title='V(x, y)',
            aspectratio=dict(x=1, y=1, z=0.7),
            camera=dict(eye=dict(x=1.4, y=-1.6, z=1.1)),
            xaxis=dict(range=[-l_dom, l_dom]),
            yaxis=dict(range=[-l_dom, l_dom]),
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=620,
        legend=dict(orientation='h', y=-0.05),
    )
    return fig


def render_sandbox(charges_df: pd.DataFrame,
                    sensors_v_df: pd.DataFrame,
                    sensors_e_df: pd.DataFrame,
                    options: dict,
                    l_dom: float):
    """
    Construye una figura matplotlib con todas las capas habilitadas.

    options claves:
        show_potential (bool)
        show_field_arrows (bool)
        show_equipotentials (bool)
        show_grid (bool)
        show_values (bool)
        grid_resolution (int)
        arrow_resolution (int)
        equipotential_levels (int)
    """
    plt.rcParams.update(MATPLOTLIB_STYLE)

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SQUARE)

    # Cachear la malla y V para no recalcular entre capas 1 y 2
    grid_cache = None
    if (options.get('show_potential', False) or
        options.get('show_equipotentials', False)) and len(charges_df) > 0:
        grid_cache = compute_grid(charges_df, l_dom,
                                   options['grid_resolution'],
                                   epsilon=EPSILON_VIZ)

    # ---------------- Capa 1: mapa de potencial -----------------
    if options.get('show_potential', False) and grid_cache is not None:
        X, Y, V, _, _ = grid_cache
        norm, cmap_name = _build_phet_norm(V)
        vmin = float(getattr(norm, 'vmin', V.min()))
        vmax = float(getattr(norm, 'vmax', V.max()))
        V_clipped = np.clip(V, vmin, vmax)
        # 'gouraud' interpola triangularmente => look orgánico/suave
        im = ax.pcolormesh(X, Y, V_clipped, cmap=cmap_name,
                            norm=norm, shading='gouraud', alpha=0.9)
        cbar = plt.colorbar(im, ax=ax, label='Potencial V(x, y)',
                             shrink=0.8, pad=0.02)
        cbar.ax.yaxis.label.set_color('#000000')
        cbar.ax.tick_params(colors='#000000', labelsize=9)

    # ---------------- Capa 2: equipotenciales -------------------
    if options.get('show_equipotentials', False) and grid_cache is not None:
        X, Y, V, _, _ = grid_cache
        v_abs = np.abs(V)
        v_max = np.percentile(v_abs[v_abs > 0], 90) if np.any(v_abs > 0) else 1.0
        has_pos = bool(np.any(V > 0))
        has_neg = bool(np.any(V < 0))
        if has_pos and has_neg:
            levels = np.linspace(-v_max, v_max, options['equipotential_levels'])
        else:
            # V monosigno: niveles solo en el rango efectivo
            v_lo = float(np.percentile(v_abs[v_abs > 0], 10)) if v_abs.any() else 0.0
            sign = 1.0 if has_pos else -1.0
            levels = sign * np.linspace(v_lo, v_max,
                                          options['equipotential_levels'])
        cs = ax.contour(X, Y, V, levels=levels, colors='#1D3557',
                         linewidths=0.8, alpha=0.6)
        if options.get('show_values', False):
            ax.clabel(cs, inline=True, fontsize=7, fmt='%.2f')

    # ---------------- Capa 3: vectores E ------------------------
    if options.get('show_field_arrows', False) and len(charges_df) > 0:
        Xa = np.linspace(-l_dom, l_dom, options['arrow_resolution'])
        Ya = np.linspace(-l_dom, l_dom, options['arrow_resolution'])
        Xa, Ya = np.meshgrid(Xa, Ya)
        # Para flechas usamos EPSILON_VIZ también (las flechas viven
        # cerca de las cargas y de otro modo unas pocas dominarían la
        # escala de color)
        Ex, Ey = compute_E_at_points(charges_df, Xa, Ya,
                                       epsilon=EPSILON_VIZ)
        E_mag = np.sqrt(Ex ** 2 + Ey ** 2)
        E_safe = np.maximum(E_mag, 1e-10)
        Ex_n = Ex / E_safe
        Ey_n = Ey / E_safe
        E_nz = E_mag[E_mag > 0]
        if E_nz.size > 0:
            vmin_q = float(np.percentile(E_nz, 5))
            vmax_q = float(np.percentile(E_nz, 95))
            if vmax_q <= vmin_q:
                vmax_q = vmin_q * 10.0
            qnorm = mcolors.LogNorm(vmin=max(vmin_q, 1e-6), vmax=vmax_q)
        else:
            qnorm = mcolors.Normalize(vmin=0, vmax=1)
        ax.quiver(Xa, Ya, Ex_n, Ey_n, E_mag,
                   cmap=CMAP_FIELD, scale=32, width=0.0035, alpha=0.9,
                   norm=qnorm)

    # ---------------- Capa 4: cargas ----------------------------
    if len(charges_df) > 0:
        pos = charges_df[charges_df['q'] > 0]
        neg = charges_df[charges_df['q'] < 0]
        if len(pos) > 0:
            ax.scatter(pos['x'], pos['y'], c=COLOR_POSITIVE, s=180,
                        edgecolors=MARKER_EDGE_COLOR, linewidths=1.5,
                        zorder=10, marker='o', label=f'+1 ({len(pos)})')
        if len(neg) > 0:
            ax.scatter(neg['x'], neg['y'], c=COLOR_NEGATIVE, s=180,
                        edgecolors=MARKER_EDGE_COLOR, linewidths=1.5,
                        zorder=10, marker='s', label=f'−1 ({len(neg)})')

    # ---------------- Capa 5: sensores V ------------------------
    if len(sensors_v_df) > 0:
        for _, row in sensors_v_df.iterrows():
            xs, ys = float(row['x']), float(row['y'])
            V_val = compute_V_at_points(charges_df,
                                         np.array([xs]), np.array([ys]))[0]
            ax.scatter([xs], [ys], c='#FFD700', s=120, marker='*',
                        edgecolors='black', linewidths=1.2, zorder=11)
            if options.get('show_values', True):
                ax.annotate(f'V = {V_val:.2f}', (xs, ys),
                             xytext=(8, 8), textcoords='offset points',
                             fontsize=9, color='#000000', fontweight='bold',
                             bbox=dict(boxstyle='round,pad=0.25',
                                       facecolor='#FFFFFF',
                                       edgecolor='#333333', alpha=0.85))

    # ---------------- Capa 6: sensores E ------------------------
    if len(sensors_e_df) > 0:
        xs_arr = sensors_e_df['x'].astype(float).values
        ys_arr = sensors_e_df['y'].astype(float).values
        Ex_s, Ey_s = compute_E_at_points(charges_df, xs_arr, ys_arr)
        E_mag_s = np.sqrt(Ex_s ** 2 + Ey_s ** 2)
        max_mag = E_mag_s.max() if E_mag_s.max() > 0 else 1.0
        arrow_scale = l_dom * 0.15 / max_mag
        for xs, ys, ex, ey, em in zip(xs_arr, ys_arr, Ex_s, Ey_s, E_mag_s):
            ax.scatter([xs], [ys], c='#22D3EE', s=80, marker='D',
                        edgecolors='black', linewidths=1.0, zorder=11)
            ax.annotate('', xy=(xs + ex * arrow_scale, ys + ey * arrow_scale),
                         xytext=(xs, ys),
                         arrowprops=dict(arrowstyle='->', color='#22D3EE',
                                          lw=2.0, alpha=0.9))
            if options.get('show_values', True):
                ax.annotate(f'|E| = {em:.2f}', (xs, ys),
                             xytext=(8, -14), textcoords='offset points',
                             fontsize=9, color='#000000', fontweight='bold',
                             bbox=dict(boxstyle='round,pad=0.25',
                                       facecolor='#FFFFFF',
                                       edgecolor='#22D3EE', alpha=0.85))

    # ---------------- Bordes del dominio ------------------------
    rect = plt.Rectangle((-l_dom, -l_dom), 2 * l_dom, 2 * l_dom,
                          fill=False, edgecolor='#58A6FF',
                          linewidth=1.5, linestyle='--', alpha=0.6)
    ax.add_patch(rect)

    margin = l_dom * 0.05
    ax.set_xlim(-l_dom - margin, l_dom + margin)
    ax.set_ylim(-l_dom - margin, l_dom + margin)
    ax.set_aspect('equal')
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.tick_params(axis='both', labelsize=9)
    ax.set_title('Laboratorio Interactivo — Cargas y Campos',
                  fontsize=14, fontweight='bold', pad=10)

    if options.get('show_grid', True):
        ax.grid(True, alpha=0.2, color='#888888', linewidth=0.4,
                 linestyle='--')
    else:
        ax.grid(False)

    if len(charges_df) > 0:
        ax.legend(loc='upper right', fontsize=9, framealpha=0.85,
                   facecolor='#FFFFFF', edgecolor='#333333')

    plt.tight_layout()
    return fig


#===============================================================================
# CONFIGURACIONES PREDEFINIDAS (botones de demostración rápida)
#===============================================================================

def preset_charges(name: str) -> pd.DataFrame:
    """Devuelve un DataFrame de cargas para configuraciones clásicas."""
    presets = {
        'Vacío': [],
        'Monopolo +': [(0.0, 0.0, 1.0)],
        'Monopolo −': [(0.0, 0.0, -1.0)],
        'Dipolo': [(-2.0, 0.0, 1.0), (2.0, 0.0, -1.0)],
        'Cuadrupolo': [(-2.0, 2.0, 1.0), (2.0, 2.0, -1.0),
                        (-2.0, -2.0, -1.0), (2.0, -2.0, 1.0)],
        'Línea de cargas +': [(x, 0.0, 1.0) for x in
                                np.linspace(-5.0, 5.0, 5)],
        'Plano +/−': ([(x, 3.0, 1.0) for x in np.linspace(-5.0, 5.0, 5)]
                       + [(x, -3.0, -1.0) for x in np.linspace(-5.0, 5.0, 5)]),
    }
    rows = presets.get(name, [])
    return pd.DataFrame(rows, columns=['x', 'y', 'q'])


#===============================================================================
# INICIALIZACIÓN DEL ESTADO
#===============================================================================

def _init_state():
    if 'phet_charges' not in st.session_state:
        st.session_state.phet_charges = preset_charges('Dipolo')
    if 'phet_sensors_v' not in st.session_state:
        st.session_state.phet_sensors_v = pd.DataFrame(
            [[3.0, 3.0]], columns=['x', 'y'])
    if 'phet_sensors_e' not in st.session_state:
        st.session_state.phet_sensors_e = pd.DataFrame(
            [[-3.0, 3.0]], columns=['x', 'y'])


#===============================================================================
# COMPONENTE PRINCIPAL DE LA TAB
#===============================================================================

def run_sandbox_tab():
    """
    Renderiza la tab completa del laboratorio interactivo dentro de la GUI
    Streamlit. Diseñado para ser llamado desde gui_app.py dentro de un
    bloque `with tabN:`.
    """
    _init_state()

    st.header("Laboratorio Interactivo — Cargas y Campos")
    st.caption(
        "Inspirado en PhET 'Charges and Fields'. "
        "Coloca cargas, sensores de potencial V y sensores de campo E, "
        "y observa el comportamiento del sistema en tiempo real."
    )

    # ===== Parámetros generales =====
    with st.expander("Parámetros del Dominio y la Visualización",
                       expanded=False):
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            l_dom = st.slider("Tamaño del dominio L",
                                min_value=2.0, max_value=20.0,
                                value=float(L_DOMAIN), step=0.5,
                                key='phet_l_dom')
        with col_p2:
            grid_res = st.slider("Resolución del mapa V",
                                   min_value=80, max_value=500,
                                   value=300, step=20,
                                   key='phet_grid_res',
                                   help=("Mayor = imagen más suave y "
                                         "orgánica, pero render más lento"))
        with col_p3:
            arrow_res = st.slider("Densidad de flechas E",
                                    min_value=10, max_value=50,
                                    value=24, step=2,
                                    key='phet_arrow_res')

    # ===== Capas visuales =====
    st.subheader("Capas Visuales")
    col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
    with col_c1:
        show_pot = st.checkbox("Mapa V(x, y)", value=True, key='phet_pot')
    with col_c2:
        show_arr = st.checkbox("Vectores E", value=False, key='phet_arr')
    with col_c3:
        show_eq = st.checkbox("Equipotenciales", value=False, key='phet_eq')
    with col_c4:
        show_vals = st.checkbox("Mostrar valores", value=True, key='phet_vals')
    with col_c5:
        show_grid = st.checkbox("Cuadrícula", value=True, key='phet_grid')

    eq_levels = 12
    if show_eq:
        eq_levels = st.slider("Nº de líneas equipotenciales",
                                min_value=4, max_value=30, value=12, step=2,
                                key='phet_eq_levels')

    st.markdown("---")

    # ===== Layout principal: columna controles | columna figura =====
    col_ctrl, col_plot = st.columns([1, 2])

    with col_ctrl:
        st.subheader("Configuración Rápida")
        preset_names = ['Vacío', 'Monopolo +', 'Monopolo −', 'Dipolo',
                         'Cuadrupolo', 'Línea de cargas +', 'Plano +/−']
        col_pa, col_pb = st.columns([2, 1])
        with col_pa:
            preset_sel = st.selectbox("Cargar configuración:",
                                        preset_names, index=3,
                                        key='phet_preset_sel')
        with col_pb:
            st.write("")
            st.write("")
            if st.button("Cargar", key='phet_load_preset'):
                st.session_state.phet_charges = preset_charges(preset_sel)
                st.rerun()

        st.markdown("---")
        st.subheader("Cargas")
        st.caption("Edita la tabla. Añade filas con + y borra con la papelera.")
        edited = st.data_editor(
            st.session_state.phet_charges,
            num_rows='dynamic',
            use_container_width=True,
            column_config={
                'x': st.column_config.NumberColumn(
                    'x', min_value=-l_dom, max_value=l_dom,
                    step=0.1, format="%.2f"),
                'y': st.column_config.NumberColumn(
                    'y', min_value=-l_dom, max_value=l_dom,
                    step=0.1, format="%.2f"),
                'q': st.column_config.NumberColumn(
                    'q', min_value=-1.0, max_value=1.0,
                    step=1.0, format="%.0f",
                    help="Usa +1 ó −1"),
            },
            key='phet_charges_editor',
        )
        st.session_state.phet_charges = edited

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("Limpiar todo", key='phet_clear'):
                st.session_state.phet_charges = preset_charges('Vacío')
                st.rerun()
        with col_b2:
            if st.button("Añadir carga aleatoria", key='phet_add_random'):
                rx = float(np.random.uniform(-l_dom + 1, l_dom - 1))
                ry = float(np.random.uniform(-l_dom + 1, l_dom - 1))
                rq = float(np.random.choice([-1.0, 1.0]))
                new = pd.DataFrame([[rx, ry, rq]], columns=['x', 'y', 'q'])
                st.session_state.phet_charges = pd.concat(
                    [st.session_state.phet_charges, new],
                    ignore_index=True)
                st.rerun()

        st.markdown("---")
        st.subheader("Sensores de Potencial V")
        sv = st.data_editor(
            st.session_state.phet_sensors_v,
            num_rows='dynamic',
            use_container_width=True,
            column_config={
                'x': st.column_config.NumberColumn(
                    'x', min_value=-l_dom, max_value=l_dom,
                    step=0.1, format="%.2f"),
                'y': st.column_config.NumberColumn(
                    'y', min_value=-l_dom, max_value=l_dom,
                    step=0.1, format="%.2f"),
            },
            key='phet_sv_editor',
        )
        st.session_state.phet_sensors_v = sv

        st.subheader("Sensores de Campo E")
        se = st.data_editor(
            st.session_state.phet_sensors_e,
            num_rows='dynamic',
            use_container_width=True,
            column_config={
                'x': st.column_config.NumberColumn(
                    'x', min_value=-l_dom, max_value=l_dom,
                    step=0.1, format="%.2f"),
                'y': st.column_config.NumberColumn(
                    'y', min_value=-l_dom, max_value=l_dom,
                    step=0.1, format="%.2f"),
            },
            key='phet_se_editor',
        )
        st.session_state.phet_sensors_e = se

    # ===== Figura =====
    with col_plot:
        # Validar cargas (saturar a [-1, +1])
        charges_df = st.session_state.phet_charges.copy()
        if len(charges_df) > 0:
            charges_df = charges_df.dropna(subset=['x', 'y', 'q'])
            charges_df['q'] = charges_df['q'].apply(
                lambda v: 1.0 if v > 0 else (-1.0 if v < 0 else 0.0))
            charges_df = charges_df[charges_df['q'] != 0.0]

        sv_df = st.session_state.phet_sensors_v.dropna(subset=['x', 'y'])
        se_df = st.session_state.phet_sensors_e.dropna(subset=['x', 'y'])

        options = {
            'show_potential': show_pot,
            'show_field_arrows': show_arr,
            'show_equipotentials': show_eq,
            'show_grid': show_grid,
            'show_values': show_vals,
            'grid_resolution': int(grid_res),
            'arrow_resolution': int(arrow_res),
            'equipotential_levels': int(eq_levels),
        }

        fig = render_sandbox(charges_df, sv_df, se_df, options, l_dom)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        # ===== Métricas en vivo =====
        st.markdown("### Lecturas de los Sensores")
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.markdown("**Sensores V**")
            if len(sv_df) > 0 and len(charges_df) > 0:
                xs = sv_df['x'].astype(float).values
                ys = sv_df['y'].astype(float).values
                Vs = compute_V_at_points(charges_df, xs, ys)
                df_out = pd.DataFrame({
                    'x': xs, 'y': ys,
                    'V(x, y)': [f"{v:.4f}" for v in Vs],
                })
                st.dataframe(df_out, use_container_width=True, hide_index=True)
            else:
                st.info("Sin sensores V o sin cargas.")

        with col_m2:
            st.markdown("**Sensores E**")
            if len(se_df) > 0 and len(charges_df) > 0:
                xs = se_df['x'].astype(float).values
                ys = se_df['y'].astype(float).values
                Ex, Ey = compute_E_at_points(charges_df, xs, ys)
                E_mag = np.sqrt(Ex ** 2 + Ey ** 2)
                angle = np.degrees(np.arctan2(Ey, Ex))
                df_out = pd.DataFrame({
                    'x': xs, 'y': ys,
                    '|E|': [f"{m:.4f}" for m in E_mag],
                    'θ (°)': [f"{a:.1f}" for a in angle],
                })
                st.dataframe(df_out, use_container_width=True, hide_index=True)
            else:
                st.info("Sin sensores E o sin cargas.")

        # ===== Energía total del sistema =====
        if len(charges_df) >= 2:
            U_total = _total_energy(charges_df)
            st.metric("Energía total U del sistema", f"{U_total:.4f}",
                       help="U = k · Σ_{i<j} q_i q_j / |r_i − r_j|")

    # ====================================================================
    # Curvas de nivel del potencial — vistas 2D y 3D (estilo PDF)
    # ====================================================================
    st.markdown("---")
    st.subheader("Curvas de Nivel del Potencial V(x, y)")
    st.caption(
        "Visualización inspirada en las slides de "
        "`Recursos/POTENCIAL-ELECTRICO.pdf`: equipotenciales como curvas "
        "cerradas alrededor de las cargas, vistas en 2D (planta) y 3D "
        "(superficie z = V(x,y) con la proyección abajo)."
    )

    col_v1, col_v2, col_v3, col_v4 = st.columns([1.3, 1, 1, 1.2])
    with col_v1:
        vista = st.radio(
            "Vista",
            options=['2D', '3D', 'Ambas'],
            index=2,
            horizontal=True,
            key='phet_potencial_vista',
        )
    with col_v2:
        n_lev = st.slider("Nº de curvas", min_value=6, max_value=40,
                            value=18, step=2, key='phet_potencial_levels')
    with col_v3:
        res_lev = st.slider("Resolución", min_value=80, max_value=400,
                              value=200, step=20,
                              key='phet_potencial_res',
                              help=("Mayor = curvas más suaves pero "
                                     "render más lento"))
    with col_v4:
        rellenar = st.checkbox("Relleno (heatmap)", value=True,
                                  key='phet_potencial_fill')
        etiquetas = st.checkbox("Etiquetas numéricas", value=True,
                                    key='phet_potencial_labels')

    if len(charges_df) == 0:
        st.info("Añade al menos una carga (panel izquierdo) para ver "
                 "las curvas de nivel.")
    else:
        if vista in ('2D', 'Ambas'):
            fig_2d = render_potential_contours_2d(
                charges_df, l_dom,
                resolution=int(res_lev),
                n_levels=int(n_lev),
                show_labels=etiquetas,
                filled=rellenar,
            )
            st.pyplot(fig_2d, use_container_width=True)
            plt.close(fig_2d)

        if vista in ('3D', 'Ambas'):
            # Resolución 3D más baja para mantener interactividad fluida
            res_3d = min(int(res_lev), 120)
            fig_3d = render_potential_surface_3d(
                charges_df, l_dom,
                resolution=res_3d,
                n_levels=int(n_lev),
                show_projection=True,
            )
            st.plotly_chart(fig_3d, use_container_width=True,
                              config={'displaylogo': False})


def _total_energy(df: pd.DataFrame) -> float:
    """Energía electrostática total con softening."""
    x = df['x'].astype(float).values
    y = df['y'].astype(float).values
    q = df['q'].astype(float).values
    n = len(x)
    U = 0.0
    for i in range(n - 1):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            r = np.sqrt(dx * dx + dy * dy + EPSILON_SOFT ** 2)
            U += K_COULOMB * q[i] * q[j] / r
    return float(U)
