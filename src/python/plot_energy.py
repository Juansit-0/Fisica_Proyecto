"""
plot_energy.py — Gráfica de energía vs iteración (estilo original limpio)

Genera la visualización de U(t) de la evolución temporal de la energía
electrostática en función de los movimientos aceptados.

Estilo:
    - Curva única color COLOR_ENERGY con sombra bajo la curva.
    - Líneas punteadas U₀ (rojo) y U_final (verde) con valores en leyenda.
    - Marcadores en los puntos inicial y final.
    - Etiqueta central "Reducción: X.X %".
    - Eje X autoescalado a los datos reales.

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from config import (setup_matplotlib, ensure_dirs, FIGURES_DIR,
                    COLOR_ENERGY, DPI, FIGURE_SIZE,
                    ENERGY_PLOT_X_MIN, ENERGY_PLOT_X_MAX,
                    ENERGY_PLOT_Y_MIN, ENERGY_PLOT_Y_MAX,
                    ENERGY_PLOT_Y_MIN_MIXED, ENERGY_PLOT_Y_MAX_MIXED,
                    ENERGY_PLOT_X_MAJOR_STEP, ENERGY_PLOT_X_MINOR_STEP,
                    ENERGY_PLOT_Y_MAJOR_STEP, ENERGY_PLOT_Y_MAJOR_STEP_MIXED,
                    ENERGY_PLOT_Y_MINOR_SUBDIV,
                    ENERGY_PLOT_Y_AUTOFIT_MIXED,
                    CHARGE_MODE)
from data_loader import load_energy_log


def _resolve_y_axis(energy_values):
    """
    Devuelve (y_min, y_max, y_major_step) según el modo de carga
    detectado en config.CHARGE_MODE.
        - CHARGE_MODE=1 (repulsión): rango fijo positivo Y_MIN..Y_MAX.
        - CHARGE_MODE=2 (mixto):     rango fijo MIXED, opcionalmente
          ampliado a múltiplos de Y_MAJOR_STEP_MIXED si los datos lo
          exceden (ENERGY_PLOT_Y_AUTOFIT_MIXED=True).
    """
    if CHARGE_MODE == 2:
        y_lo = float(ENERGY_PLOT_Y_MIN_MIXED)
        y_hi = float(ENERGY_PLOT_Y_MAX_MIXED)
        step = float(ENERGY_PLOT_Y_MAJOR_STEP_MIXED)
        if ENERGY_PLOT_Y_AUTOFIT_MIXED and len(energy_values) > 0:
            y_data_min = float(energy_values.min())
            y_data_max = float(energy_values.max())
            # Si los datos exceden los límites fijos, ampliarlos a un
            # múltiplo redondo del paso mayor.
            if y_data_min < y_lo:
                y_lo = float(np.floor(y_data_min / step) * step)
            if y_data_max > y_hi:
                y_hi = float(np.ceil(y_data_max / step) * step)
        return y_lo, y_hi, step
    # Modo 1 (repulsión): rango fijo original
    return (float(ENERGY_PLOT_Y_MIN),
             float(ENERGY_PLOT_Y_MAX),
             float(ENERGY_PLOT_Y_MAJOR_STEP))


def _pick_y_tick_step(y_range: float) -> float:
    """
    Elige el paso del eje Y para tener una rejilla fina pero legible.

    Objetivo: ~30-40 ticks principales en pasos "redondos"
    (1, 2, 5, 10, 20, 50, 100, ...). Se elige el paso *más cercano*
    al ideal (no el siguiente "redondo" superior), permitiendo que el
    eje quede más denso cuando el rango cae justo encima de un paso.
    """
    target_ticks = 30
    raw = y_range / target_ticks
    if raw <= 0:
        return 1.0
    exp = np.floor(np.log10(raw))
    base = 10 ** exp
    nice_steps = np.array([1, 2, 5, 10]) * base
    # Paso "redondo" más cercano al ideal, en lugar de redondear arriba.
    idx = int(np.argmin(np.abs(nice_steps - raw)))
    return float(nice_steps[idx])


def plot_energy_vs_iteration():
    """
    Gráfica principal de U(t) vs movimiento aceptado.
    Muestra la convergencia energética del sistema con el estilo
    original limpio: una sola curva, marcadores U₀ y U_final, y la
    anotación de reducción porcentual centrada arriba.
    """
    print("\n  ")
    print("  GENERANDO GRÁFICA DE ENERGÍA")
    print("  \n")

    df = load_energy_log()
    iterations = df['accepted_count'].values
    energy = df['energy'].values

    print(f"  Puntos en el log: {len(iterations)}")
    print(f"  Rango accepted_count: {iterations.min()} .. {iterations.max()}")

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # Curva principal de energía
    ax.plot(iterations, energy, color=COLOR_ENERGY, linewidth=1.2,
             alpha=0.9, label='Energía total U')

    # Rellenar debajo de la curva para efecto visual
    y_floor = float(energy.min()) - 0.05 * abs(float(energy.min()))
    ax.fill_between(iterations, energy, y_floor,
                     color=COLOR_ENERGY, alpha=0.08)

    # Marcar energía inicial y final
    ax.axhline(y=energy[0], color='#FF6B6B', linestyle=':', alpha=0.4,
                linewidth=0.8, label=f'U₀ = {energy[0]:.2f}')
    ax.axhline(y=energy[-1], color='#51CF66', linestyle=':', alpha=0.4,
                linewidth=0.8, label=f'U_final = {energy[-1]:.2f}')

    # Puntos inicial y final
    ax.scatter([iterations[0]], [energy[0]], color='#FF6B6B', s=60,
                zorder=10, edgecolors='black', linewidths=0.5)
    ax.scatter([iterations[-1]], [energy[-1]], color='#51CF66', s=60,
                zorder=10, edgecolors='black', linewidths=0.5)

    # Etiquetas
    ax.set_xlabel('Movimientos Aceptados', fontsize=13)
    ax.set_ylabel('Energía Electrostática U', fontsize=13)
    ax.set_title('Convergencia de la Energía Electrostática',
                  fontsize=15, fontweight='bold', pad=12)

    # Eje X autoescalado a los datos (estilo batch original)
    ax.set_xlim(0, float(iterations.max()) * 1.02)

    # Eje Y autoescalado al rango con holgura pequeña arriba/abajo.
    # En modo mixto puede incluir valores negativos automáticamente.
    y_data_min = float(energy.min())
    y_data_max = float(energy.max())
    y_pad = (y_data_max - y_data_min) * 0.04
    if y_pad < 1e-9:
        y_pad = 1.0
    ax.set_ylim(y_data_min - y_pad, y_data_max + y_pad)

    # Línea de referencia U = 0 si el rango cruza el cero (modo mixto)
    if y_data_min < 0 < y_data_max:
        ax.axhline(y=0.0, color='#1D3557', linestyle='--', alpha=0.5,
                    linewidth=1.0, label='U = 0', zorder=4)

    # Cuadrícula simple (estilo original del batch)
    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')
    ax.legend(loc='upper right', fontsize=9, framealpha=0.8,
               facecolor='#FFFFFF', edgecolor='#333333')

    # Anotación central de reducción porcentual
    # Cambio energético. En modo mixto U₀ puede ser ≈ 0 (cargas
    # opuestas se cancelan al inicio) y el % de reducción explota.
    # En ese caso mostramos ΔU absoluto en lugar de porcentual.
    delta_u = energy[0] - energy[-1]
    if CHARGE_MODE == 2 and abs(energy[0]) < 5.0:
        delta_label = f'ΔU = {delta_u:.2f}'
    else:
        reduction = (delta_u / abs(energy[0])) * 100
        delta_label = f'Reducción: {reduction:.1f}%'
    ax.text(0.5, 0.95, delta_label,
             transform=ax.transAxes, fontsize=12, ha='center',
             color='#51CF66', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFFFF',
                       edgecolor='#333333', alpha=0.9))

    plt.tight_layout()
    filepath = FIGURES_DIR / 'energy_vs_iteration.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                 facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Gráfica de energía guardada: {filepath}")
    print(f"   Eje X autoescalado: 0 → {float(iterations.max()):.0f} "
          f"movimientos aceptados")


def plot_energy_log_scale():
    """Gráfica en escala log de la energía (si es positiva)."""
    df = load_energy_log()
    iterations = df['accepted_count'].values
    energy = df['energy'].values

    if not np.all(energy > 0):
        print("   Energía contiene valores negativos — log-scale omitido")
        return

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    ax.semilogy(iterations, energy, color='#A78BFA', linewidth=1.2,
                  alpha=0.9, label='U (escala log)')

    ax.set_xlabel('Movimientos Aceptados', fontsize=13)
    ax.set_ylabel('Energía U (escala log)', fontsize=13)
    ax.set_title('Convergencia Energética — Escala Logarítmica',
                  fontsize=15, fontweight='bold', pad=12)
    # Eje X autoescalado a los datos
    ax.set_xlim(0, float(iterations.max()) * 1.02)
    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-',
             which='both')
    ax.legend(loc='upper right', fontsize=9, framealpha=0.8,
               facecolor='#FFFFFF', edgecolor='#333333')

    plt.tight_layout()
    filepath = FIGURES_DIR / 'energy_log_scale.png'
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight',
                 facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   Gráfica log-scale guardada: {filepath}")


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
    ax.set_xlim(0, float(iterations.max()) * 1.02)
    ax.set_ylim(0, max(100, float(np.max(rate * 100)) * 1.1))
    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')
    ax.legend(loc='upper right', fontsize=9, framealpha=0.8,
               facecolor='#FFFFFF', edgecolor='#333333')

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
