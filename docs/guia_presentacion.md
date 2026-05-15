# Guía de Presentación y Defensa del Proyecto

Esta guía provee las respuestas clave a las preguntas comunes en la defensa del proyecto ante el jurado/docente.

## 1. Justificación de la Arquitectura (Fortran + Python)

**Docente:** *"¿Por qué complicarse usando Fortran y Python combinados y no hacer todo en Python o todo en MATLAB?"*

**Respuesta Óptima:**
> "El problema requería alto rendimiento y visualización científica. Elegimos un enfoque **híbrido** o de *Pipeline Científico*. 
> 
> Usamos **Fortran 90** para la simulación numérica (las 500,000 iteraciones y cálculos matriciales de energía) porque es un lenguaje compilado en bajo nivel con un rendimiento inigualable en bucles matemáticos, siendo el estándar de oro en HPC y supercomputación.
> Por otro lado, elegimos **Python** (Matplotlib/Pandas) para la lectura de los resultados de Fortran y el post-procesamiento. Python no es eficiente calculando los campos N-body, pero cuenta con el mejor ecosistema gráfico del mercado. De esta forma, desacoplamos la carga de CPU intensa de la carga de visualización, logrando que correr 500,000 pasos tome una fracción de segundo, algo inalcanzable con Python nativo."

## 2. Explicando la Optimización Algorítmica

**Docente:** *"Veo que la simulación es muy veloz. ¿Cuál fue el secreto para evitar que colapse calculando iteraciones infinitas?"*

**Respuesta Óptima:**
> "La fórmula estándar de energía requiere recorrer iteraciones anidadas del orden de O(N²) por cada paso temporal. 
> Para 50 partículas son 1,225 pares a evaluar. Dado que nuestro algoritmo Monte Carlo a $T=0$ perturba una sola partícula a la vez, programamos la matriz energética de forma matricial inteligente: en vez de recalcular todo, creamos el módulo `compute_delta_energy` que evalúa de forma O(N) la perturbación de esa única partícula y sumamos ese $\Delta U$ a la energía total. Esta abstracción aceleró nuestra ejecución 50 veces más rápido permitiendo recolectar logs temporales de medio millón de iteraciones instantáneamente."

## 3. Discutiendo la Estabilidad del Sistema y la Fórmula de Softening

**Docente:** *"¿Qué previene que las partículas caigan al mismo punto provocando una división por cero?"*

**Respuesta Óptima:**
> "En simulaciones astrofísicas o electrostáticas N-Body de alta iteración, el radio $r \to 0$ produce una singularidad en el cálculo tensorial y estalla la división de coma flotante produciendo `NaN`. Implementamos en el código fuente Fortran un 'Softening Parameter' (Parámetro de Ablandamiento) $\epsilon = 0.01$. Cuando calculamos $r$, en vez de usar pura Pitágoras usamos $\sqrt{\Delta x^2 + \Delta y^2 + \epsilon^2}$. Este pequeño valor elimina la singularidad en el denominador permitiendo que las cargas opuestas simulen proximidad extrema como un choque o aniquilación estable, pero sin corromper la simulación."

## 4. Analizando los Resultados Gráficos

- **El Muro Perimetral de Cargas:** Al tener solas cargas positivas, todas tienden a ubicarse en la frontera del entorno restringido $[-10,10]$. Esto valida experimentalmente el Teorema de Gauss (Toda carga de exceso en un conductor se distribuye en la superficie).
- **Caída Logarítmica de Energía:** En la gráfica de Energía, la curva decae extremadamente rápido en las primeras 10,000 iteraciones (alta aceptación de saltos, sistema altamente excitable) y luego hace un plató o asíntota, probando la convergencia a una matriz estructural estable (mínimo local de energía).
