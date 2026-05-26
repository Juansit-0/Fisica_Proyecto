"""
video_generator.py — Generación de video de la evolución del sistema
=====================================================================

Estrategia:
    1. Cargar todas las configuraciones guardadas por la simulación.
    2. Construir una secuencia de exactamente VIDEO_TARGET_FRAMES frames:
        - Si hay más configuraciones que frames objetivo, se hace
          subsampling uniforme (cubre toda la simulación).
        - Si hay menos, se interpolan posiciones linealmente entre
          configuraciones consecutivas para suavizar el movimiento.
    3. Renderizar todos los frames al mismo tamaño exacto en píxeles
       (sin bbox_inches='tight' que cambia el tamaño y rompe encoders).
    4. Encodear a libx264 con FPS = TARGET_FRAMES / DURATION (≈30 fps),
       resultando en un video de duración VIDEO_DURATION_S segundos.

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import imageio.v2 as imageio
import os
from pathlib import Path

from config import (FRAMES_DIR, VIDEOS_DIR, ENERGY_LOG,
                    COLOR_POSITIVE, COLOR_NEGATIVE, MARKER_SIZE,
                    MARKER_EDGE_COLOR, MARKER_EDGE_WIDTH,
                    L_DOMAIN, GRID_RESOLUTION, MATPLOTLIB_STYLE,
                    VIDEO_FPS, VIDEO_DURATION_S, VIDEO_TARGET_FRAMES,
                    VIDEO_QUALITY, VIDEO_FRAME_SIZE, VIDEO_FRAME_DPI,
                    VIDEO_INTERPOLATION_MODE, VIDEO_SHOW_FULL_GRID)
from data_loader import load_all_configurations, get_positions_and_charges


def _build_interpolated_sequence(configs, energies, target_frames):
    """
    Construye una secuencia de exactamente `target_frames` frames a partir
    de las configuraciones disponibles.

    - Si len(configs) >= target_frames: muestreo uniforme.
    - Si len(configs) <  target_frames: interpolación lineal de posiciones
      entre configuraciones consecutivas (las cargas q se mantienen del
      frame "from"; el orden de partículas se asume idéntico entre
      configuraciones, lo cual cumple el algoritmo Fortran).

    Cada elemento de la secuencia devuelta es un dict con:
        x, y, q (arrays 1D), energy (float|None), config_num (int)
    """
    n = len(configs)
    if n == 0:
        return []

    # Pre-extraer arrays para evitar overhead de get_positions_and_charges
    arrays = []
    for (cnum, df) in configs:
        x, y, q = get_positions_and_charges(df)
        arrays.append((cnum, np.asarray(x, dtype=float),
                       np.asarray(y, dtype=float),
                       np.asarray(q, dtype=float)))

    def _energy_for(idx_real):
        if energies is None or len(energies) == 0:
            return None
        return float(energies[min(idx_real, len(energies) - 1)])

    # Caso 1: tenemos suficientes configs → subsampling uniforme
    if n >= target_frames:
        idxs = np.linspace(0, n - 1, target_frames).astype(int)
        seq = []
        for idx in idxs:
            cnum, x, y, q = arrays[idx]
            seq.append({
                'x': x, 'y': y, 'q': q,
                'energy': _energy_for(idx),
                'config_num': cnum,
            })
        return seq

    # Caso 2: pocas configs → cubrir target_frames repitiendo configs.
    # Mapear cada frame de salida t ∈ [0, target_frames-1] a un t real
    # ∈ [0, n-1] continuo. Según el modo:
    #   - 'nearest': elegir la config real más cercana (movimiento en
    #     saltos discretos, respeta el snap-to-grid de la simulación).
    #   - 'linear':  interpolar posiciones entre las dos configs vecinas
    #     (movimiento suave, pero posiciones intermedias quedan fuera
    #     de la malla discreta).
    seq = []
    mode = VIDEO_INTERPOLATION_MODE
    for t in range(target_frames):
        t_real = t * (n - 1) / max(target_frames - 1, 1)

        if mode == 'nearest':
            idx = int(round(t_real))
            idx = max(0, min(idx, n - 1))
            cnum, x_out, y_out, q_out = arrays[idx]
            e_out = _energy_for(idx)
        else:  # 'linear'
            i = int(np.floor(t_real))
            j = min(i + 1, n - 1)
            alpha = t_real - i
            cnum, xa, ya, qa = arrays[i]
            _, xb, yb, _ = arrays[j]
            if len(xa) != len(xb):
                x_out, y_out = xa, ya
            else:
                x_out = (1.0 - alpha) * xa + alpha * xb
                y_out = (1.0 - alpha) * ya + alpha * yb
            q_out = qa
            e_a = _energy_for(i)
            e_b = _energy_for(j)
            if e_a is None or e_b is None:
                e_out = e_a if e_a is not None else e_b
            else:
                e_out = (1.0 - alpha) * e_a + alpha * e_b

        seq.append({
            'x': x_out, 'y': y_out, 'q': q_out,
            'energy': e_out,
            'config_num': cnum,
        })
    return seq


def _render_frame(state, frame_idx, total_frames, fig, ax):
    """Renderiza un frame sobre los ejes reutilizados (sin recrearlos).

    Reusar fig/ax es ~5-10× más rápido y garantiza que todos los frames
    tengan exactamente el mismo tamaño en píxeles (requerido por libx264).
    """
    ax.clear()

    x, y, q = state['x'], state['y'], state['q']
    pos_mask = q > 0
    neg_mask = q < 0

    if np.any(pos_mask):
        ax.scatter(x[pos_mask], y[pos_mask], c=COLOR_POSITIVE,
                    s=MARKER_SIZE * 0.7,
                    edgecolors=MARKER_EDGE_COLOR,
                    linewidths=MARKER_EDGE_WIDTH,
                    label='+1', zorder=5, alpha=0.95)
    if np.any(neg_mask):
        ax.scatter(x[neg_mask], y[neg_mask], c=COLOR_NEGATIVE,
                    s=MARKER_SIZE * 0.7,
                    edgecolors=MARKER_EDGE_COLOR,
                    linewidths=MARKER_EDGE_WIDTH,
                    label='−1', zorder=5, alpha=0.95, marker='s')

    margin = L_DOMAIN * 0.08
    ax.set_xlim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_ylim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_aspect('equal')

    rect = plt.Rectangle((-L_DOMAIN, -L_DOMAIN), 2 * L_DOMAIN, 2 * L_DOMAIN,
                          fill=False, edgecolor='#58A6FF', linewidth=1.2,
                          linestyle='--', alpha=0.55)
    ax.add_patch(rect)

    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('y', fontsize=11)
    ax.set_title('Evolución del Sistema de Cargas',
                  fontsize=13, fontweight='bold', pad=10)

    if VIDEO_SHOW_FULL_GRID:
        # Restaurar la malla densa GRID_RESOLUTION del video original.
        # Los ticks coinciden con las celdas a las que se snappean las cargas.
        grid_spacing = (2.0 * L_DOMAIN) / (GRID_RESOLUTION - 1)
        ticks = np.arange(-L_DOMAIN, L_DOMAIN + grid_spacing * 0.5,
                           grid_spacing)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.grid(True, alpha=0.55, color='#888888', linewidth=0.6,
                 linestyle='-')
        # Labels rotados y pequeños para no saturar
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=6)
        plt.setp(ax.get_yticklabels(), fontsize=6)
    else:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=9, prune='both'))
        ax.tick_params(axis='both', labelsize=9)
        ax.grid(True, alpha=0.25, color='#888888', linewidth=0.4,
                 linestyle='--')

    info = f"Config #{state['config_num']}"
    if state['energy'] is not None:
        info += f"\nU = {state['energy']:.4f}"
    info += f"\nProgreso: {(frame_idx + 1) / total_frames * 100:.0f}%"
    ax.text(0.02, 0.98, info, transform=ax.transAxes, fontsize=9,
             verticalalignment='top', color='#000000', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.35', facecolor='#FFFFFF',
                       edgecolor='#333333', alpha=0.9))

    ax.legend(loc='upper right', fontsize=9, framealpha=0.85,
               facecolor='#FFFFFF', edgecolor='#333333')


def generate_video(clean_frames=True):
    """Pipeline completo de generación de video fluido."""
    print("\n  ")
    print("  GENERANDO VIDEO DE EVOLUCIÓN")
    print("  \n")

    import pandas as pd
    energy_data = None
    if ENERGY_LOG.exists():
        energy_df = pd.read_csv(ENERGY_LOG)
        energy_data = energy_df['energy'].values

    configs = load_all_configurations()
    n_configs = len(configs)
    if n_configs == 0:
        print("   No hay configuraciones.")
        return

    target = VIDEO_TARGET_FRAMES
    if n_configs >= target:
        modo = f"subsampling uniforme ({n_configs} → {target})"
    else:
        modo = f"interpolación lineal ({n_configs} → {target})"
    print(f"  Configuraciones disponibles: {n_configs}")
    print(f"  Frames objetivo: {target} ({modo})")
    print(f"  Duración objetivo: {VIDEO_DURATION_S}s @ {VIDEO_FPS:.1f} fps")

    sequence = _build_interpolated_sequence(configs, energy_data, target)

    # === Setup matplotlib con tamaño exacto en píxeles ===
    plt.rcParams.update(MATPLOTLIB_STYLE)
    width_px, height_px = VIDEO_FRAME_SIZE
    fig_w = width_px / VIDEO_FRAME_DPI
    fig_h = height_px / VIDEO_FRAME_DPI
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=VIDEO_FRAME_DPI)
    fig.subplots_adjust(left=0.10, right=0.96, top=0.92, bottom=0.10)

    # === Renderizar frames a disco (PNGs ordenados) ===
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    frame_paths = []
    print(f"  Renderizando {target} frames...")
    for i, state in enumerate(sequence):
        _render_frame(state, i, target, fig, ax)
        frame_path = FRAMES_DIR / f'frame_{i:06d}.png'
        fig.savefig(frame_path, dpi=VIDEO_FRAME_DPI,
                     facecolor=fig.get_facecolor())
        frame_paths.append(str(frame_path))
        if (i + 1) % max(1, target // 10) == 0 or i == target - 1:
            print(f"    Frame {i + 1}/{target} ({(i + 1) / target * 100:.0f}%)")

    plt.close(fig)

    # === Encodear video ===
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    video_path = VIDEOS_DIR / 'evolucion_cargas.mp4'
    print(f"\n  Ensamblando video con libx264 a {VIDEO_FPS:.1f} fps...")
    writer = imageio.get_writer(
        str(video_path), fps=VIDEO_FPS, codec='libx264',
        quality=VIDEO_QUALITY, pixelformat='yuv420p',
        macro_block_size=1,  # evita warning si dimensión no divisible por 16
    )
    for fp in frame_paths:
        writer.append_data(imageio.imread(fp))
    writer.close()

    duration_real = target / VIDEO_FPS
    print(f"   Video generado: {video_path}")
    print(f"    Frames: {target}  FPS: {VIDEO_FPS:.1f}  "
           f"Duración: {duration_real:.2f}s")

    if clean_frames:
        for fp in frame_paths:
            try:
                os.remove(fp)
            except OSError:
                pass
        print("   Frames temporales eliminados.")


if __name__ == '__main__':
    from config import ensure_dirs
    ensure_dirs()
    generate_video(clean_frames=True)
