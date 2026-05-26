"""
plot_batch_comparison.py — Comparación de curvas U(t) entre simulaciones
=========================================================================

Carga los `energy_log.csv` de todas las simulaciones de un batch
(generado por `run_comparison_batch.py`) y produce:

    - Una figura con las N curvas U(t) superpuestas, coloreadas con un
      colormap perceptual.
    - La media e intervalo ±1σ entre simulaciones, interpolados a una
      malla común de `accepted_count`.
    - Tabla con estadísticas por simulación: U₀, U_final, ΔU, % reducción.
    - Resumen agregado: media/std/min/max de U_final y % reducción.

Diseño: módulo standalone reutilizable desde la GUI y desde scripts CLI.
Mantiene el estilo gráfico del resto del proyecto (matplotlib, paleta
del config.py, eje Y con intervalos finos via _pick_y_tick_step).

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

from config import (FIGURE_SIZE, DPI, MATPLOTLIB_STYLE,
                    COLOR_POSITIVE, COLOR_NEGATIVE,
                    ENERGY_PLOT_X_MIN, ENERGY_PLOT_X_MAX,
                    ENERGY_PLOT_Y_MIN, ENERGY_PLOT_Y_MAX,
                    ENERGY_PLOT_Y_MIN_MIXED, ENERGY_PLOT_Y_MAX_MIXED,
                    ENERGY_PLOT_X_MAJOR_STEP, ENERGY_PLOT_X_MINOR_STEP,
                    ENERGY_PLOT_Y_MAJOR_STEP, ENERGY_PLOT_Y_MAJOR_STEP_MIXED,
                    ENERGY_PLOT_Y_MINOR_SUBDIV,
                    ENERGY_PLOT_Y_AUTOFIT_MIXED,
                    CHARGE_MODE)


def _resolve_y_axis_for_batch(energies_concat):
    """Mismo criterio que plot_energy: rango Y según CHARGE_MODE."""
    if CHARGE_MODE == 2:
        y_lo = float(ENERGY_PLOT_Y_MIN_MIXED)
        y_hi = float(ENERGY_PLOT_Y_MAX_MIXED)
        step = float(ENERGY_PLOT_Y_MAJOR_STEP_MIXED)
        if ENERGY_PLOT_Y_AUTOFIT_MIXED and energies_concat.size > 0:
            dmin, dmax = float(energies_concat.min()), float(energies_concat.max())
            if dmin < y_lo:
                y_lo = float(np.floor(dmin / step) * step)
            if dmax > y_hi:
                y_hi = float(np.ceil(dmax / step) * step)
        return y_lo, y_hi, step
    return (float(ENERGY_PLOT_Y_MIN),
             float(ENERGY_PLOT_Y_MAX),
             float(ENERGY_PLOT_Y_MAJOR_STEP))


# Paleta para hasta 30 simulaciones, con suficiente contraste para
# distinguir al menos 15 trayectorias a simple vista.
DEFAULT_CMAP = 'turbo'


def _pick_y_tick_step(y_range: float, target_ticks: int = 30) -> float:
    """Paso 'redondo' (1/2/5/10/...) más cercano al ideal."""
    if y_range <= 0:
        return 1.0
    raw = y_range / target_ticks
    exp = np.floor(np.log10(raw))
    base = 10 ** exp
    nice_steps = np.array([1, 2, 5, 10]) * base
    idx = int(np.argmin(np.abs(nice_steps - raw)))
    return float(nice_steps[idx])


def discover_batches(comparison_root: Path) -> List[Path]:
    """Devuelve la lista de batches detectados, ordenada del más
    reciente al más antiguo."""
    if not comparison_root.exists():
        return []
    return sorted([d for d in comparison_root.iterdir()
                    if d.is_dir() and d.name.startswith('batch_')],
                   reverse=True)


def load_batch(batch_dir: Path) -> List[Tuple[int, pd.DataFrame]]:
    """
    Carga todas las simulaciones de un batch.

    Returns:
        Lista de (seed:int, df:pd.DataFrame) ordenada por seed.
        Cada DataFrame contiene las columnas iteration, accepted_count,
        energy, acceptance_rate.
    """
    sims: List[Tuple[int, pd.DataFrame]] = []
    for sim_dir in sorted(batch_dir.iterdir()):
        if not (sim_dir.is_dir() and sim_dir.name.startswith('simulacion_seed_')):
            continue
        log = sim_dir / 'data' / 'energy_log.csv'
        if not log.exists():
            continue
        try:
            seed = int(sim_dir.name.replace('simulacion_seed_', ''))
            df = pd.read_csv(log)
            if 'accepted_count' in df.columns and 'energy' in df.columns:
                sims.append((seed, df))
        except (ValueError, pd.errors.EmptyDataError):
            continue
    return sorted(sims, key=lambda t: t[0])


def per_sim_summary(sims: List[Tuple[int, pd.DataFrame]]) -> pd.DataFrame:
    """Estadísticas por simulación: U₀, U_final, ΔU, % reducción, iters."""
    rows = []
    for seed, df in sims:
        e0 = float(df['energy'].iloc[0])
        ef = float(df['energy'].iloc[-1])
        delta = e0 - ef
        reduc = (delta / abs(e0)) * 100.0 if e0 != 0 else 0.0
        iters_total = int(df['iteration'].iloc[-1])
        accepted = int(df['accepted_count'].iloc[-1])
        rows.append({
            'seed': seed,
            'U_0': e0,
            'U_final': ef,
            'delta_U': delta,
            'reduccion_%': reduc,
            'iteraciones': iters_total,
            'aceptados': accepted,
        })
    return pd.DataFrame(rows)


def _resample_to_common_grid(sims: List[Tuple[int, pd.DataFrame]],
                              n_points: int = 400):
    """
    Reescala cada curva U(t) a una malla común de `accepted_count`
    normalizada en [0, 1]. Permite calcular media y std entre sims
    que tienen distinto número de aceptaciones.

    Returns:
        (t_norm, U_matrix) donde t_norm ∈ [0,1] tamaño n_points
        y U_matrix shape (n_sims, n_points).
    """
    t_norm = np.linspace(0.0, 1.0, n_points)
    rows = []
    for _, df in sims:
        x = df['accepted_count'].values.astype(float)
        y = df['energy'].values.astype(float)
        if x.max() <= x.min():
            rows.append(np.full(n_points, y[-1]))
            continue
        x_norm = (x - x.min()) / (x.max() - x.min())
        y_resampled = np.interp(t_norm, x_norm, y)
        rows.append(y_resampled)
    return t_norm, np.array(rows)


def render_batch_overlay(sims: List[Tuple[int, pd.DataFrame]],
                          title: str = 'Comparación de Convergencia '
                                       'Energética entre Simulaciones',
                          show_mean_band: bool = True,
                          cmap_name: str = DEFAULT_CMAP):
    """
    Figura con todas las curvas U(t) superpuestas, una por simulación,
    coloreadas con `cmap_name`. Sobre las curvas se dibuja la media
    inter-simulaciones (línea negra gruesa) y la banda ±1σ (sombreado
    gris) si `show_mean_band=True`.

    Args:
        sims: salida de `load_batch`.
        title: título del gráfico.
        show_mean_band: añade media ± 1σ entre simulaciones.
        cmap_name: paleta para distinguir las simulaciones.

    Returns:
        matplotlib.figure.Figure
    """
    plt.rcParams.update(MATPLOTLIB_STYLE)
    fig, ax = plt.subplots(figsize=(FIGURE_SIZE[0] * 1.2, FIGURE_SIZE[1]))

    if not sims:
        ax.text(0.5, 0.5, 'No se encontraron simulaciones en este batch.',
                 ha='center', va='center', transform=ax.transAxes,
                 fontsize=12, color='#555555', style='italic')
        return fig

    n = len(sims)
    cmap = plt.colormaps.get_cmap(cmap_name)
    colors = [cmap(i / max(n - 1, 1)) for i in range(n)]

    # Curvas individuales (eje X = movimientos aceptados absolutos)
    max_x = 0.0
    y_all = []
    for (seed, df), color in zip(sims, colors):
        x = df['accepted_count'].values
        y = df['energy'].values
        ax.plot(x, y, color=color, linewidth=1.0, alpha=0.85,
                 label=f'seed {seed}')
        max_x = max(max_x, float(x.max()))
        y_all.append(y)

    # Banda de media ± 1σ inter-simulaciones, en eje normalizado
    if show_mean_band and n >= 3:
        t_norm, U_mat = _resample_to_common_grid(sims, n_points=400)
        mean_curve = U_mat.mean(axis=0)
        std_curve = U_mat.std(axis=0)
        # Mapear t_norm de vuelta a la escala 'aceptados' usando el
        # promedio de aceptaciones totales para tener un eje X común.
        avg_max_accepted = np.mean([df['accepted_count'].iloc[-1]
                                      for _, df in sims])
        x_axis = t_norm * avg_max_accepted
        ax.fill_between(x_axis, mean_curve - std_curve,
                          mean_curve + std_curve,
                          color='#888888', alpha=0.25,
                          label='media ± 1σ (entre sims)', zorder=4)
        ax.plot(x_axis, mean_curve, color='black', linewidth=2.4,
                 alpha=0.9, label='Media inter-sim', zorder=5)

    # Estilo de ejes
    ax.set_xlabel('Movimientos aceptados', fontsize=13)
    ax.set_ylabel('Energía electrostática U', fontsize=13)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
    # Eje X autoescalado a los datos
    ax.set_xlim(0, max_x * 1.02)

    # Eje Y autoescalado con holgura del 4 %
    energies_concat = np.concatenate(y_all) if y_all else np.array([0.0, 1.0])
    y_data_min = float(energies_concat.min())
    y_data_max = float(energies_concat.max())
    y_pad = (y_data_max - y_data_min) * 0.04
    if y_pad < 1e-9:
        y_pad = 1.0
    ax.set_ylim(y_data_min - y_pad, y_data_max + y_pad)
    ax.tick_params(axis='both', which='major', labelsize=10)

    # Línea en U = 0 si los datos cruzan el cero (modo mixto)
    if y_data_min < 0 < y_data_max:
        ax.axhline(y=0.0, color='#1D3557', linestyle='--', alpha=0.5,
                    linewidth=1.0, label='U = 0', zorder=4)

    ax.grid(True, alpha=0.6, color='#888888', linewidth=0.8, linestyle='-')

    # Leyenda compacta: si hay muchas sims, ponerla a la derecha en
    # 2 columnas para que no tape los datos.
    ncol = 2 if n > 10 else 1
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
               fontsize=8 if n > 12 else 9, framealpha=0.9,
               facecolor='#FFFFFF', edgecolor='#333333',
               ncol=ncol, columnspacing=0.6, handlelength=1.2)

    plt.tight_layout()
    return fig


def render_final_energy_violin(sims: List[Tuple[int, pd.DataFrame]]):
    """
    Visualización complementaria: distribución de energías finales y
    porcentaje de reducción entre las N simulaciones, en formato
    boxplot + scatter (cada punto = una sim).
    """
    plt.rcParams.update(MATPLOTLIB_STYLE)
    summary = per_sim_summary(sims)
    if len(summary) == 0:
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center',
                 transform=ax.transAxes)
        return fig

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIGURE_SIZE[0] * 1.4,
                                                     FIGURE_SIZE[1] * 0.85))

    # Subplot 1: boxplot + jitter de U_final
    ax1.boxplot(summary['U_final'].values, vert=True, widths=0.45,
                  patch_artist=True,
                  boxprops=dict(facecolor='#E63946', alpha=0.35,
                                  edgecolor='#7a1d24'),
                  medianprops=dict(color='#1D3557', linewidth=2),
                  whiskerprops=dict(color='#7a1d24'),
                  capprops=dict(color='#7a1d24'))
    jitter = np.random.normal(1.0, 0.04, size=len(summary))
    ax1.scatter(jitter, summary['U_final'].values, c='#1D3557',
                  s=42, zorder=10, alpha=0.85,
                  edgecolors='white', linewidths=0.8)
    ax1.set_xticks([1])
    ax1.set_xticklabels(['Energía final'])
    ax1.set_ylabel('U_final', fontsize=12)
    ax1.grid(True, alpha=0.35, color='#888888', linewidth=0.5,
              linestyle='--')
    ax1.set_title('Distribución de U_final entre simulaciones',
                   fontsize=12, fontweight='bold')

    # Subplot 2: barras de % reducción por seed
    seeds = summary['seed'].values
    reduc = summary['reduccion_%'].values
    bars = ax2.bar([str(s) for s in seeds], reduc, color='#51CF66',
                     edgecolor='#1D3557', alpha=0.85, linewidth=0.8)
    ax2.axhline(y=float(np.mean(reduc)), color='black', linestyle='--',
                  linewidth=1.5, alpha=0.7,
                  label=f'Media = {np.mean(reduc):.2f}%')
    ax2.set_xlabel('seed', fontsize=12)
    ax2.set_ylabel('Reducción de U (%)', fontsize=12)
    ax2.set_title('% Reducción por simulación',
                   fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.35, color='#888888', linewidth=0.5,
              linestyle='--', axis='y')
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right', fontsize=9)
    ax2.legend(loc='upper right', fontsize=9, framealpha=0.9,
                facecolor='#FFFFFF', edgecolor='#333333')

    plt.tight_layout()
    return fig


def render_full_comparison(batch_dir: Path,
                             output_dir: Optional[Path] = None):
    """
    Pipeline CLI: carga el batch, genera las dos figuras de comparación
    y, si se indica `output_dir`, las guarda como PNG.

    Returns:
        (fig_overlay, fig_summary, summary_df)
    """
    sims = load_batch(batch_dir)
    fig_overlay = render_batch_overlay(sims)
    fig_summary = render_final_energy_violin(sims)
    summary_df = per_sim_summary(sims)

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        fig_overlay.savefig(output_dir / 'batch_energy_overlay.png',
                              dpi=DPI, bbox_inches='tight',
                              facecolor=fig_overlay.get_facecolor())
        fig_summary.savefig(output_dir / 'batch_energy_summary.png',
                              dpi=DPI, bbox_inches='tight',
                              facecolor=fig_summary.get_facecolor())
        summary_df.to_csv(output_dir / 'batch_summary.csv', index=False)

    return fig_overlay, fig_summary, summary_df


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Uso: python plot_batch_comparison.py '
               '<comparison_results/batch_YYYYMMDD_HHMMSS>')
        sys.exit(1)
    bdir = Path(sys.argv[1])
    fo, fs, df = render_full_comparison(bdir, output_dir=bdir)
    print(df.to_string(index=False))
    print(f"\nFiguras guardadas en: {bdir}")
