#!/usr/bin/env python3
"""
Script completo para diagnosticar el problema de las partículas azules
"""

from pathlib import Path
import subprocess
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent


def main():
    print("=" * 60)
    print("DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("=" * 60)

    # Paso 1: Escribir parámetros para modo mixto
    print("\n📝 Paso 1: Escribiendo parámetros para modo mixto (charge_mode=2)...")
    params_file = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
    contenido = f"""50
10.0
0.25
10000
2
100
1000
0
"""
    with open(params_file, "w", encoding="utf-8") as f:
        f.write(contenido)
    print("✅ Parámetros escritos (charge_mode=2, 50 partículas, 10k iteraciones)")

    # Paso 2: Limpiar datos antiguos
    print("\n🧹 Paso 2: Limpiando datos antiguos...")
    subprocess.run(["make", "clean_data"], cwd=PROJECT_ROOT, check=True)
    print("✅ Datos antiguos eliminados")

    # Paso 3: Compilar y ejecutar simulación
    print("\n⚙️  Paso 3: Compilando y ejecutando simulación...")
    subprocess.run(["make", "compile"], cwd=PROJECT_ROOT, check=True)
    subprocess.run(["make", "run_sim"], cwd=PROJECT_ROOT, check=True)
    print("✅ Simulación completada")

    # Paso 4: Verificar configuraciones generadas
    print("\n🔍 Paso 4: Verificando configuraciones generadas...")

    initial_config = PROJECT_ROOT / "data" / "output" / "initial_config.csv"
    final_config = PROJECT_ROOT / "data" / "output" / "final_config.csv"

    for nombre, archivo in [("Inicial", initial_config), ("Final", final_config)]:
        if archivo.exists():
            df = pd.read_csv(archivo)
            n_pos = len(df[df['charge'] > 0])
            n_neg = len(df[df['charge'] < 0])
            print(f"\n📊 Configuración {nombre}:")
            print(f"  - Total partículas: {len(df)}")
            print(f"  - Cargas +1 (rojas): {n_pos}")
            print(f"  - Cargas -1 (azules): {n_neg}")
            print(f"  - Cargas únicas: {df['charge'].unique()}")
        else:
            print(f"\n❌ No se encontró la configuración {nombre}!")

    # Paso 5: Ejecutar visualización
    print("\n🎨 Paso 5: Ejecutando visualización...")
    resultado_vis = subprocess.run([
        "python3", "src/python/run_visualization.py"
    ], cwd=PROJECT_ROOT, capture_output=True, text=True)

    if resultado_vis.returncode == 0:
        print("✅ Visualización completada!")
        print("\n📈 Archivos de visualización generados:")
        figuras_dir = PROJECT_ROOT / "results" / "figures"
        if figuras_dir.exists():
            for archivo in figuras_dir.iterdir():
                print(f"  - {archivo.name}")
    else:
        print("❌ Error en visualización:")
        print(resultado_vis.stderr)

    print("\n" + "=" * 60)
    print("DIAGNÓSTICO COMPLETO!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
