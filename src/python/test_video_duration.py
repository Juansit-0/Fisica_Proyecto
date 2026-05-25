#!/usr/bin/env python3
"""
Script de prueba para generar 3 videos y verificar la duración.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import imageio.v2 as imageio
from pathlib import Path
from typing import List, Dict, Tuple
import random


#===============================================================================
# CONFIGURACIÓN GLOBAL (MISMA QUE EL SCRIPT ORIGINAL)
#===============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_VIDEOS_DIR = PROJECT_ROOT / "results" / "test_videos"
OUTPUT_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Parámetros técnicos de video (NUEVOS VALORES)
# VALOR ANTERIOR: NUM_FRAMES = 60, VIDEO_DURATION = 10.0, FPS = 6.0
# NUEVO VALOR: Aumentamos frames drásticamente para ver MUCHO más movimiento
NUM_FRAMES = 120          # Aumentado de 60 a 120 frames (duplicado)
VIDEO_DURATION = 30.0     # Duración objetivo: 30 segundos
FPS = NUM_FRAMES / VIDEO_DURATION  # 4 FPS (más lento para detalle)

# Parámetros de visualización
COLOR_POSITIVE = '#E63946'
COLOR_NEGATIVE = '#457B9D'
MARKER_SIZE = 100
MARKER_EDGE_COLOR = 'white'
MARKER_EDGE_WIDTH = 1.5
L_DOMAIN = 10.0


#===============================================================================
# DEFINICIÓN DE 3 CONFIGURACIONES DE PRUEBA
#===============================================================================

def definir_configuraciones_prueba() -> List[Dict]:
    """
    Define 3 configuraciones para la prueba.
    """
    return [
        {
            "id": "test_01_repulsion",
            "nombre": "Prueba - Solo Repulsión 10 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 10,
            "cargas": np.ones(10),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (10, 2))
        },
        {
            "id": "test_02_mixto",
            "nombre": "Prueba - Atracción + Repulsión 20 partículas",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 20,
            "cargas": np.array([1]*10 + [-1]*10),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (20, 2))
        },
        {
            "id": "test_03_circular",
            "nombre": "Prueba - Configuración Circular",
            "categoria": "Solo Repulsión",
            "n_particulas": 12,
            "cargas": np.ones(12),
            "posiciones_iniciales": np.array([[8*np.cos(theta), 8*np.sin(theta)] for theta in np.linspace(0, 2*np.pi, 12, endpoint=False)])
        }
    ]


#===============================================================================
# SIMULACIÓN SIMPLIFICADA PARA ANIMACIÓN
#===============================================================================

def simular_movimiento(posiciones_iniciales: np.ndarray, cargas: np.ndarray, num_frames: int) -> List[np.ndarray]:
    posiciones = posiciones_iniciales.astype(float).copy()
    frames = [posiciones.copy()]
    
    for _ in range(num_frames - 1):
        fuerzas = np.zeros_like(posiciones)
        
        for i in range(len(posiciones)):
            for j in range(len(posiciones)):
                if i != j:
                    r = posiciones[j] - posiciones[i]
                    dist = np.linalg.norm(r)
                    if dist > 0.1:
                        fuerza = cargas[i] * cargas[j] * r / (dist**3)
                        fuerzas[i] += fuerza * 0.5
        
        posiciones += fuerzas * 0.08
        posiciones = np.clip(posiciones, -L_DOMAIN*0.95, L_DOMAIN*0.95)
        frames.append(posiciones.copy())
    
    return frames


#===============================================================================
# GENERACIÓN DE FRAMES Y VIDEO
#===============================================================================

def generar_frame(posiciones: np.ndarray, cargas: np.ndarray, config: Dict, frame_num: int, total_frames: int) -> str:
    plt.rcParams.update({
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
    })
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    pos_mask = cargas > 0
    neg_mask = cargas < 0
    
    if np.any(pos_mask):
        ax.scatter(
            posiciones[pos_mask, 0], posiciones[pos_mask, 1],
            c=COLOR_POSITIVE, s=MARKER_SIZE,
            edgecolors=MARKER_EDGE_COLOR, linewidths=MARKER_EDGE_WIDTH,
            label='+1', zorder=5, alpha=0.9
        )
    
    if np.any(neg_mask):
        ax.scatter(
            posiciones[neg_mask, 0], posiciones[neg_mask, 1],
            c=COLOR_NEGATIVE, s=MARKER_SIZE,
            edgecolors=MARKER_EDGE_COLOR, linewidths=MARKER_EDGE_WIDTH,
            label='−1', zorder=5, alpha=0.9, marker='s'
        )
    
    margin = L_DOMAIN * 0.08
    ax.set_xlim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_ylim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_aspect('equal')
    
    rect = plt.Rectangle(
        (-L_DOMAIN, -L_DOMAIN), 2*L_DOMAIN, 2*L_DOMAIN,
        fill=False, edgecolor='#58A6FF', linewidth=1.5,
        linestyle='--', alpha=0.6
    )
    ax.add_patch(rect)
    
    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')
    
    # Rotar etiquetas del eje X para evitar superposicion y reducir tamaño de fuente
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('y', fontsize=11)
    ax.set_title(config["nombre"], fontsize=13, fontweight='bold', pad=10)
    
    info = f"Categoría: {config['categoria']}\n"
    info += f"Partículas: {config['n_particulas']}\n"
    info += f"Frame: {frame_num+1}/{total_frames}"
    
    ax.text(
        0.02, 0.98, info, transform=ax.transAxes, fontsize=7,
        verticalalignment='top', color='#000000', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFFFF', edgecolor='#333333', alpha=0.9)
    )
    
    ax.legend(loc='upper right', fontsize=7, framealpha=0.8, facecolor='#FFFFFF', edgecolor='#333333')
    
    plt.tight_layout()
    
    frame_path = OUTPUT_VIDEOS_DIR / f"temp_frame_{frame_num:06d}.png"
    fig.savefig(frame_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    
    return str(frame_path)


def generar_video_configuracion(config: Dict) -> Path:
    print(f"\n  Generando video: {config['nombre']}")
    
    frames_posiciones = simular_movimiento(
        config["posiciones_iniciales"],
        config["cargas"],
        NUM_FRAMES
    )
    
    frame_paths = []
    for i, posiciones in enumerate(frames_posiciones):
        frame_path = generar_frame(posiciones, config["cargas"], config, i, NUM_FRAMES)
        frame_paths.append(frame_path)
        if (i+1) % 10 == 0 or i == NUM_FRAMES - 1:
            print(f"    Frame {i+1}/{NUM_FRAMES}")
    
    print(f"  Ensamblando video ({FPS:.1f} FPS)...")
    print(f"  Parámetros: {NUM_FRAMES} frames, {FPS:.1f} FPS, Duración esperada: {NUM_FRAMES/FPS:.1f} segundos")
    
    video_filename = f"{config['id']}.mp4"
    video_path = OUTPUT_VIDEOS_DIR / video_filename
    
    writer = imageio.get_writer(
        str(video_path),
        fps=FPS,
        codec='libx264',
        quality=9,
        pixelformat='yuv420p'
    )
    
    for fp in frame_paths:
        writer.append_data(imageio.imread(fp))
    
    writer.close()
    
    for fp in frame_paths:
        Path(fp).unlink()
    
    print(f"  Video generado: {video_path}")
    print(f"  Verificacion: {NUM_FRAMES} frames @ {FPS:.1f} FPS = {NUM_FRAMES/FPS:.1f} segundos")
    return video_path


#===============================================================================
# FUNCIÓN PRINCIPAL
#===============================================================================

def main():
    print("\n" + "="*80)
    print("  PRUEBA DE VIDEOS - DURACIÓN CORREGIDA")
    print("="*80)
    print(f"\n  Parámetros técnicos:")
    print(f"    Frames por video: {NUM_FRAMES} (anteriormente: 30)")
    print(f"    FPS: {FPS:.1f}")
    print(f"    Duración objetivo: {NUM_FRAMES/FPS:.1f} segundos")
    print(f"    Directorio de salida: {OUTPUT_VIDEOS_DIR}")
    
    configuraciones = definir_configuraciones_prueba()
    
    print(f"\n  Generando {len(configuraciones)} videos de prueba...")
    
    for config in configuraciones:
        generar_video_configuracion(config)
    
    print("\n" + "="*80)
    print("  RESUMEN DE PRUEBA")
    print("="*80)
    print(f"  Total videos generados: {len(configuraciones)}")
    print(f"  Cada video tiene: {NUM_FRAMES} frames")
    print(f"  Tasa de reproducción: {FPS:.1f} FPS")
    print(f"  Duración esperada por video: {NUM_FRAMES/FPS:.1f} segundos")
    print(f"  Directorio: {OUTPUT_VIDEOS_DIR}")
    print("\n  Prueba completada! Verifica la duración de los videos.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

