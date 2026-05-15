#!/usr/bin/env python3
"""
Script para probar la secuencia completa 1 → 2 → 1
"""

from pathlib import Path
import subprocess
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent

def ejecutar_prueba(charge_mode, nombre):
    print("\n" + "=" * 60)
    print(f"PRUEBA: {nombre} (charge_mode={charge_mode})")
    print("=" * 60)
    
    # Escribir parámetros
    params_file = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
    contenido = f"""20
10.0
0.25
1000
{charge_mode}
100
1000
0
"""
    with open(params_file, "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"✅ Parámetros escritos: charge_mode={charge_mode}")
    
    # Ejecutar simulación
    resultado = subprocess.run(["make", "run_sim"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    
    if resultado.returncode != 0:
        print("❌ Error en la simulación!")
        return False
    
    # Verificar configuración final
    final_config = PROJECT_ROOT / "data" / "output" / "final_config.csv"
    if not final_config.exists():
        print("❌ No se encontró la configuración final!")
        return False
    
    df = pd.read_csv(final_config)
    n_pos = len(df[df['charge'] > 0])
    n_neg = len(df[df['charge'] < 0])
    
    print(f"✅ Cargas +1: {n_pos}")
    print(f"✅ Cargas -1: {n_neg}")
    
    if charge_mode == 1:
        return n_pos == 20 and n_neg == 0
    else:  # charge_mode == 2
        return n_pos == 10 and n_neg == 10


def main():
    print("=" * 60)
    print("PRUEBA DE SECUENCIA COMPLETA: 1 → 2 → 1")
    print("=" * 60)
    
    # Primero compilar una vez
    print("\n📦 Compilando...")
    subprocess.run(["make", "compile"], cwd=PROJECT_ROOT, check=True)
    
    # Secuencia de pruebas
    secuencia = [
        (1, "Solo repulsión"),
        (2, "Atracción y repulsión"),
        (1, "Solo repulsión (nuevamente)")
    ]
    
    resultados = []
    for charge_mode, nombre in secuencia:
        resultados.append(ejecutar_prueba(charge_mode, nombre))
    
    # Resultado final
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    if all(resultados):
        print("✅ TODAS LAS PRUEBAS PASARON!")
        print("La secuencia 1 → 2 → 1 funciona perfectamente!")
        return 0
    else:
        print("❌ ALGUNA PRUEBA FALLÓ!")
        return 1


if __name__ == "__main__":
    exit(main())
