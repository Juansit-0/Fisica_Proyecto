# Simulación de Cargas Eléctricas y Minimización de Energía Electrostática

**Proyecto de Electricidad y Magnetismo**  
**Universidad Cooperativa de Colombia**  
**Docente:** M.Sc. Alejandro Molina  

Este proyecto simula un sistema bidimensional de cargas eléctricas puntuales que evolucionan dinámicamente buscando configuraciones de mínima energía electrostática mediante un algoritmo de búsqueda "greedy" de minimización energética.

## Arquitectura del Sistema (Híbrida)

El proyecto utiliza una arquitectura que combina el máximo rendimiento de compilación nativa con la flexibilidad y el poder del ecosistema científico de Python:
- **FORTRAN (Núcleo Numérico):** Encargado de la lógica física pesada, algoritmos en $O(N^2)$ optimizados a $O(N)$ y minimización energética veloz. 
- **PYTHON (Pipeline Visual y de Análisis):** Encargado del análisis estadístico, renderizado de mapas de calor, campo eléctrico, gráficas de energía y la generación de videos de la evolución temporal.

## Requisitos Previos

- Compilador de Fortran (`gfortran` provisto por GCC)
- Python 3.x
- Bibliotecas Python: `numpy`, `matplotlib`, `pandas`, `imageio`, `scipy`

## Estructura del Proyecto

```text
Proyecto_FisicaII/
 src/
    fortran/         (Módulos numéricos y de minimización)
    python/          (Pipeline científico de visualización)
 data/
    input/           (simulation_params.txt)
    output/          (Logs de energía, configuraciones)
 results/
    figures/         (Gráficas y mapas de calor)
    videos/          (Evolución temporal)
 docs/                (Fundamentación y manuales)
 Makefile             (Script de compilación)
 run_all.sh           (Script maestro)
```

## Modo de Uso

El proyecto expone un ejecutable automatizado que procesa ambas etapas de experimentación.

### Ejecución Completa (Ambas Fases)
```bash
./run_all.sh
```

### Ejecución por Fases Individuales
Para simular únicamente con cargas positivas:
```bash
./run_all.sh phase1
```

Para simular con cargas positivas y negativas:
```bash
./run_all.sh phase2
```

## Fundamentos Físicos Modelados

El sistema evalúa las siguientes relaciones en un espacio $[-L, L] \times [-L, L]$:
- **Energía Electrostática:** $U = k \sum_{i<j} \frac{q_i q_j}{|r_i - r_j|}$
- **Potencial Eléctrico:** $V(r) = k \sum_i \frac{q_i}{|r - r_i|}$
- **Campo Eléctrico:** $\vec{E}(r) = k \sum_i \frac{q_i (\vec{r} - \vec{r}_i)}{|\vec{r} - \vec{r}_i|^3}$

> Para mayor profundidad, consulte los documentos detallados en la carpeta `/docs/`.
