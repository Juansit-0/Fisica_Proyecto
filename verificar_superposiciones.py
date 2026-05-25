import pandas as pd
import numpy as np
from pathlib import Path

# Cargar configuración final
final_config = Path("data/output/final_config.csv")
df = pd.read_csv(final_config)

print("="*80)
print("VERIFICACIÓN COMPLETA DE SUPERPOSICIONES")
print("="*80)

n = len(df)
overlaps_found = False
min_dist = np.inf
min_pair = None

# Verificar todas las parejas
for i in range(n):
    x1, y1 = df.iloc[i]['x'], df.iloc[i]['y']
    q1 = df.iloc[i]['charge']
    
    for j in range(i+1, n):
        x2, y2 = df.iloc[j]['x'], df.iloc[j]['y']
        q2 = df.iloc[j]['charge']
        
        dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        
        # Actualizar distancia mínima
        if dist < min_dist:
            min_dist = dist
            min_pair = (i, j, q1, q2)
        
        # Verificar superposición (EPSILON_SOFT = 0.01)
        if dist < 0.01:
            overlaps_found = True
            print(f"\n⚠️  SUPERPOSICIÓN ENCONTRADA!")
            print(f"  Partícula {i+1:2d}: ({x1:.6f}, {y1:.6f}) q={q1:.0f}")
            print(f"  Partícula {j+1:2d}: ({x2:.6f}, {y2:.6f}) q={q2:.0f}")
            print(f"  Distancia: {dist:.8f} (menor que 0.01)")

print("\n" + "="*80)
print("RESUMEN:")
print(f"  Total de partículas: {n}")
print(f"  Total de parejas: {n*(n-1)//2}")
print(f"  Distancia mínima encontrada: {min_dist:.8f}")
if min_pair:
    i, j, q1, q2 = min_pair
    print(f"  Pareja con distancia mínima: {i+1} (q={q1:.0f}) ↔ {j+1} (q={q2:.0f})")

if overlaps_found:
    print("\n❌  HAY SUPERPOSICIONES EN EL SISTEMA!")
else:
    print("\n✅  NO HAY SUPERPOSICIONES EN EL SISTEMA!")
print("="*80)
