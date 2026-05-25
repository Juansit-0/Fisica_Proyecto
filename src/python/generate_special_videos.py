#!/usr/bin/env python3
"""
Script para generar videos de simulación de cargas eléctricas con requisitos específicos:
- Dos categorías: SOLO REPULSIÓN y ATRACCIÓN + REPULSIÓN
- 15+ configuraciones únicas
- 30 frames por video, 5 segundos de duración (6 FPS)
- Velocidad de movimiento clara y lenta
- Etiquetas detalladas en cada video

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
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
# CONFIGURACIÓN GLOBAL
#===============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_VIDEOS_DIR = PROJECT_ROOT / "results" / "special_videos"
OUTPUT_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Parámetros técnicos de video
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
# DEFINICIÓN DE CONFIGURACIONES
#===============================================================================

def definir_configuraciones() -> Tuple[List[Dict], List[Dict]]:
    """
    Define dos categorías de configuraciones:
    1. SOLO REPULSIÓN (todas las cargas +1)
    2. ATRACCIÓN + REPULSIÓN (mezcla de +1 y -1)
    
    Total: MUCHAS configuraciones únicas (más de 30)
    """
    
    #---------------------------------------------------------------------------
    # CATEGORÍA 1: SOLO REPULSIÓN (18 configuraciones)
    #---------------------------------------------------------------------------
    solo_repulsion = [
        {
            "id": "repulsion_01",
            "nombre": "Solo Repulsión - 5 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 5,
            "cargas": np.ones(5),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (5, 2))
        },
        {
            "id": "repulsion_02",
            "nombre": "Solo Repulsión - 10 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 10,
            "cargas": np.ones(10),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (10, 2))
        },
        {
            "id": "repulsion_03",
            "nombre": "Solo Repulsión - 15 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 15,
            "cargas": np.ones(15),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (15, 2))
        },
        {
            "id": "repulsion_04",
            "nombre": "Solo Repulsión - 20 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 20,
            "cargas": np.ones(20),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (20, 2))
        },
        {
            "id": "repulsion_05",
            "nombre": "Solo Repulsión - 25 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 25,
            "cargas": np.ones(25),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (25, 2))
        },
        {
            "id": "repulsion_06",
            "nombre": "Solo Repulsión - 30 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 30,
            "cargas": np.ones(30),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (30, 2))
        },
        {
            "id": "repulsion_07",
            "nombre": "Solo Repulsión - 35 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 35,
            "cargas": np.ones(35),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (35, 2))
        },
        {
            "id": "repulsion_08",
            "nombre": "Solo Repulsión - 40 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 40,
            "cargas": np.ones(40),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (40, 2))
        },
        {
            "id": "repulsion_09",
            "nombre": "Solo Repulsión - 50 partículas",
            "categoria": "Solo Repulsión",
            "n_particulas": 50,
            "cargas": np.ones(50),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (50, 2))
        },
        {
            "id": "repulsion_10",
            "nombre": "Solo Repulsión - Configuración circular pequeña",
            "categoria": "Solo Repulsión",
            "n_particulas": 8,
            "cargas": np.ones(8),
            "posiciones_iniciales": np.array([[5*np.cos(theta), 5*np.sin(theta)] for theta in np.linspace(0, 2*np.pi, 8, endpoint=False)])
        },
        {
            "id": "repulsion_11",
            "nombre": "Solo Repulsión - Configuración circular mediana",
            "categoria": "Solo Repulsión",
            "n_particulas": 12,
            "cargas": np.ones(12),
            "posiciones_iniciales": np.array([[7*np.cos(theta), 7*np.sin(theta)] for theta in np.linspace(0, 2*np.pi, 12, endpoint=False)])
        },
        {
            "id": "repulsion_12",
            "nombre": "Solo Repulsión - Configuración circular grande",
            "categoria": "Solo Repulsión",
            "n_particulas": 16,
            "cargas": np.ones(16),
            "posiciones_iniciales": np.array([[8.5*np.cos(theta), 8.5*np.sin(theta)] for theta in np.linspace(0, 2*np.pi, 16, endpoint=False)])
        },
        {
            "id": "repulsion_13",
            "nombre": "Solo Repulsión - Cuadrícula 3x3",
            "categoria": "Solo Repulsión",
            "n_particulas": 9,
            "cargas": np.ones(9),
            "posiciones_iniciales": np.array([[x, y] for x in np.linspace(-4, 4, 3) for y in np.linspace(-4, 4, 3)])
        },
        {
            "id": "repulsion_14",
            "nombre": "Solo Repulsión - Cuadrícula 4x4",
            "categoria": "Solo Repulsión",
            "n_particulas": 16,
            "cargas": np.ones(16),
            "posiciones_iniciales": np.array([[x, y] for x in np.linspace(-6, 6, 4) for y in np.linspace(-6, 6, 4)])
        },
        {
            "id": "repulsion_15",
            "nombre": "Solo Repulsión - Cuadrícula 5x5",
            "categoria": "Solo Repulsión",
            "n_particulas": 25,
            "cargas": np.ones(25),
            "posiciones_iniciales": np.array([[x, y] for x in np.linspace(-7, 7, 5) for y in np.linspace(-7, 7, 5)])
        },
        {
            "id": "repulsion_16",
            "nombre": "Solo Repulsión - Muy concentradas en el centro",
            "categoria": "Solo Repulsión",
            "n_particulas": 30,
            "cargas": np.ones(30),
            "posiciones_iniciales": np.random.uniform(-1.5, 1.5, (30, 2))
        },
        {
            "id": "repulsion_17",
            "nombre": "Solo Repulsión - Tres grupos separados",
            "categoria": "Solo Repulsión",
            "n_particulas": 24,
            "cargas": np.ones(24),
            "posiciones_iniciales": np.vstack([
                np.random.uniform(-8, -5, (8, 2)),
                np.random.uniform(-2, 2, (8, 2)),
                np.random.uniform(5, 8, (8, 2))
            ])
        },
        {
            "id": "repulsion_18",
            "nombre": "Solo Repulsión - Espiral",
            "categoria": "Solo Repulsión",
            "n_particulas": 15,
            "cargas": np.ones(15),
            "posiciones_iniciales": np.array([
                [2*(1 + i*0.4)*np.cos(i*0.8*np.pi), 2*(1 + i*0.4)*np.sin(i*0.8*np.pi)]
                for i in range(15)
            ])
        }
    ]
    
    #---------------------------------------------------------------------------
    # CATEGORÍA 2: ATRACCIÓN + REPULSIÓN (18 configuraciones)
    #---------------------------------------------------------------------------
    atraccion_repulsion = [
        {
            "id": "mixto_01",
            "nombre": "Atracción + Repulsión - 8 partículas (4+4)",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 8,
            "cargas": np.array([1]*4 + [-1]*4),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (8, 2))
        },
        {
            "id": "mixto_02",
            "nombre": "Atracción + Repulsión - 12 partículas (6+6)",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 12,
            "cargas": np.array([1]*6 + [-1]*6),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (12, 2))
        },
        {
            "id": "mixto_03",
            "nombre": "Atracción + Repulsión - 16 partículas (8+8)",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 16,
            "cargas": np.array([1]*8 + [-1]*8),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (16, 2))
        },
        {
            "id": "mixto_04",
            "nombre": "Atracción + Repulsión - 20 partículas (10+10)",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 20,
            "cargas": np.array([1]*10 + [-1]*10),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (20, 2))
        },
        {
            "id": "mixto_05",
            "nombre": "Atracción + Repulsión - 24 partículas (12+12)",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 24,
            "cargas": np.array([1]*12 + [-1]*12),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (24, 2))
        },
        {
            "id": "mixto_06",
            "nombre": "Atracción + Repulsión - 28 partículas (14+14)",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 28,
            "cargas": np.array([1]*14 + [-1]*14),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (28, 2))
        },
        {
            "id": "mixto_07",
            "nombre": "Atracción + Repulsión - 32 partículas (16+16)",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 32,
            "cargas": np.array([1]*16 + [-1]*16),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (32, 2))
        },
        {
            "id": "mixto_08",
            "nombre": "Atracción + Repulsión - 40 partículas (20+20)",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 40,
            "cargas": np.array([1]*20 + [-1]*20),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.8, L_DOMAIN*0.8, (40, 2))
        },
        {
            "id": "mixto_09",
            "nombre": "Atracción + Repulsión - Dipolo simple",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 2,
            "cargas": np.array([1, -1]),
            "posiciones_iniciales": np.array([[-4, 0], [4, 0]])
        },
        {
            "id": "mixto_10",
            "nombre": "Atracción + Repulsión - Cuadrantes separados",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 20,
            "cargas": np.array([1]*10 + [-1]*10),
            "posiciones_iniciales": np.vstack([
                np.random.uniform(-8, 0, (10, 2)),
                np.random.uniform(0, 8, (10, 2))
            ])
        },
        {
            "id": "mixto_11",
            "nombre": "Atracción + Repulsión - Anillos concéntricos",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 24,
            "cargas": np.array([1]*12 + [-1]*12),
            "posiciones_iniciales": np.vstack([
                np.array([[7*np.cos(theta), 7*np.sin(theta)] for theta in np.linspace(0, 2*np.pi, 12, endpoint=False)]),
                np.array([[4*np.cos(theta), 4*np.sin(theta)] for theta in np.linspace(0, 2*np.pi, 12, endpoint=False)])
            ])
        },
        {
            "id": "mixto_12",
            "nombre": "Atracción + Repulsión - Cruce de cargas",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 16,
            "cargas": np.array([1]*8 + [-1]*8),
            "posiciones_iniciales": np.array([
                [-8, -8], [-8, -4], [-8, 0], [-8, 4],
                [8, -8], [8, -4], [8, 0], [8, 4],
                [-8, 8], [-4, 8], [0, 8], [4, 8],
                [-8, -8], [-4, -8], [0, -8], [4, -8]
            ])
        },
        {
            "id": "mixto_13",
            "nombre": "Atracción + Repulsión - Configuración aleatoria",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 30,
            "cargas": np.random.choice([1, -1], size=30),
            "posiciones_iniciales": np.random.uniform(-L_DOMAIN*0.9, L_DOMAIN*0.9, (30, 2))
        },
        {
            "id": "mixto_14",
            "nombre": "Atracción + Repulsión - Tres grupos (2 positivos, 1 negativo)",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 30,
            "cargas": np.array([1]*10 + [1]*10 + [-1]*10),
            "posiciones_iniciales": np.vstack([
                np.random.uniform(-8, -4, (10, 2)),
                np.random.uniform(4, 8, (10, 2)),
                np.random.uniform(-2, 2, (10, 2))
            ])
        },
        {
            "id": "mixto_15",
            "nombre": "Atracción + Repulsión - Cuadrícula chessboard",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 16,
            "cargas": np.array([1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, -1, 1, -1, 1]),
            "posiciones_iniciales": np.array([[x, y] for x in np.linspace(-6, 6, 4) for y in np.linspace(-6, 6, 4)])
        },
        {
            "id": "mixto_16",
            "nombre": "Atracción + Repulsión - Espirales opuestas",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 20,
            "cargas": np.array([1]*10 + [-1]*10),
            "posiciones_iniciales": np.vstack([
                np.array([
                    [2*(1 + i*0.3)*np.cos(i*0.6*np.pi), 2*(1 + i*0.3)*np.sin(i*0.6*np.pi)]
                    for i in range(10)
                ]),
                np.array([
                    [-2*(1 + i*0.3)*np.cos(i*0.6*np.pi), -2*(1 + i*0.3)*np.sin(i*0.6*np.pi)]
                    for i in range(10)
                ])
            ])
        },
        {
            "id": "mixto_17",
            "nombre": "Atracción + Repulsión - Líneas paralelas",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 20,
            "cargas": np.array([1]*10 + [-1]*10),
            "posiciones_iniciales": np.vstack([
                np.array([[x, -5] for x in np.linspace(-7, 7, 10)]),
                np.array([[x, 5] for x in np.linspace(-7, 7, 10)])
            ])
        },
        {
            "id": "mixto_18",
            "nombre": "Atracción + Repulsión - Anillos de cargas alternadas",
            "categoria": "Atracción + Repulsión",
            "n_particulas": 20,
            "cargas": np.array([1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1]),
            "posiciones_iniciales": np.array([[7.5*np.cos(theta), 7.5*np.sin(theta)] for theta in np.linspace(0, 2*np.pi, 20, endpoint=False)])
        }
    ]
    
    print(f"  Total configuraciones: {len(solo_repulsion) + len(atraccion_repulsion)}")
    print(f"    - Solo Repulsión: {len(solo_repulsion)}")
    print(f"    - Atracción + Repulsión: {len(atraccion_repulsion)}")
    
    return solo_repulsion, atraccion_repulsion


#===============================================================================
# SIMULACIÓN SIMPLIFICADA PARA ANIMACIÓN
#===============================================================================

def simular_movimiento(posiciones_iniciales: np.ndarray, cargas: np.ndarray, num_frames: int) -> List[np.ndarray]:
    """
    Simula el movimiento de las cargas de forma simplificada para la animación.
    Ajusta la velocidad para que el movimiento sea claro y lento.
    """
    posiciones = posiciones_iniciales.astype(float).copy()
    frames = [posiciones.copy()]
    
    for _ in range(num_frames - 1):
        # Calcular fuerzas entre todas las partículas (simplificado)
        fuerzas = np.zeros_like(posiciones)
        
        for i in range(len(posiciones)):
            for j in range(len(posiciones)):
                if i != j:
                    r = posiciones[j] - posiciones[i]
                    dist = np.linalg.norm(r)
                    if dist > 0.1:
                        # Fuerza de Coulomb simplificada
                        fuerza = cargas[i] * cargas[j] * r / (dist**3)
                        # Escalar para velocidad controlada
                        fuerzas[i] += fuerza * 0.5
        
        # Actualizar posiciones con velocidad controlada
        posiciones += fuerzas * 0.08
        
        # Aplicar límites del dominio
        posiciones = np.clip(posiciones, -L_DOMAIN*0.95, L_DOMAIN*0.95)
        
        frames.append(posiciones.copy())
    
    return frames


#===============================================================================
# GENERACIÓN DE FRAMES Y VIDEO
#===============================================================================

def generar_frame(posiciones: np.ndarray, cargas: np.ndarray, config: Dict, frame_num: int, total_frames: int) -> str:
    """
    Genera un frame individual para el video.
    """
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
    
    # Separar cargas positivas y negativas
    pos_mask = cargas > 0
    neg_mask = cargas < 0
    
    # Plotear cargas
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
    
    # Configurar ejes
    margin = L_DOMAIN * 0.08
    ax.set_xlim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_ylim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_aspect('equal')
    
    # Dibujar dominio
    rect = plt.Rectangle(
        (-L_DOMAIN, -L_DOMAIN), 2*L_DOMAIN, 2*L_DOMAIN,
        fill=False, edgecolor='#58A6FF', linewidth=1.5,
        linestyle='--', alpha=0.6
    )
    ax.add_patch(rect)
    
    # Malla
    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')
    
    # Rotar etiquetas del eje X para evitar superposicion y reducir tamaño de fuente
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
    
    # Título y etiquetas
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('y', fontsize=11)
    ax.set_title(config["nombre"], fontsize=13, fontweight='bold', pad=10)
    
    # Información en la esquina
    info = f"Categoría: {config['categoria']}\n"
    info += f"Partículas: {config['n_particulas']}\n"
    info += f"Frame: {frame_num+1}/{total_frames}"
    
    ax.text(
        0.02, 0.98, info, transform=ax.transAxes, fontsize=7,
        verticalalignment='top', color='#000000', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFFFF', edgecolor='#333333', alpha=0.9)
    )
    
    # Leyenda
    ax.legend(loc='upper right', fontsize=7, framealpha=0.8, facecolor='#FFFFFF', edgecolor='#333333')
    
    plt.tight_layout()
    
    # Guardar frame
    frame_path = OUTPUT_VIDEOS_DIR / f"temp_frame_{frame_num:06d}.png"
    fig.savefig(frame_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    
    return str(frame_path)


def generar_video_configuracion(config: Dict) -> Path:
    """
    Genera un video completo para una configuración específica.
    """
    print(f"\n  Generando video: {config['nombre']}")
    
    # Simular movimiento
    frames_posiciones = simular_movimiento(
        config["posiciones_iniciales"],
        config["cargas"],
        NUM_FRAMES
    )
    
    # Generar frames
    frame_paths = []
    for i, posiciones in enumerate(frames_posiciones):
        frame_path = generar_frame(posiciones, config["cargas"], config, i, NUM_FRAMES)
        frame_paths.append(frame_path)
        if (i+1) % 5 == 0 or i == NUM_FRAMES - 1:
            print(f"    Frame {i+1}/{NUM_FRAMES}")
    
    # Ensamblar video
    print(f"  Ensamblando video ({FPS:.1f} FPS)...")
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
    
    # Limpiar frames temporales
    for fp in frame_paths:
        Path(fp).unlink()
    
    print(f"  ✅ Video generado: {video_path}")
    return video_path


#===============================================================================
# FUNCIÓN PRINCIPAL
#===============================================================================

def main():
    """
    Función principal: genera todos los videos.
    """
    print("\n" + "="*80)
    print("  GENERACIÓN DE VIDEOS ESPECIALES DE SIMULACIÓN")
    print("="*80)
    print(f"\n  Parámetros técnicos:")
    print(f"    Frames por video: {NUM_FRAMES}")
    print(f"    Duración: {VIDEO_DURATION} segundos")
    print(f"    FPS: {FPS:.1f}")
    print(f"    Directorio de salida: {OUTPUT_VIDEOS_DIR}")
    
    # Definir configuraciones
    solo_repulsion, atraccion_repulsion = definir_configuraciones()
    
    # Generar videos de categoría 1: Solo Repulsión
    print("\n" + "="*80)
    print("  CATEGORÍA 1: SOLO REPULSIÓN")
    print("="*80)
    
    for config in solo_repulsion:
        generar_video_configuracion(config)
    
    # Generar videos de categoría 2: Atracción + Repulsión
    print("\n" + "="*80)
    print("  CATEGORÍA 2: ATRACCIÓN + REPULSIÓN")
    print("="*80)
    
    for config in atraccion_repulsion:
        generar_video_configuracion(config)
    
    # Resumen final
    total_videos = len(solo_repulsion) + len(atraccion_repulsion)
    print("\n" + "="*80)
    print("  RESUMEN FINAL")
    print("="*80)
    print(f"  Total videos generados: {total_videos}")
    print(f"  Videos de Solo Repulsión: {len(solo_repulsion)}")
    print(f"  Videos de Atracción + Repulsión: {len(atraccion_repulsion)}")
    print(f"  Directorio de salida: {OUTPUT_VIDEOS_DIR}")
    print("\n  ✅ Todos los videos han sido generados exitosamente!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

