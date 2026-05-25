import pandas as pd
import numpy as np
from pathlib import Path

# Cargar configuración final
final_config = Path("data/output/final_config.csv")
df = pd.read_csv(final_config)

# Verificar dipolos: cada par (1-2, 3-4, ..., 49-50)
print("="*60)
print("VERIFICACIÓN DE DIPOLOS (CONFIGURACIÓN FINAL)")
print("="*60)

n_dipolos = len(df) // 2
distancias = []

for i in range(n_dipolos):
    idx1 = 2 * i
    idx2 = 2 * i + 1
    
    x1, y1 = df.iloc[idx1]['x'], df.iloc[idx1]['y']
    x2, y2 = df.iloc[idx2]['x'], df.iloc[idx2]['y']
    q1, q2 = df.iloc[idx1]['charge'], df.iloc[idx2]['charge']
    
    dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    distancias.append(dist)
    
    print(f"Dipolo {i+1:2d}: (+{q1:.0f}) en ({x1:.3f}, {y1:.3f}) ↔ ({q2:.0f}) en ({x2:.3f}, {y2:.3f}) → Distancia: {dist:.4f}")

print("="*60)
print(f"Distancia mínima entre dipolos: {np.min(distancias):.4f}")
print(f"Distancia máxima entre dipolos: {np.max(distancias):.4f}")
print(f"Distancia media entre dipolos:   {np.mean(distancias):.4f}")
print("="*60)

if np.min(distancias) < 0.01:
    print("\n⚠️  ADVERTENCIA: Algunos dipolos están superpuestos!")
else:
    print("\n✅  Todos los dipolos están separados correctamente!")
