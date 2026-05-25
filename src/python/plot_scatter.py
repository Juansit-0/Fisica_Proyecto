"""
plot_scatter.py — Scatter plots de configuraciones de cargas

Genera visualizaciones de la distribución espacial de cargas:
- Configuración inicial
- Configuración final
- Comparación lado a lado (initial vs final)

Convención de colores (del PDF del proyecto):
- Rojo: carga positiva (+1)
- Azul: carga negativa (-1)

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib.pyplot as plt
from config import (setup_matplotlib, ensure_dirs, FIGURES_DIR,
                    COLOR_POSITIVE, COLOR_NEGATIVE, MARKER_SIZE,
                    MARKER_EDGE_COLOR, MARKER_EDGE_WIDTH,
                    L_DOMAIN, GRID_RESOLUTION, DPI, FIGURE_SIZE_WIDE, FIGURE_SIZE_SQUARE)
from data_loader import (load_initial_configuration, load_final_configuration,
                          get_positions_and_charges)


def plot_single_configuration(df, title, filename, energy=None):
    """
    Genera scatter plot de una configuración individual.
    
    Args:
        df: DataFrame con columnas x, y, charge
        title: título del gráfico
        filename: nombre del archivo de salida (sin ruta)
        energy: energía total (opcional, para mostrar en el gráfico)
    """
    x, y, q = get_positions_and_charges(df)
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SQUARE)
    
    # Separar cargas positivas y negativas
    pos_mask = q > 0
    neg_mask = q < 0
    
    # Scatter de cargas positivas
    if np.any(pos_mask):
        ax.scatter(x[pos_mask], y[pos_mask],
                   c=COLOR_POSITIVE, s=MARKER_SIZE,
                   edgecolors=MARKER_EDGE_COLOR,
                   linewidths=MARKER_EDGE_WIDTH,
                   label=f'+1 ({np.sum(pos_mask)} cargas)',
                   zorder=5, alpha=0.9)
    
    # Scatter de cargas negativas
    if np.any(neg_mask):
        ax.scatter(x[neg_mask], y[neg_mask],
                   c=COLOR_NEGATIVE, s=MARKER_SIZE,
                   edgecolors=MARKER_EDGE_COLOR,
                   linewidths=MARKER_EDGE_WIDTH,
                   label=f'−1 ({np.sum(neg_mask)} cargas)',
                   zorder=5, alpha=0.9, marker='s')
    
    # Dominio fijo [-L, L]
    margin = L_DOMAIN * 0.08
    ax.set_xlim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_ylim(-L_DOMAIN - margin, L_DOMAIN + margin)
    ax.set_aspect('equal')
    
    # Bordes del dominio
    rect = plt.Rectangle((-L_DOMAIN, -L_DOMAIN), 2*L_DOMAIN, 2*L_DOMAIN,
                          fill=False, edgecolor='#58A6FF', linewidth=1.5,
                          linestyle='--', alpha=0.6)
    ax.add_patch(rect)
    
    # Etiquetas y título
    ax.set_xlabel('x', fontsize=13)
    ax.set_ylabel('y', fontsize=13)
    ax.set_title(title, fontsize=15, fontweight='bold', pad=12)
    
    # Configurar ticks de malla basados en GRID_RESOLUTION
    grid_spacing = (2.0 * L_DOMAIN) / (GRID_RESOLUTION - 1)
    ticks = np.arange(-L_DOMAIN, L_DOMAIN + grid_spacing, grid_spacing)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')
    ax.legend(loc='upper right', fontsize=9, framealpha=0.8,
              facecolor='#FFFFFF', edgecolor='#333333')
    
    # Rotar etiquetas del eje X para evitar superposicion y reducir tamaño de fuente
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
    
    # Mostrar energía si se proporciona
    if energy is not None:
        ax.text(0.02, 0.02, f'U = {energy:.4f}',
                transform=ax.transAxes, fontsize=11,
                color='#000000', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFFFF',
                          edgecolor='#333333', alpha=0.9))
    
    plt.tight_layout()
    filepath = FIGURES_DIR / filename
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Gráfica guardada: {filepath}")


def plot_comparison(df_initial, df_final, energy_initial=None, energy_final=None):
    """
    Genera comparación lado a lado: configuración inicial vs final.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIGURE_SIZE_WIDE)
    
    for ax, df, title, energy in [
        (ax1, df_initial, 'Configuración Inicial', energy_initial),
        (ax2, df_final, 'Configuración Final (Mínima Energía)', energy_final)
    ]:
        x, y, q = get_positions_and_charges(df)
        
        pos_mask = q > 0
        neg_mask = q < 0
        
        if np.any(pos_mask):
            ax.scatter(x[pos_mask], y[pos_mask],
                       c=COLOR_POSITIVE, s=MARKER_SIZE * 0.8,
                       edgecolors=MARKER_EDGE_COLOR,
                       linewidths=MARKER_EDGE_WIDTH,
                       label='+1', zorder=5, alpha=0.9)
        
        if np.any(neg_mask):
            ax.scatter(x[neg_mask], y[neg_mask],
                       c=COLOR_NEGATIVE, s=MARKER_SIZE * 0.8,
                       edgecolors=MARKER_EDGE_COLOR,
                       linewidths=MARKER_EDGE_WIDTH,
                       label='−1', zorder=5, alpha=0.9, marker='s')
        
        margin = L_DOMAIN * 0.08
        ax.set_xlim(-L_DOMAIN - margin, L_DOMAIN + margin)
        ax.set_ylim(-L_DOMAIN - margin, L_DOMAIN + margin)
        ax.set_aspect('equal')
        
        rect = plt.Rectangle((-L_DOMAIN, -L_DOMAIN), 2*L_DOMAIN, 2*L_DOMAIN,
                              fill=False, edgecolor='#58A6FF', linewidth=1.5,
                              linestyle='--', alpha=0.6)
        ax.add_patch(rect)
        
        ax.set_xlabel('x', fontsize=5)
        ax.set_ylabel('y', fontsize=5)
        ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
        
        # Configurar ticks de malla basados en GRID_RESOLUTION
        grid_spacing = (2.0 * L_DOMAIN) / (GRID_RESOLUTION - 1)
        ticks = np.arange(-L_DOMAIN, L_DOMAIN + grid_spacing, grid_spacing)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')
        ax.legend(loc='upper right', fontsize=9, framealpha=0.8,
                  facecolor='#FFFFFF', edgecolor='#333333')
        
        # Rotar etiquetas del eje X para evitar superposicion y reducir tamaño de fuente
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=5)
        plt.setp(ax.get_yticklabels(), fontsize=5)
        
        if energy is not None:
            ax.text(0.02, 0.02, f'U = {energy:.4f}',
                    transform=ax.transAxes, fontsize=9,
                    color='#000000', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFFFF',
                              edgecolor='#333333', alpha=0.9))
    
    fig.suptitle('Evolución del Sistema de Cargas Electrostáticas',
                 fontsize=16, fontweight='bold', y=1.02, color='#000000')
    
    plt.tight_layout()
    filepath = FIGURES_DIR / 'comparison_initial_vs_final.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Comparación guardada: {filepath}")


def generate_scatter_plots():
    """Pipeline principal de scatter plots."""
    print("\n  ")
    print("  GENERANDO SCATTER PLOTS")
    print("  \n")
    
    # Cargar datos
    df_initial = load_initial_configuration()
    df_final = load_final_configuration()
    
    # Calcular energías para anotación
    from data_loader import load_energy_log
    energy_df = load_energy_log()
    e_initial = energy_df['energy'].iloc[0]
    e_final = energy_df['energy'].iloc[-1]
    
    # Gráficas individuales
    plot_single_configuration(df_initial, 'Configuración Inicial',
                              'scatter_initial.png', energy=e_initial)
    plot_single_configuration(df_final, 'Configuración Final — Mínima Energía',
                              'scatter_final.png', energy=e_final)
    
    # Comparación
    plot_comparison(df_initial, df_final, e_initial, e_final)


if __name__ == '__main__':
    setup_matplotlib()
    ensure_dirs()
    generate_scatter_plots()
