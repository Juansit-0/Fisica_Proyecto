"""
video_generator.py — Generación de video de la evolución del sistema

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import os
from pathlib import Path
from config import (FRAMES_DIR, VIDEOS_DIR, ENERGY_LOG,
                    COLOR_POSITIVE, COLOR_NEGATIVE, MARKER_SIZE,
                    MARKER_EDGE_COLOR, MARKER_EDGE_WIDTH,
                    L_DOMAIN, GRID_RESOLUTION, VIDEO_FPS, MATPLOTLIB_STYLE)
from data_loader import load_all_configurations, get_positions_and_charges


def generate_frame(df, frame_number, config_number, energy=None, total_configs=0):
    """Genera un frame individual para el video."""
    plt.rcParams.update(MATPLOTLIB_STYLE)
    x, y, q = get_positions_and_charges(df)

    fig, ax = plt.subplots(figsize=(8, 8))
    pos_mask = q > 0
    neg_mask = q < 0

    if np.any(pos_mask):
        ax.scatter(x[pos_mask], y[pos_mask], c=COLOR_POSITIVE, s=MARKER_SIZE*0.7,
                   edgecolors=MARKER_EDGE_COLOR, linewidths=MARKER_EDGE_WIDTH,
                   label='+1', zorder=5, alpha=0.9)
    if np.any(neg_mask):
        ax.scatter(x[neg_mask], y[neg_mask], c=COLOR_NEGATIVE, s=MARKER_SIZE*0.7,
                   edgecolors=MARKER_EDGE_COLOR, linewidths=MARKER_EDGE_WIDTH,
                   label='−1', zorder=5, alpha=0.9, marker='s')

    margin = L_DOMAIN * 0.08
    ax.set_xlim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_ylim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_aspect('equal')

    rect = plt.Rectangle((-L_DOMAIN, -L_DOMAIN), 2*L_DOMAIN, 2*L_DOMAIN,
                          fill=False, edgecolor='#58A6FF', linewidth=1.2,
                          linestyle='--', alpha=0.5)
    ax.add_patch(rect)
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('y', fontsize=11)
    ax.set_title('Evolución del Sistema de Cargas', fontsize=13, fontweight='bold', pad=10)
    
    # Configurar ticks de malla basados en GRID_RESOLUTION
    grid_spacing = (2.0 * L_DOMAIN) / (GRID_RESOLUTION - 1)
    ticks = np.arange(-L_DOMAIN, L_DOMAIN + grid_spacing, grid_spacing)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')
    
    # Rotar etiquetas del eje X para evitar superposicion y reducir tamaño de fuente
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)

    info = f'Config #{config_number}'
    if energy is not None:
        info += f'\nU = {energy:.4f}'
    if total_configs > 0:
        info += f'\nProgreso: {(frame_number+1)/total_configs*100:.0f}%'
    ax.text(0.02, 0.98, info, transform=ax.transAxes, fontsize=7,
            verticalalignment='top', color='#000000', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFFFF',
                      edgecolor='#333333', alpha=0.9))
    ax.legend(loc='upper right', fontsize=7, framealpha=0.8,
              facecolor='#FFFFFF', edgecolor='#333333')

    plt.tight_layout()
    frame_path = FRAMES_DIR / f'frame_{frame_number:06d}.png'
    fig.savefig(frame_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    return str(frame_path)


def generate_video(clean_frames=False):
    """Pipeline completo de generación de video."""
    print("\n  ")
    print("  GENERANDO VIDEO DE EVOLUCIÓN")
    print("  \n")

    import pandas as pd
    energy_data = None
    if ENERGY_LOG.exists():
        energy_df = pd.read_csv(ENERGY_LOG)
        energy_data = energy_df['energy'].values

    configs = load_all_configurations()
    total = len(configs)
    if total == 0:
        print("   No hay configuraciones.")
        return

    print(f"  Generando {total} frames...")
    frame_paths = []
    for i, (config_num, df) in enumerate(configs):
        energy = energy_data[min(i, len(energy_data)-1)] if energy_data is not None else None
        frame_path = generate_frame(df, i, config_num, energy, total)
        frame_paths.append(frame_path)
        if (i+1) % max(1, total//10) == 0 or i == total - 1:
            print(f"    Frame {i+1}/{total} ({(i+1)/total*100:.0f}%)")

    print(f"\n  Ensamblando video ({VIDEO_FPS} FPS)...")
    video_path = VIDEOS_DIR / 'evolucion_cargas.mp4'
    writer = imageio.get_writer(str(video_path), fps=VIDEO_FPS,
                                codec='libx264', quality=8, pixelformat='yuv420p')
    for fp in frame_paths:
        writer.append_data(imageio.imread(fp))
    writer.close()

    print(f"   Video generado: {video_path}")
    print(f"    Frames: {total}, FPS: {VIDEO_FPS}, Duración: {total/VIDEO_FPS:.1f}s")

    if clean_frames:
        for fp in frame_paths:
            os.remove(fp)
        print("   Frames eliminados")


if __name__ == '__main__':
    from config import ensure_dirs
    ensure_dirs()
    generate_video(clean_frames=False)
