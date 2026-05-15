"""
plot_energy.py — Gráfica de energía vs iteración

Genera visualización de la evolución temporal de la energía electrostática
U(t) en función de las iteraciones aceptadas, mostrando:
- Tendencia decreciente monótona
- Convergencia hacia un mínimo
- Tasa de aceptación

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from config import (setup_matplotlib, ensure_dirs, FIGURES_DIR,
                    COLOR_ENERGY, DPI, FIGURE_SIZE)
from data_loader import load_energy_log


def plot_energy_vs_iteration():
    """
    Genera gráfica principal de U(t) vs iteración aceptada.
    Muestra la convergencia energética del sistema.
    """
    print("\n  ")
    print("  GENERANDO GRÁFICA DE ENERGÍA")
    print("  \n")
    
    df = load_energy_log()
    
    iterations = df['accepted_count'].values
    energy = df['energy'].values
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    
    # Curva principal de energía
    ax.plot(iterations, energy, color=COLOR_ENERGY, linewidth=1.2,
            alpha=0.9, label='Energía total U')
    
    # Rellenar debajo de la curva para efecto visual
    ax.fill_between(iterations, energy, energy.min() * 1.1,
                    color=COLOR_ENERGY, alpha=0.08)
    
    # Marcar energía inicial y final
    ax.axhline(y=energy[0], color='#FF6B6B', linestyle=':', alpha=0.4,
               linewidth=0.8, label=f'U₀ = {energy[0]:.2f}')
    ax.axhline(y=energy[-1], color='#51CF66', linestyle=':', alpha=0.4,
               linewidth=0.8, label=f'U_final = {energy[-1]:.2f}')
    
    # Punto inicial y final
    ax.scatter([iterations[0]], [energy[0]], color='#FF6B6B', s=60,
               zorder=10, edgecolors='white', linewidths=0.5)
    ax.scatter([iterations[-1]], [energy[-1]], color='#51CF66', s=60,
               zorder=10, edgecolors='white', linewidths=0.5)
    
    # Etiquetas
    ax.set_xlabel('Movimientos Aceptados', fontsize=13)
    ax.set_ylabel('Energía Electrostática U', fontsize=13)
    ax.set_title('Convergencia de la Energía Electrostática',
                 fontsize=15, fontweight='bold', pad=12)
    
    ax.grid(True, alpha=0.2)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.8,
              facecolor='#161B22', edgecolor='#30363D')
    
    # Anotación de reducción
    reduction = ((energy[0] - energy[-1]) / abs(energy[0])) * 100
    ax.text(0.5, 0.95, f'Reducción: {reduction:.1f}%',
            transform=ax.transAxes, fontsize=12, ha='center',
            color='#51CF66', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#161B22',
                      edgecolor='#30363D', alpha=0.9))
    
    plt.tight_layout()
    filepath = FIGURES_DIR / 'energy_vs_iteration.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Gráfica de energía guardada: {filepath}")


def plot_energy_log_scale():
    """Gráfica de energía en escala logarítmica para apreciar convergencia."""
    df = load_energy_log()
    
    iterations = df['accepted_count'].values
    energy = df['energy'].values
    
    # Solo funciona si la energía es positiva (cargas iguales)
    if np.all(energy > 0):
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        ax.semilogy(iterations, energy, color='#A78BFA', linewidth=1.2,
                    alpha=0.9, label='U (escala log)')
        
        ax.set_xlabel('Movimientos Aceptados', fontsize=13)
        ax.set_ylabel('Energía U (escala log)', fontsize=13)
        ax.set_title('Convergencia Energética — Escala Logarítmica',
                     fontsize=15, fontweight='bold', pad=12)
        ax.grid(True, alpha=0.2, which='both')
        ax.legend(loc='upper right', fontsize=10, framealpha=0.8,
                  facecolor='#161B22', edgecolor='#30363D')
        
        plt.tight_layout()
        filepath = FIGURES_DIR / 'energy_log_scale.png'
        fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"   Gráfica log-scale guardada: {filepath}")
    else:
        print("   Energía contiene valores negativos — log-scale omitido")


def plot_acceptance_rate():
    """Gráfica de tasa de aceptación a lo largo de la simulación."""
    df = load_energy_log()
    
    iterations = df['iteration'].values
    rate = df['acceptance_rate'].values
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    
    ax.plot(iterations, rate * 100, color='#22D3EE', linewidth=1.0,
            alpha=0.8, label='Tasa de aceptación')
    
    ax.set_xlabel('Iteración', fontsize=13)
    ax.set_ylabel('Tasa de Aceptación (%)', fontsize=13)
    ax.set_title('Evolución de la Tasa de Aceptación',
                 fontsize=15, fontweight='bold', pad=12)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.2)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.8,
              facecolor='#161B22', edgecolor='#30363D')
    
    plt.tight_layout()
    filepath = FIGURES_DIR / 'acceptance_rate.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Tasa de aceptación guardada: {filepath}")


def generate_energy_plots():
    """Pipeline principal de gráficas de energía."""
    plot_energy_vs_iteration()
    plot_energy_log_scale()
    plot_acceptance_rate()


if __name__ == '__main__':
    setup_matplotlib()
    ensure_dirs()
    generate_energy_plots()
