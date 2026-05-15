"""
run_visualization.py — Pipeline maestro de visualización

Ejecuta todos los módulos de visualización en secuencia:
1. Scatter plots (inicial, final, comparación)
2. Energía vs iteración
3. Mapas de calor del potencial eléctrico
4. Campo eléctrico (quiver + magnitud)
5. Análisis estadístico

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import sys
import os
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import setup_matplotlib, ensure_dirs


def main():
    """Pipeline maestro de visualización y análisis."""
    print()
    print("  ****************************************************")
    print("  *                                                  *")
    print("  *   PIPELINE DE VISUALIZACIÓN CIENTÍFICA           *")
    print("  *   Simulación de Cargas Electrostáticas            *")
    print("  *                                                  *")
    print("  ****************************************************")
    print()

    # Configurar matplotlib
    setup_matplotlib()
    ensure_dirs()

    # 1. Scatter plots
    print("  [1/5] Generando scatter plots...")
    from plot_scatter import generate_scatter_plots
    generate_scatter_plots()

    # 2. Energía vs iteración
    print("\n  [2/5] Generando gráficas de energía...")
    from plot_energy import generate_energy_plots
    generate_energy_plots()

    # 3. Mapas de calor del potencial
    print("\n  [3/5] Generando mapas de calor del potencial...")
    from plot_heatmap import generate_heatmaps
    generate_heatmaps()

    # 4. Campo eléctrico
    print("\n  [4/5] Generando visualización del campo eléctrico...")
    from plot_field import generate_field_plots
    generate_field_plots()

    # 5. Análisis estadístico
    print("\n  [5/5] Ejecutando análisis estadístico...")
    from analysis import generate_analysis
    generate_analysis()

    # Resumen final
    print()
    print("  ****************************************************")
    print("  *   PIPELINE COMPLETADO EXITOSAMENTE              *")
    print("  ****************************************************")
    print()
    print("  Resultados guardados en:")
    print("     results/figures/  — Gráficas científicas")
    print("     results/frames/   — Frames para video")
    print()
    print("  Para generar el video, ejecute:")
    print("    $ python3 src/python/video_generator.py")
    print()


if __name__ == '__main__':
    main()
