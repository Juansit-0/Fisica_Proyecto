#!/usr/bin/env python3
"""
Script de prueba para reproducir el error en el modo de carga
"""

from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent


def escribir_parametros(charge_mode: int):
    """Escribe parámetros con un valor específico de charge_mode"""
    params_file = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
    
    contenido = f"""50
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
    print(f"✓ Parámetros escritos con charge_mode={charge_mode}")


def leer_parametros():
    """Lee y muestra los parámetros del archivo"""
    params_file = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
    if params_file.exists():
        with open(params_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
        print(f"\n📋 Contenido de simulation_params.txt:")
        for i, line in enumerate(lines):
            print(f"  Línea {i+1}: {line}")
        if len(lines) >= 5:
            print(f"\n🔍 charge_mode detectado: {lines[4]}")


def main():
    print("=" * 60)
    print("PRUEBA DE FUNCIONAMIENTO DEL MODO DE CARGA")
    print("=" * 60)
    
    # Secuencia de prueba: 1 → 2 → 1 (el caso que falla)
    secuencia = [1, 2, 1]
    
    for modo in secuencia:
        print(f"\n{'=' * 60}")
        print(f"PRUEBA: Estableciendo charge_mode={modo}")
        print('=' * 60)
        
        escribir_parametros(modo)
        leer_parametros()
        
        # Verificación simple: el valor en el archivo debe ser el mismo que escribimos
        params_file = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
        with open(params_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
        
        valor_en_archivo = int(lines[4])
        if valor_en_archivo == modo:
            print(f"\nÉxito: El archivo tiene charge_mode={valor_en_archivo}")
        else:
            print(f"\nERROR: Se esperaba charge_mode={modo}, pero el archivo tiene {valor_en_archivo}!")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETA!")
    print("=" * 60)


if __name__ == "__main__":
    main()
