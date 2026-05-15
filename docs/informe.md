# Estructura Sugerida para el Informe Final del Proyecto

El documento a entregar al M.Sc. Alejandro Molina deberá ser tipeado en formato Artículo IEEE o estándar Universidad Cooperativa, estructurado así:

## 1. Introducción
- Declaración del problema (Optimizar arreglos espaciales de cargas).
- Importancia de sistemas auto-organizables de mínima energía.
- Arquitectura de solución planteada (Integración modular y delegación de procesamiento a lenguajes compilados de bajo nivel).

## 2. Marco Teórico
- Ecuaciones de la Ley de Coulomb para el sistema n-body.
- Definición formal de gradiente, energía potencial y campo eléctrico vectorial $\vec{E}$.
- Explicación teórica de la minimización energética por pasos (Monte Carlo - Greedy Descent).

## 3. Metodología y Arquitectura Computacional
- Módulos creados, diagramas de topología y dependencias Fortran.
- Técnicas de estabilidad numérica (Parámetro $\epsilon$ para evitar la división geométrica por cero).
- Optimizaciones (Reducción de complejidad temporal evaluando deltas localizados en lugar de recalculado de matriz O(N²)).

## 4. Resultados Analíticos
- Comparaciones espaciales en la iteración inicial y final. Inserte imágenes `/results/figures/scatter_initial.png` y `scatter_final.png`.
- Presentar el declive energético. Inserte el log-scale `/results/figures/energy_vs_iteration.png`. Interpretar qué sucede en la fase de convergencia plana (llegada al Mínimo Local de energía).

## 5. Visualización Científica (Discusión)
- Exposición y discusión del Potencial Eléctrico superpuesto en el espacio (`potential_heatmap.png`).
- Discusión sobre la dirección y magnitudes repulsivas visuales del campo eléctrico local en las configuraciones límite (`electric_field_quiver.png`).

## 6. Conclusiones
- Hallazgos sobre el efecto de dominios restrictivos sobre cargas con repulsión homogénea.
- El éxito de la implementación híbrida y lecciones sobre escalado algorítmico y estabilización iterativa.

## 7. Referencias
- Documentación de GNU Fortran
- Documentación de Matplotlib y SciPy
- Notas de clase, Proyecto Electricidad y Magnetismo
