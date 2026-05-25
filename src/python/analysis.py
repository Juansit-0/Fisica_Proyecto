"""
analysis.py — Análisis estadístico y físico de la simulación

Análisis de:
- Histogramas de energía comparando múltiples configuraciones
- Distribución de energías durante la simulación
- Estadísticas de convergencia
- Resumen del sistema

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import (setup_matplotlib, ensure_dirs, FIGURES_DIR,
                    L_DOMAIN, DPI, FIGURE_SIZE, MATPLOTLIB_STYLE)
from data_loader import (load_energy_log, load_initial_configuration,
                          load_final_configuration, load_all_configurations, get_positions_and_charges)


def compute_total_energy(x, y, q, epsilon=1e-2):
    """Calcula la energía total del sistema para una configuración."""
    n = len(x)
    U = 0.0
    for i in range(n - 1):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            r = np.sqrt(dx*dx + dy*dy + epsilon*epsilon)
            U += q[i] * q[j] / r
    return U


def plot_energy_comparison_histogram():
    """Histograma de energías comparando múltiples configuraciones (10 + final)."""
    plt.rcParams.update(MATPLOTLIB_STYLE)
    
    configs = load_all_configurations()
    
    num_configs = len(configs)
    step = max(1, num_configs // 10)  # Tomar 10 configuraciones + final
    selected_configs = configs[::step]
    if len(selected_configs) > 10:
        selected_configs = selected_configs[:10]
    # Asegurar que la configuración final está incluida
    if configs[-1] not in selected_configs:
        selected_configs.append(configs[-1])
    
    energies = []
    labels = []
    
    for (num, df) in selected_configs:
        x, y, q = get_positions_and_charges(df)
        U = compute_total_energy(x, y, q)
        energies.append(U)
        labels.append(f'Config {num}')
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    colors = plt.cm.viridis(np.linspace(0, 1, len(energies)))
    
    bars = ax.bar(labels, energies, color=colors, edgecolor='white', linewidth=1)
    
    ax.set_xlabel('Configuración', fontsize=13)
    ax.set_ylabel('Energía total U', fontsize=13)
    ax.set_title('Comparación de Energías — Múltiples Configuraciones',
                 fontsize=15, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')
    
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    filepath = FIGURES_DIR / 'energy_comparison_histogram.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Histograma de comparación de energías: {filepath}")


def plot_energy_distribution():
    """Distribución de energías durante la simulación."""
    plt.rcParams.update(MATPLOTLIB_STYLE)
    
    df_energy = load_energy_log()
    energies = df_energy['energy'].values
    n_total = len(energies)
    
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    n, bins, patches = ax.hist(energies, bins=30, alpha=0.7, color='#51CF66',
                                edgecolor='white', linewidth=0.5)
    
    # Convertir a porcentaje
    n_percent = (n / n_total) * 100
    ax.clear()
    ax.bar(bins[:-1], n_percent, width=np.diff(bins), alpha=0.7, color='#51CF66',
           edgecolor='white', linewidth=0.5)
    
    ax.set_xlabel('Energía total U', fontsize=13)
    ax.set_ylabel('Frecuencia (%)', fontsize=13)
    ax.set_title('Distribución de Energías Durante la Simulación',
                 fontsize=15, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')
    
    # Rotar etiquetas del eje X para evitar superposicion y reducir tamaño de fuente
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
    
    plt.tight_layout()
    filepath = FIGURES_DIR / 'energy_distribution.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Distribución de energías: {filepath}")


def print_summary_statistics():
    """Imprime resumen estadístico completo."""
    print("\n  ")
    print("  RESUMEN ESTADÍSTICO")
    print("  \n")

    df_energy = load_energy_log()
    df_f = load_final_configuration()
    xf, yf, qf = get_positions_and_charges(df_f)

    e_init = df_energy['energy'].iloc[0]
    e_final = df_energy['energy'].iloc[-1]
    reduction = (e_init - e_final) / abs(e_init) * 100

    print(f"  Energía inicial:    {e_init:.6f}")
    print(f"  Energía final:      {e_final:.6f}")
    print(f"  Reducción:          {reduction:.2f}%")
    print(f"  Cargas +1:          {np.sum(qf > 0)}")
    print(f"  Cargas -1:          {np.sum(qf < 0)}")
    print()


def generate_analysis():
    """Pipeline principal de análisis."""
    print("\n  ")
    print("  GENERANDO ANÁLISIS ESTADÍSTICO")
    print("  \n")
    print_summary_statistics()
    plot_energy_comparison_histogram()
    plot_energy_distribution()


if __name__ == '__main__':
    setup_matplotlib()
    ensure_dirs()
    generate_analysis()
