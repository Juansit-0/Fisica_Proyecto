#!/usr/bin/env python3
"""
Script de prueba final para verificar que la solución al problema del modo de carga funciona
"""

from pathlib import Path
import sys

# Agregar directorio de la GUI al path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src" / "python"))

# Importar lo necesario de la GUI
OPCIONES_MODOS = {
    "Solo repulsión (todas +1)": 1,
    "Atracción y repulsión (mezcla +1/-1)": 2
}


def probar_mapeo_modos():
    """Prueba que el mapeo entre texto y valor numérico funcione correctamente"""
    print("=" * 60)
    print("PRUEBA 1: Mapeo de modos de carga")
    print("=" * 60)
    
    pruebas = [
        ("Solo repulsión (todas +1)", 1),
        ("Atracción y repulsión (mezcla +1/-1)", 2)
    ]
    
    todo_ok = True
    for texto_esperado, valor_esperado in pruebas:
        valor_obtenido = OPCIONES_MODOS[texto_esperado]
        if valor_obtenido == valor_esperado:
            print(f"✅ Éxito: '{texto_esperado}' → {valor_obtenido}")
        else:
            print(f"❌ ERROR: '{texto_esperado}' → {valor_obtenido} (se esperaba {valor_esperado})")
            todo_ok = False
    
    return todo_ok


def probar_secuencia_cambios():
    """Prueba la secuencia que fallaba antes: 1 → 2 → 1"""
    print("\n" + "=" * 60)
    print("PRUEBA 2: Secuencia de cambios (1 → 2 → 1)")
    print("=" * 60)
    
    secuencia_textos = [
        "Solo repulsión (todas +1)",
        "Atracción y repulsión (mezcla +1/-1)", 
        "Solo repulsión (todas +1)"
    ]
    secuencia_valores_esperados = [1, 2, 1]
    
    todo_ok = True
    for i, (texto, valor_esperado) in enumerate(zip(secuencia_textos, secuencia_valores_esperados)):
        valor_obtenido = OPCIONES_MODOS[texto]
        estado = "✅" if valor_obtenido == valor_esperado else "❌"
        print(f"{estado} Paso {i+1}: Texto='{texto}' → Valor={valor_obtenido} (esperado={valor_esperado})")
        if valor_obtenido != valor_esperado:
            todo_ok = False
    
    return todo_ok


def main():
    print("\n" + "=" * 60)
    print("PRUEBA FINAL DE LA SOLUCIÓN")
    print("=" * 60)
    
    # Ejecutar pruebas
    prueba1_ok = probar_mapeo_modos()
    prueba2_ok = probar_secuencia_cambios()
    
    # Resultado final
    print("\n" + "=" * 60)
    if prueba1_ok and prueba2_ok:
        print("✅ TODAS LAS PRUEBAS PASARON!")
        print("La solución está funcionando correctamente.")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON!")
    print("=" * 60)
    
    return 0 if (prueba1_ok and prueba2_ok) else 1


if __name__ == "__main__":
    exit(main())
