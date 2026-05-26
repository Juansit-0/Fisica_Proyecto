"""
movable_charge.py — Mover una carga en la configuración final
==============================================================

Toma la configuración de mínima energía (final_config.csv) y permite al
usuario:

    1. Seleccionar UNA carga por su `particle_id`.
    2. Desplazarla en el plano vía sliders (x, y).
    3. Visualizar el sistema con la carga reubicada y comparar con la
       configuración original.
    4. Construir el mapa de calor de la energía total U(x, y) que
       resulta de fijar las N-1 cargas restantes y mover la elegida
       por todo el dominio (requisito directo del PDF del proyecto).

Física (idéntica al núcleo Fortran):
    U = k · Σ_{i<j} q_i q_j / |r_i − r_j|

Diseño:
- Estado persistente en st.session_state (no se pierde entre re-runs).
- Render con matplotlib (mismo estilo del resto del proyecto).
- Reutiliza constantes y colores de config.py.

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator

from config import (COLOR_POSITIVE, COLOR_NEGATIVE, MARKER_EDGE_COLOR,
                    L_DOMAIN, K_COULOMB, EPSILON_SOFT, EPSILON_VIZ,
                    CMAP_POTENTIAL, FIGURE_SIZE_SQUARE, MATPLOTLIB_STYLE,
                    OUTPUT_DIR)


#===============================================================================
# FÍSICA
#===============================================================================

def total_energy(df: pd.DataFrame, epsilon: float = EPSILON_SOFT) -> float:
    """Energía electrostática total del sistema con softening."""
    x = df['x'].astype(float).values
    y = df['y'].astype(float).values
    q = df['charge'].astype(float).values
    n = len(x)
    U = 0.0
    for i in range(n - 1):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            r = np.sqrt(dx * dx + dy * dy + epsilon * epsilon)
            U += K_COULOMB * q[i] * q[j] / r
    return float(U)


@st.cache_data(show_spinner=False, max_entries=8)
def _energy_landscape_cached(df_signature: tuple, idx_movable: int,
                               l_dom: float, resolution: int,
                               epsilon: float):
    """Wrapper cacheable: clave por (firma del DF, idx, l_dom, res, ε).

    Streamlit no hashea DataFrames trivialmente, por eso recibimos una
    tupla con (x_tuple, y_tuple, q_tuple) reconstruyendo el DF aquí.
    """
    xs, ys, qs = df_signature
    df_in = pd.DataFrame({'x': xs, 'y': ys, 'charge': qs})
    return energy_landscape(df_in, idx_movable, l_dom,
                              resolution=resolution, epsilon=epsilon)


def energy_landscape(df: pd.DataFrame, idx_movable: int,
                       l_dom: float, resolution: int = 150,
                       epsilon: float = EPSILON_VIZ) -> Tuple[np.ndarray,
                                                                 np.ndarray,
                                                                 np.ndarray]:
    """
    Construye U(x, y) cuando la carga `idx_movable` se desplaza por
    cada nodo (x, y) de una malla de `resolution × resolution`.

    Las demás N-1 cargas permanecen fijas en sus posiciones originales.

    Algoritmo eficiente:
        U_total(x, y) = U_fixed_only  +  q_movable · V_fixed(x, y)
    donde V_fixed(x, y) es el potencial generado por las cargas
    restantes evaluado en (x, y). Vectorizado completamente con
    broadcasting (NumPy).
    """
    x_fixed = df['x'].astype(float).values
    y_fixed = df['y'].astype(float).values
    q_fixed = df['charge'].astype(float).values

    q_movable = float(q_fixed[idx_movable])

    # Energía de las N-1 cargas fijas entre sí (constante)
    mask = np.arange(len(df)) != idx_movable
    xf = x_fixed[mask]
    yf = y_fixed[mask]
    qf = q_fixed[mask]
    n_fixed = len(xf)
    u_fixed_only = 0.0
    for i in range(n_fixed - 1):
        for j in range(i + 1, n_fixed):
            dx = xf[i] - xf[j]
            dy = yf[i] - yf[j]
            r = np.sqrt(dx * dx + dy * dy + epsilon * epsilon)
            u_fixed_only += K_COULOMB * qf[i] * qf[j] / r

    # Malla (x, y) donde se evalúa el potencial de las fijas
    xs = np.linspace(-l_dom, l_dom, resolution)
    ys = np.linspace(-l_dom, l_dom, resolution)
    X, Y = np.meshgrid(xs, ys)

    V_fixed = np.zeros_like(X)
    for k in range(n_fixed):
        dx = X - xf[k]
        dy = Y - yf[k]
        r = np.sqrt(dx * dx + dy * dy + epsilon * epsilon)
        V_fixed += K_COULOMB * qf[k] / r

    U = u_fixed_only + q_movable * V_fixed
    return X, Y, U


#===============================================================================
# RENDERS
#===============================================================================

def render_system_with_movable(df: pd.DataFrame, idx_movable: int,
                                 x_new: float, y_new: float, l_dom: float):
    """
    Render del sistema mostrando:
      - Cargas fijas (N-1) en color habitual.
      - La carga movible original como sombra (transparente).
      - La carga movible en su nueva posición destacada con halo.
      - Flecha que indica el desplazamiento.
    """
    plt.rcParams.update(MATPLOTLIB_STYLE)
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SQUARE)

    n = len(df)
    indices = np.arange(n)
    mask_fixed = indices != idx_movable

    x_all = df['x'].astype(float).values
    y_all = df['y'].astype(float).values
    q_all = df['charge'].astype(float).values

    # Cargas fijas
    x_f, y_f, q_f = x_all[mask_fixed], y_all[mask_fixed], q_all[mask_fixed]
    pos = q_f > 0
    neg = q_f < 0
    if np.any(pos):
        ax.scatter(x_f[pos], y_f[pos], c=COLOR_POSITIVE, s=120,
                    edgecolors=MARKER_EDGE_COLOR, linewidths=1.0,
                    zorder=8, marker='o', label='+1 (fija)')
    if np.any(neg):
        ax.scatter(x_f[neg], y_f[neg], c=COLOR_NEGATIVE, s=120,
                    edgecolors=MARKER_EDGE_COLOR, linewidths=1.0,
                    zorder=8, marker='s', label='−1 (fija)')

    # Posición ORIGINAL de la carga movible (fantasma)
    x_orig = float(x_all[idx_movable])
    y_orig = float(y_all[idx_movable])
    q_mov = float(q_all[idx_movable])
    color_mov = COLOR_POSITIVE if q_mov > 0 else COLOR_NEGATIVE
    marker_mov = 'o' if q_mov > 0 else 's'

    ax.scatter([x_orig], [y_orig], c=color_mov, s=200,
                edgecolors='#333333', linewidths=1.0, zorder=9,
                marker=marker_mov, alpha=0.25,
                label='Posición original')

    # Posición NUEVA con halo
    ax.scatter([x_new], [y_new], c=color_mov, s=280,
                edgecolors='black', linewidths=2.0, zorder=12,
                marker=marker_mov, alpha=0.95,
                label=f'Carga #{idx_movable + 1} (movida)')
    ax.scatter([x_new], [y_new], c='none', s=750,
                edgecolors='#FFD700', linewidths=2.5, zorder=11)

    # Flecha de desplazamiento
    if (x_new, y_new) != (x_orig, y_orig):
        ax.annotate('', xy=(x_new, y_new), xytext=(x_orig, y_orig),
                     arrowprops=dict(arrowstyle='->', color='#1D3557',
                                      lw=2.0, alpha=0.9), zorder=10)

    # Dominio
    rect = plt.Rectangle((-l_dom, -l_dom), 2 * l_dom, 2 * l_dom,
                          fill=False, edgecolor='#58A6FF', linewidth=1.5,
                          linestyle='--', alpha=0.6)
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
    ax.set_title(f'Sistema con Carga #{idx_movable + 1} Movida',
                  fontsize=13, fontweight='bold', pad=10)
    ax.grid(True, alpha=0.25, color='#888888', linewidth=0.4,
             linestyle='--')
    ax.legend(loc='upper right', fontsize=8, framealpha=0.85,
               facecolor='#FFFFFF', edgecolor='#333333')

    plt.tight_layout()
    return fig


def compute_potential_map(df: pd.DataFrame, l_dom: float,
                            resolution: int = 150,
                            epsilon: float = EPSILON_VIZ):
    """
    Potencial eléctrico V(x, y) del sistema completo con TODAS las
    cargas en las posiciones actuales del DataFrame.

    V(r) = k · Σ q_i / |r - r_i|

    Para usar tras mover una carga: pasar el df modificado para ver
    cómo cambia el campo de potencial.
    """
    xs = np.linspace(-l_dom, l_dom, resolution)
    ys = np.linspace(-l_dom, l_dom, resolution)
    X, Y = np.meshgrid(xs, ys)

    x_arr = df['x'].astype(float).values
    y_arr = df['y'].astype(float).values
    q_arr = df['charge'].astype(float).values

    V = np.zeros_like(X)
    for i in range(len(df)):
        dx = X - x_arr[i]
        dy = Y - y_arr[i]
        r = np.sqrt(dx * dx + dy * dy + epsilon * epsilon)
        V += K_COULOMB * q_arr[i] / r
    return X, Y, V


def render_potential_map_with_charges(df_modified: pd.DataFrame,
                                         idx_movable: int,
                                         l_dom: float,
                                         resolution: int = 150,
                                         current_x: float = None,
                                         current_y: float = None):
    """
    Mapa de calor del POTENCIAL V(x, y) del sistema con la carga
    `idx_movable` ya colocada en su NUEVA posición (current_x,
    current_y). Este mapa SÍ se actualiza al mover el slider porque
    el potencial depende de la posición de la carga.
    """
    plt.rcParams.update(MATPLOTLIB_STYLE)
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SQUARE)

    X, Y, V = compute_potential_map(df_modified, l_dom, resolution)

    # Saturación percentil 3-97 para evitar spikes de cargas puntuales
    v_lo = float(np.percentile(V, 3))
    v_hi = float(np.percentile(V, 97))
    V_clipped = np.clip(V, v_lo, v_hi)

    # Norma robusta: divergente si cruza 0, lineal si monosigno
    has_pos = bool(np.any(V_clipped > 0))
    has_neg = bool(np.any(V_clipped < 0))
    if has_pos and has_neg:
        v_p = max(abs(v_lo), abs(v_hi))
        norm = mcolors.TwoSlopeNorm(vmin=-v_p, vcenter=0.0, vmax=v_p)
        cmap_name = CMAP_POTENTIAL
    else:
        norm = mcolors.Normalize(vmin=v_lo, vmax=v_hi)
        cmap_name = 'inferno' if has_pos else 'inferno_r'

    im = ax.pcolormesh(X, Y, V_clipped, cmap=cmap_name, norm=norm,
                        shading='gouraud', alpha=0.92)
    cbar = plt.colorbar(im, ax=ax, label='Potencial V(x, y)',
                         shrink=0.85, pad=0.02)
    cbar.ax.yaxis.label.set_color('#000000')
    cbar.ax.tick_params(colors='#000000', labelsize=9)

    # Contornos de equipotenciales
    try:
        levels = np.linspace(V_clipped.min(), V_clipped.max(), 12)
        ax.contour(X, Y, V_clipped, levels=levels, colors='#1D3557',
                    linewidths=0.6, alpha=0.5)
    except Exception:
        pass

    # Cargas fijas (todas menos la movible)
    n = len(df_modified)
    mask_fixed = np.arange(n) != idx_movable
    x_all = df_modified['x'].astype(float).values
    y_all = df_modified['y'].astype(float).values
    q_all = df_modified['charge'].astype(float).values
    x_f, y_f, q_f = x_all[mask_fixed], y_all[mask_fixed], q_all[mask_fixed]
    pos = q_f > 0
    neg = q_f < 0
    if np.any(pos):
        ax.scatter(x_f[pos], y_f[pos], c=COLOR_POSITIVE, s=80,
                    edgecolors='black', linewidths=1.0, zorder=10,
                    marker='o', label='+1 (fija)')
    if np.any(neg):
        ax.scatter(x_f[neg], y_f[neg], c=COLOR_NEGATIVE, s=80,
                    edgecolors='black', linewidths=1.0, zorder=10,
                    marker='s', label='−1 (fija)')

    # Carga MÓVIL en su posición nueva — destacada con halo
    if current_x is not None and current_y is not None:
        q_mov = float(df_modified.iloc[idx_movable]['charge'])
        c_mov = COLOR_POSITIVE if q_mov > 0 else COLOR_NEGATIVE
        m_mov = 'o' if q_mov > 0 else 's'
        ax.scatter([current_x], [current_y], c='none', s=750,
                    edgecolors='#FFD700', linewidths=2.5, zorder=14)
        ax.scatter([current_x], [current_y], c=c_mov, s=220,
                    edgecolors='black', linewidths=1.8, zorder=15,
                    marker=m_mov, label=f'Carga #{idx_movable + 1} '
                                           f'(movida)')

    margin = l_dom * 0.05
    ax.set_xlim(-l_dom - margin, l_dom + margin)
    ax.set_ylim(-l_dom - margin, l_dom + margin)
    ax.set_aspect('equal')
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.tick_params(axis='both', labelsize=9)
    ax.set_title('Potencial V(x, y) del sistema modificado',
                  fontsize=12, fontweight='bold', pad=10)
    ax.grid(True, alpha=0.18, color='#888888', linewidth=0.4,
             linestyle='--')
    ax.legend(loc='upper right', fontsize=8, framealpha=0.85,
               facecolor='#FFFFFF', edgecolor='#333333')

    plt.tight_layout()
    return fig, V


def render_energy_landscape_map(df: pd.DataFrame, idx_movable: int,
                                  l_dom: float, resolution: int = 150,
                                  current_x: float = None,
                                  current_y: float = None,
                                  precomputed=None):
    """
    Mapa de calor U(x, y) — fijando todas las cargas excepto la
    seleccionada y desplazándola por toda la malla.

    Cumple el requisito del PDF:
       'Fijar todas las cargas excepto una, desplazar esa carga en el
        plano y calcular la energía total del sistema en cada nueva
        posición y realizar el mapa de calor.'

    Si `precomputed` (tupla X, Y, U) se proporciona, se usa directamente
    sin recalcular el landscape — solo cambia el marker de la posición
    actual. Esto hace que mover el slider sea inmediato.
    """
    plt.rcParams.update(MATPLOTLIB_STYLE)
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SQUARE)

    if precomputed is not None:
        X, Y, U = precomputed
    else:
        X, Y, U = energy_landscape(df, idx_movable, l_dom, resolution)

    # Saturación por percentiles para que un par de píxeles no rompan
    # la escala (cerca de las cargas vivas U diverge como 1/r).
    u_lo = float(np.percentile(U, 3))
    u_hi = float(np.percentile(U, 97))
    U_clipped = np.clip(U, u_lo, u_hi)

    # Norma robusta: si U es monosigno usar Normalize, si cruza 0 usar
    # TwoSlopeNorm centrado en U_min (mejor contraste de la cuenca).
    has_pos = bool(np.any(U_clipped > 0))
    has_neg = bool(np.any(U_clipped < 0))
    if has_pos and has_neg:
        norm = mcolors.TwoSlopeNorm(vmin=u_lo, vcenter=0.0, vmax=u_hi)
        cmap_name = CMAP_POTENTIAL
    else:
        norm = mcolors.Normalize(vmin=u_lo, vmax=u_hi)
        cmap_name = 'inferno' if has_pos else 'inferno_r'

    im = ax.pcolormesh(X, Y, U_clipped, cmap=cmap_name, norm=norm,
                        shading='gouraud', alpha=0.92)
    cbar = plt.colorbar(im, ax=ax,
                         label=f'U(x, y) variando carga #{idx_movable + 1}',
                         shrink=0.85, pad=0.02)
    cbar.ax.yaxis.label.set_color('#000000')
    cbar.ax.tick_params(colors='#000000', labelsize=9)

    # Contornos de iso-energía
    try:
        levels = np.linspace(u_lo, u_hi, 12)
        ax.contour(X, Y, U_clipped, levels=levels, colors='#1D3557',
                    linewidths=0.6, alpha=0.55)
    except Exception:
        pass

    # Cargas fijas
    n = len(df)
    mask_fixed = np.arange(n) != idx_movable
    x_all = df['x'].astype(float).values
    y_all = df['y'].astype(float).values
    q_all = df['charge'].astype(float).values
    x_f, y_f, q_f = x_all[mask_fixed], y_all[mask_fixed], q_all[mask_fixed]
    pos = q_f > 0
    neg = q_f < 0
    if np.any(pos):
        ax.scatter(x_f[pos], y_f[pos], c=COLOR_POSITIVE, s=80,
                    edgecolors='black', linewidths=1.0, zorder=10,
                    marker='o', label='+1 (fija)')
    if np.any(neg):
        ax.scatter(x_f[neg], y_f[neg], c=COLOR_NEGATIVE, s=80,
                    edgecolors='black', linewidths=1.0, zorder=10,
                    marker='s', label='−1 (fija)')

    # Posición actual de la carga móvil (puntero)
    if current_x is not None and current_y is not None:
        ax.scatter([current_x], [current_y], c='#FFD700', s=220,
                    edgecolors='black', linewidths=1.8, zorder=15,
                    marker='*', label=f'Carga #{idx_movable + 1}')

    margin = l_dom * 0.05
    ax.set_xlim(-l_dom - margin, l_dom + margin)
    ax.set_ylim(-l_dom - margin, l_dom + margin)
    ax.set_aspect('equal')
    ax.set_xlabel('x (posición de la carga movible)', fontsize=12)
    ax.set_ylabel('y (posición de la carga movible)', fontsize=12)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
    ax.tick_params(axis='both', labelsize=9)
    ax.set_title(f'Mapa de Calor U(x, y) — Carga #{idx_movable + 1} '
                  f'libre, resto fijas',
                  fontsize=12, fontweight='bold', pad=10)
    ax.grid(True, alpha=0.18, color='#888888', linewidth=0.4,
             linestyle='--')
    ax.legend(loc='upper right', fontsize=8, framealpha=0.85,
               facecolor='#FFFFFF', edgecolor='#333333')

    plt.tight_layout()
    return fig, U


#===============================================================================
# UI STREAMLIT
#===============================================================================

def _load_final_config() -> pd.DataFrame:
    """Carga la configuración de mínima energía desde final_config.csv."""
    final_path = OUTPUT_DIR / "final_config.csv"
    if not final_path.exists():
        return pd.DataFrame(columns=['particle_id', 'x', 'y', 'charge'])
    return pd.read_csv(final_path)


def run_movable_charge_tab():
    """
    Renderiza la tab "Carga Móvil" dentro de la GUI Streamlit.

    Permite al usuario seleccionar una carga de la configuración final
    y moverla con sliders x, y para observar:
        - ΔU vs configuración mínima.
        - Mapa de calor U(x, y) sobre todo el dominio.
    """
    st.header("Carga Móvil sobre la Configuración Final")
    st.caption(
        "Sobre la configuración de mínima energía, selecciona una "
        "carga y muévela para comparar cómo se transforma el sistema "
        "y cuánto cambia la energía total."
    )

    df_final = _load_final_config()
    if len(df_final) == 0:
        st.warning(
            "No se encontró `data/output/final_config.csv`. "
            "Ejecuta primero una simulación.")
        return

    n = len(df_final)
    l_dom = float(L_DOMAIN)
    U_orig = total_energy(df_final)

    # ===== Estado persistente =====
    # IMPORTANTE: Streamlit prohíbe modificar st.session_state[key] de un
    # widget DESPUÉS de instanciarlo. Por eso usamos callbacks `on_click`
    # / `on_change` que se ejecutan ANTES del rerun, modificando las
    # keys con el widget aún no creado en ese pass.
    if 'movable_idx' not in st.session_state:
        st.session_state.movable_idx = 0
    if 'slider_movable_x' not in st.session_state:
        st.session_state.slider_movable_x = float(df_final.iloc[0]['x'])
    if 'slider_movable_y' not in st.session_state:
        st.session_state.slider_movable_y = float(df_final.iloc[0]['y'])

    # Opciones del selectbox (necesarias para resolver new_idx en el
    # callback `on_change`)
    options = [f"#{int(row['particle_id'])}  q={int(row['charge']):+d}  "
                f"({row['x']:+.3f}, {row['y']:+.3f})"
                for _, row in df_final.iterrows()]

    # ---- Callbacks ----
    def _on_select_change():
        """Cambio de carga seleccionada: actualiza idx y resetea
        sliders a la pos original de la nueva carga."""
        new_label = st.session_state.movable_select
        try:
            new_idx = options.index(new_label)
        except ValueError:
            return
        st.session_state.movable_idx = new_idx
        st.session_state.slider_movable_x = float(df_final.iloc[new_idx]['x'])
        st.session_state.slider_movable_y = float(df_final.iloc[new_idx]['y'])

    def _on_reset_click():
        idx_cur = int(st.session_state.movable_idx)
        st.session_state.slider_movable_x = float(df_final.iloc[idx_cur]['x'])
        st.session_state.slider_movable_y = float(df_final.iloc[idx_cur]['y'])

    def _on_center_click():
        st.session_state.slider_movable_x = 0.0
        st.session_state.slider_movable_y = 0.0

    # ===== Panel de control =====
    col_ctrl, col_metrics = st.columns([1.1, 1])

    with col_ctrl:
        st.subheader("Selección y desplazamiento")

        st.selectbox(
            "Carga a mover",
            options=options,
            index=int(st.session_state.movable_idx),
            key='movable_select',
            on_change=_on_select_change,
        )

        idx = int(st.session_state.movable_idx)
        x_orig = float(df_final.iloc[idx]['x'])
        y_orig = float(df_final.iloc[idx]['y'])

        # Sliders x, y — solo `key=`, lectura por st.session_state
        st.slider("Nueva posición x",
                   min_value=-l_dom, max_value=l_dom,
                   step=0.05, key='slider_movable_x')
        st.slider("Nueva posición y",
                   min_value=-l_dom, max_value=l_dom,
                   step=0.05, key='slider_movable_y')
        x_new = float(st.session_state.slider_movable_x)
        y_new = float(st.session_state.slider_movable_y)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.button("Resetear a posición original",
                       key='btn_reset_movable',
                       on_click=_on_reset_click)
        with col_b2:
            st.button("Mover al centro (0, 0)",
                       key='btn_center_movable',
                       on_click=_on_center_click)

    with col_metrics:
        st.subheader("Energía del sistema")
        # Calcular U con la carga en su nueva posición
        df_modified = df_final.copy()
        df_modified.at[idx, 'x'] = float(x_new)
        df_modified.at[idx, 'y'] = float(y_new)
        U_new = total_energy(df_modified)
        delta_U = U_new - U_orig

        # Métricas
        m1, m2 = st.columns(2)
        m1.metric("U original (mínima)", f"{U_orig:.4f}")
        m2.metric("U nueva", f"{U_new:.4f}",
                    delta=f"{delta_U:+.4f}",
                    delta_color=("inverse" if delta_U > 0 else "normal"))

        st.markdown("---")
        # Interpretación
        if abs(delta_U) < 1e-6:
            st.info("Sin cambio — la carga está en su posición original.")
        elif delta_U > 0:
            st.warning(
                f"La nueva posición **aumenta** la energía en "
                f"{delta_U:.4f}. La configuración original era más estable.")
        else:
            st.success(
                f"La nueva posición **reduce** aún más la energía en "
                f"{abs(delta_U):.4f}. El sistema no había convergido al "
                f"mínimo global para esta carga.")

        # Distancia recorrida
        dx = x_new - x_orig
        dy = y_new - y_orig
        dist = float(np.sqrt(dx * dx + dy * dy))
        st.caption(f"Desplazamiento: Δr = {dist:.3f}  "
                    f"(Δx = {dx:+.3f}, Δy = {dy:+.3f})")

    st.markdown("---")

    # ===== Visualizaciones =====
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.subheader("Sistema con la carga movida")
        fig_sys = render_system_with_movable(
            df_final, idx,
            st.session_state.slider_movable_x,
            st.session_state.slider_movable_y,
            l_dom,
        )
        st.pyplot(fig_sys, use_container_width=True)
        plt.close(fig_sys)

    with col_v2:
        st.subheader("Mapa de calor")
        mapa_mode = st.radio(
            "Tipo de mapa",
            options=['Potencial V(x, y) del sistema modificado',
                     'Energía U(x, y) variando esta carga'],
            index=0,
            key='movable_map_mode',
            help=(
                "Potencial V: muestra el campo de potencial del "
                "sistema con la carga MOVIDA en su pos actual. "
                "Cambia cuando mueves el slider.\n\n"
                "Energía U: muestra la energía total si la carga "
                "se pusiera en cada punto (las demás fijas). El "
                "fondo NO cambia con el slider — solo la estrella."
            ),
        )
        resolution = st.slider(
            "Resolución del mapa",
            min_value=60, max_value=300, value=100, step=20,
            key='slider_landscape_res',
            help="Mayor = mapa más suave, render más lento.",
        )

        if mapa_mode.startswith('Potencial'):
            # Mapa V(x, y) del sistema con la carga en pos NUEVA
            # → SÍ se actualiza al mover el slider.
            fig_map, _ = render_potential_map_with_charges(
                df_modified, idx, l_dom,
                resolution=int(resolution),
                current_x=float(st.session_state.slider_movable_x),
                current_y=float(st.session_state.slider_movable_y),
            )
            st.pyplot(fig_map, use_container_width=True)
            plt.close(fig_map)
            st.caption(
                "Las **equipotenciales** son las curvas negras. La "
                "**estrella dorada** marca la carga movida. Al mover "
                "el slider, todo el campo se redibuja.")
        else:
            # Mapa U(x, y) clásico — solo la estrella sigue al slider.
            df_sig = (
                tuple(df_final['x'].astype(float).tolist()),
                tuple(df_final['y'].astype(float).tolist()),
                tuple(df_final['charge'].astype(float).tolist()),
            )
            X_grid, Y_grid, U_grid = _energy_landscape_cached(
                df_sig, idx, l_dom, int(resolution), float(EPSILON_VIZ))
            fig_map, _ = render_energy_landscape_map(
                df_final, idx, l_dom,
                resolution=int(resolution),
                current_x=float(st.session_state.slider_movable_x),
                current_y=float(st.session_state.slider_movable_y),
                precomputed=(X_grid, Y_grid, U_grid),
            )
            st.pyplot(fig_map, use_container_width=True)
            plt.close(fig_map)
            st.caption(
                "U(x, y) = energía total del sistema SI la carga "
                "seleccionada se pusiera en (x, y). Es función del "
                "dominio, no de la posición actual → solo la estrella "
                "se mueve.")

            # Mínimo global del mapa U (solo en modo Energía)
            u_min_global = float(U_grid.min())
            u_max_global = float(U_grid.max())
            idx_min = np.unravel_index(np.argmin(U_grid), U_grid.shape)
            x_grid_axis = np.linspace(-l_dom, l_dom, U_grid.shape[1])
            y_grid_axis = np.linspace(-l_dom, l_dom, U_grid.shape[0])
            st.caption(
                f"Mín U(x,y) en el mapa = {u_min_global:.4f} en "
                f"({x_grid_axis[idx_min[1]]:+.2f}, "
                f"{y_grid_axis[idx_min[0]]:+.2f})  |  "
                f"Máx = {u_max_global:.4f}")
