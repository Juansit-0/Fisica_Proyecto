"""
data_loader.py — Carga y validación de datos de simulación

Lee los archivos CSV generados por el núcleo Fortran y los convierte
en estructuras de datos de numpy/pandas para análisis y visualización.

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import numpy as np
import pandas as pd
from pathlib import Path
from config import (OUTPUT_DIR, CONFIG_DIR, ENERGY_LOG,
                    INITIAL_CONFIG, FINAL_CONFIG)


def load_energy_log():
    """
    Carga el registro de energía desde energy_log.csv.
    
    Returns:
        pd.DataFrame con columnas:
        - iteration: número de iteración
        - accepted_count: movimientos aceptados acumulados
        - energy: energía total U del sistema
        - acceptance_rate: tasa de aceptación acumulada
    """
    if not ENERGY_LOG.exists():
        raise FileNotFoundError(
            f"Archivo de energía no encontrado: {ENERGY_LOG}\n"
            "¿Ejecutaste la simulación Fortran primero?"
        )
    
    df = pd.read_csv(ENERGY_LOG)
    
    # Validación: energía debe ser numérica y no contener NaN
    if df['energy'].isna().any():
        print("[WARNING] Se encontraron valores NaN en la energía. Eliminando...")
        df = df.dropna(subset=['energy'])
    
    print(f"   Energy log cargado: {len(df)} registros")
    print(f"    Energía inicial: {df['energy'].iloc[0]:.6f}")
    print(f"    Energía final:   {df['energy'].iloc[-1]:.6f}")
    
    return df


def load_configuration(filepath):
    """
    Carga una configuración de partículas desde un archivo CSV.
    
    Args:
        filepath: ruta al archivo CSV
        
    Returns:
        pd.DataFrame con columnas: particle_id, x, y, charge
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Configuración no encontrada: {filepath}")
    
    df = pd.read_csv(filepath)
    
    # Validación: coordenadas deben ser numéricas
    for col in ['x', 'y', 'charge']:
        if col not in df.columns:
            raise ValueError(f"Columna '{col}' no encontrada en {filepath}")
    
    return df


def load_initial_configuration():
    """Carga la configuración inicial del sistema."""
    return load_configuration(INITIAL_CONFIG)


def load_final_configuration():
    """Carga la configuración final (mínima energía) del sistema."""
    return load_configuration(FINAL_CONFIG)


def load_all_configurations():
    """
    Carga todas las configuraciones guardadas durante la simulación,
    ordenadas por número de archivo.
    
    Returns:
        list of (config_number, pd.DataFrame)
    """
    config_files = sorted(CONFIG_DIR.glob("config_*.csv"))
    
    if not config_files:
        raise FileNotFoundError(
            f"No se encontraron configuraciones en {CONFIG_DIR}\n"
            "¿Ejecutaste la simulación Fortran primero?"
        )
    
    configs = []
    for f in config_files:
        # Extraer número del nombre: config_000001.csv → 1
        num = int(f.stem.split('_')[1])
        df = load_configuration(f)
        configs.append((num, df))
    
    print(f"   {len(configs)} configuraciones cargadas")
    
    return configs


def get_positions_and_charges(df):
    """
    Extrae arrays numpy de posiciones y cargas desde un DataFrame.
    
    Returns:
        x, y, q: arrays numpy
    """
    x = df['x'].values.astype(np.float64)
    y = df['y'].values.astype(np.float64)
    q = df['charge'].values.astype(np.float64)
    
    return x, y, q
