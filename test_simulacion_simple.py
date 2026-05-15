#!/usr/bin/env python3
"""
Script simple para probar la simulación de manera directa
"""

from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent

def escribir_parametros(n_particulas, l_dominio, delta_mov, max_iter, charge_mode):
    """Escribe el archivo de parámetros"""
    params_file = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
    contenido = f"""{n_particulas}
{l_dominio}
{delta_mov}
{max_iter}
{charge_mode}
100
1000
0
"""
    with open(params_file, "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"✅ Parámetros escritos: charge_mode={charge_mode}")

def leer_configuracion(archivo):
    """Lee una configuración CSV y muestra las cargas"""
    import pandas as pd
    df = pd.read_csv(archivo)
    print(f"\n📊 {archivo.name}:")
    print(f"  - Total partículas: {len(df)}")
    print(f"  - Cargas +1: {len(df[df['charge'] > 0])}")
    print(f"  - Cargas -1: {len(df[df['charge'] < 0])}")
    print(f"  - Cargas únicas: {df['charge'].unique()}")
    return df

def main():
    print("=" * 60)
    print("PRUEBA DE SIMULACIÓN - MODO SOLO REPULSIÓN")
    print("=" * 60)
    
    # Paso 1: Escribir parámetros para solo repulsión
    escribir_parametros(n_particulas=20, l_dominio=10.0, delta_mov=0.25, 
                       max_iter=1000, charge_mode=1)
    
    # Paso 2: Compilar y ejecutar solo la simulación (sin video)
    print("\n📦 Compilando y ejecutando simulación...")
    
    # Limpiar archivos de compilación
    subprocess.run(["make", "clean"], cwd=PROJECT_ROOT, check=True)
    
    # Compilar primero (solo compile target)
    resultado_make = subprocess.run(["make", "compile"], cwd=PROJECT_ROOT, 
                                    capture_output=True, text=True)
    
    if resultado_make.returncode != 0:
        print("❌ Error en compilación:")
        print(resultado_make.stderr)
        return 1
    print("✅ Compilación exitosa!")
    
    # Ejecutar simulación (solo run_sim target)
    resultado_sim = subprocess.run(["make", "run_sim"], cwd=PROJECT_ROOT, 
                                   capture_output=True, text=True)
    
    if resultado_sim.returncode == 0:
        print("✅ Simulación completada exitosamente!")
    else:
        print("❌ Error en la simulación:")
        print(resultado_sim.stderr)
        return 1
    
    # Paso 3: Leer las configuraciones generadas
    initial_config = PROJECT_ROOT / "data" / "output" / "initial_config.csv"
    final_config = PROJECT_ROOT / "data" / "output" / "final_config.csv"
    
    if initial_config.exists():
        leer_configuracion(initial_config)
    if final_config.exists():
        leer_configuracion(final_config)
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETA!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
