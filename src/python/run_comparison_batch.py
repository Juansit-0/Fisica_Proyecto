#!/usr/bin/env python3
"""
Script para ejecutar 15 simulaciones con semillas diferentes y mismos parámetros.
Guarda resultados organizados para su posterior comparación.
"""

import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import sys
from typing import Dict, Any


#===============================================================================
# CONFIGURACIÓN INICIAL
#===============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
NUM_SIMULACIONES = 15  # Mínimo 15 simulaciones


def obtener_parametros_base() -> Dict[str, Any]:
    """
    Lee los parámetros base desde simulation_params.txt.
    Estos parámetros se mantienen constantes en todas las simulaciones.
    """
    params_file = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
    
    if not params_file.exists():
        print(f"Error: No se encontró {params_file}")
        sys.exit(1)
    
    with open(params_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    return {
        "n_particulas": int(lines[0]),
        "l_dominio": float(lines[1]),
        "delta_mov": float(lines[2]),
        "max_iter": int(lines[3]),
        "charge_mode": int(lines[4]),
        "save_every": int(lines[5]),
        "print_every": int(lines[6]) if len(lines) > 6 else 10000
    }


def escribir_parametros_con_semilla(params: Dict[str, Any], seed: int) -> None:
    """
    Escribe los parámetros incluyendo la semilla específica.
    """
    params_file = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
    
    contenido = f"""{params['n_particulas']}
{params['l_dominio']}
{params['delta_mov']}
{params['max_iter']}
{params['charge_mode']}
{params['save_every']}
{params['print_every']}
{seed}
"""
    
    with open(params_file, "w", encoding="utf-8") as f:
        f.write(contenido)


def crear_directorio_resultados(seed: int, timestamp: str) -> Path:
    """
    Crea un directorio único para almacenar los resultados de una simulación.
    """
    results_dir = PROJECT_ROOT / "comparison_results" / f"batch_{timestamp}" / f"simulacion_seed_{seed}"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def copiar_resultados_a_directorio(target_dir: Path) -> None:
    """
    Copia todos los resultados de una simulación al directorio objetivo.
    """
    data_output = PROJECT_ROOT / "data" / "output"
    results = PROJECT_ROOT / "results"
    
    # Copiar datos de salida
    if data_output.exists():
        shutil.copytree(data_output, target_dir / "data", dirs_exist_ok=True)
    
    # Copiar figuras
    figuras_dir = results / "figures"
    if figuras_dir.exists():
        shutil.copytree(figuras_dir, target_dir / "figures", dirs_exist_ok=True)
    
    # Copiar video
    video_dir = results / "videos"
    if video_dir.exists():
        shutil.copytree(video_dir, target_dir / "videos", dirs_exist_ok=True)


def guardar_info_simulacion(target_dir: Path, params: Dict[str, Any], seed: int) -> None:
    """
    Guarda un archivo con información detallada de la simulación.
    """
    info_file = target_dir / "simulation_info.txt"
    
    contenido = f"""=== INFORMACIÓN DE SIMULACIÓN ===
Fecha y hora: {datetime.now().isoformat()}
Semilla: {seed}

PARÁMETROS:
Número de partículas: {params['n_particulas']}
Tamaño del dominio: {params['l_dominio']}
Delta movimiento: {params['delta_mov']}
Iteraciones máximas: {params['max_iter']}
Modo de carga: {params['charge_mode']}
Save every: {params['save_every']}
Print every: {params['print_every']}
"""
    
    with open(info_file, "w", encoding="utf-8") as f:
        f.write(contenido)


def ejecutar_simulacion_individual(params: Dict[str, Any], seed: int, timestamp: str) -> bool:
    """
    Ejecuta una simulación individual con la semilla especificada.
    """
    print(f"\n{'='*60}")
    print(f"  EJECUTANDO SIMULACIÓN {seed}/{NUM_SIMULACIONES}")
    print(f"{'='*60}")
    
    try:
        # Paso 1: Limpiar datos antiguos
        print("  [1/5] Limpiando datos antiguos...")
        subprocess.run(
            ["make", "clean_data"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Paso 2: Escribir parámetros con la semilla
        print("  [2/5] Escribiendo parámetros...")
        escribir_parametros_con_semilla(params, seed)
        
        # Paso 3: Compilar (si es necesario)
        print("  [3/5] Compilando...")
        subprocess.run(
            ["make", "compile"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Paso 4: Ejecutar simulación
        print("  [4/5] Ejecutando simulación...")
        subprocess.run(
            ["make", "run_sim"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Paso 5: Generar visualizaciones
        print("  [5/5] Generando visualizaciones...")
        subprocess.run(
            ["make", "visualize"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Intentar generar video (opcional)
        try:
            print("  Generando video (opcional)...")
            subprocess.run(
                ["make", "video"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=300
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("  Video no generado (continuando)...")
        
        # Guardar resultados
        print("  Guardando resultados...")
        target_dir = crear_directorio_resultados(seed, timestamp)
        copiar_resultados_a_directorio(target_dir)
        guardar_info_simulacion(target_dir, params, seed)
        
        print(f"  Simulacion {seed} completada exitosamente!")
        print(f"  Resultados guardados en: {target_dir}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  Error en simulacion {seed}: {e}")
        print(f"  stderr: {e.stderr}")
        return False


def main():
    """
    Función principal: ejecuta todas las simulaciones y coordina el proceso.
    """
    print("\n" + "="*80)
    print("  BATCH DE COMPARACIÓN - 15 SIMULACIONES CON SEMILLAS DIFERENTES")
    print("="*80)
    
    # Obtener parámetros base
    params_base = obtener_parametros_base()
    print(f"\nParametros base:")
    for key, value in params_base.items():
        print(f"  - {key}: {value}")
    
    # Generar timestamp único para el batch
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"\nTimestamp del batch: {timestamp}")
    
    # Ejecutar todas las simulaciones
    resultados_exitosos = 0
    semillas_exitosas = []
    
    for seed in range(1, NUM_SIMULACIONES + 1):
        exito = ejecutar_simulacion_individual(params_base, seed, timestamp)
        if exito:
            resultados_exitosos += 1
            semillas_exitosas.append(seed)
    
    # Resumen final
    print("\n" + "="*80)
    print("  RESUMEN DEL BATCH")
    print("="*80)
    print(f"Total simulaciones: {NUM_SIMULACIONES}")
    print(f"Simulaciones exitosas: {resultados_exitosos}")
    print(f"Simulaciones fallidas: {NUM_SIMULACIONES - resultados_exitosos}")
    
    if semillas_exitosas:
        print(f"\nSemillas exitosas: {semillas_exitosas}")
    
    batch_dir = PROJECT_ROOT / "comparison_results" / f"batch_{timestamp}"
    print(f"\nTodos los resultados guardados en: {batch_dir}")
    
    # Guardar resumen del batch
    resumen_file = batch_dir / "batch_summary.txt"
    with open(resumen_file, "w", encoding="utf-8") as f:
        f.write(f"=== RESUMEN DEL BATCH ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Total simulaciones: {NUM_SIMULACIONES}\n")
        f.write(f"Simulaciones exitosas: {resultados_exitosos}\n")
        f.write(f"Simulaciones fallidas: {NUM_SIMULACIONES - resultados_exitosos}\n")
        f.write(f"Semillas exitosas: {semillas_exitosas}\n\n")
        f.write("=== PARÁMETROS BASE ===\n")
        for key, value in params_base.items():
            f.write(f"{key}: {value}\n")
    
    print("\nBatch completado!")
    print(f"Resumen guardado en: {resumen_file}")


if __name__ == "__main__":
    main()

