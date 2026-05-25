"""
Verifica que las cargas se encuentren estrictamente en las coordenadas de la malla.
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Directorio del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "output"
CONFIG_DIR = DATA_DIR / "configurations"

def load_configuration(filepath):
    """Carga una configuración desde un archivo CSV."""
    return pd.read_csv(filepath)

def verify_grid(df, grid_resolution=50, l_domain=10.0):
    """
    Verifica que todas las cargas estén en la malla.
    """
    # Calcular el espaciado entre puntos de la malla
    grid_spacing = (2.0 * l_domain) / (grid_resolution - 1)
    
    print("=" * 70)
    print(f"Verificación de la malla (Resolución: {grid_resolution} puntos/lado)")
    print(f"Dominio: [{-l_domain}, {l_domain}]")
    print(f"Espaciado de malla: {grid_spacing:.6f} unidades")
    print("=" * 70)
    print()
    
    # Obtener coordenadas
    x = df['x'].values
    y = df['y'].values
    
    # Verificar cada coordenada
    print("Verificando coordenadas de las cargas:")
    print()
    
    all_on_grid = True
    for i, (xi, yi) in enumerate(zip(x, y)):
        # Calcular índice de la malla
        idx_x = np.round((xi + l_domain) / grid_spacing)
        idx_y = np.round((yi + l_domain) / grid_spacing)
        
        # Calcular coordenada de malla esperada
        x_grid = -l_domain + idx_x * grid_spacing
        y_grid = -l_domain + idx_y * grid_spacing
        
        # Verificar si coincide
        diff_x = abs(xi - x_grid)
        diff_y = abs(yi - y_grid)
        
        on_grid = diff_x < 1e-6 and diff_y < 1e-6
        if not on_grid:
            all_on_grid = False
        
        print(f"  Carga {i+1:2d}: x={xi:10.6f} (grid: {x_grid:10.6f}, diff: {diff_x:.1e})  "
              f"y={yi:10.6f} (grid: {y_grid:10.6f}, diff: {diff_y:.1e})  {'✓' if on_grid else '✗'}")
    
    print()
    print("=" * 70)
    if all_on_grid:
        print("✓ TODAS LAS CARGAS ESTÁN EN LA MALLA!")
    else:
        print("✗ ALGUNAS CARGAS NO ESTÁN EN LA MALLA!")
    print("=" * 70)
    
    # Mostrar la lista de puntos de malla para referencia
    print()
    print("Puntos de malla disponibles (ejemplo):")
    for i in range(min(10, grid_resolution)):
        x_val = -l_domain + i * grid_spacing
        print(f"  x[{i:2d}] = {x_val:.6f}")
    
    return all_on_grid

if __name__ == '__main__':
    import sys
    
    # Archivos de configuración disponibles
    initial_file = DATA_DIR / "initial_config.csv"
    final_file = DATA_DIR / "final_config.csv"
    
    # Verificar configuración inicial
    if initial_file.exists():
        print()
        print("=" * 70)
        print("CONFIGURACIÓN INICIAL")
        print("=" * 70)
        df_initial = load_configuration(initial_file)
        verify_grid(df_initial, grid_resolution=50, l_domain=10.0)
    
    # Verificar configuración final
    if final_file.exists():
        print()
        print()
        print("=" * 70)
        print("CONFIGURACIÓN FINAL")
        print("=" * 70)
        df_final = load_configuration(final_file)
        verify_grid(df_final, grid_resolution=50, l_domain=10.0)

