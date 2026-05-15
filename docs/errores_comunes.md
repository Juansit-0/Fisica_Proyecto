# Manual de Errores Comunes y Soluciones

Al ejecutar compiladores, pipelines cruzados y manejo matricial, existen trampas comunes que detienen la simulación. Este proyecto cuenta con defensas explícitas, pero aquí se enlistan problemas clásicos a tener en cuenta.

## 1. Problemas de Entorno (Fortran y GCC)

**Error:** `gfortran: command not found` o fallo en `ld: library 'System' not found` en MacOS.
- **Causa:** Homebrew GCC instaló `gfortran` pero MacOS (Xcode) no exporta las carpetas base del sistema al GCC GNU. 
- **Solución Implementada:** El Makefile utiliza `xcrun --show-sdk-path` y exporta la variable `SDKROOT` para ubicar las librerías dinámicas del sistema, acoplando Homebrew con Apple Clang/Xcode.

## 2. Singularidades (`NaN` o `Inf` propagados)

**Error:** Las iteraciones muestran `U = NaN` y el campo eléctrico se dibuja en blanco.
- **Causa Física:** Dos cargas puntuales evaluaron su distancia mutua como $0.0$, el potencial evalúa la función de división entre cero produciendo el overflow IEEE 754 de Infinito. Todos los pasos subsiguientes se contaminan.
- **Solución Implementada:** `mod_energy.f90` incluye un sumando estático $\epsilon^2$ en la raíz cuadrada de las distancias euclidianas. (Técnica: *Softening Parameter*).

## 3. Flickering o Saltos en el Renderizado del Video

**Error:** Al ver `evolucion_cargas.mp4`, los ejes de la gráfica saltan o la escala cambia erráticamente cada 2 frames, mareando al espectador.
- **Causa Visual:** La gráfica autoscala los ejes $X$ y $Y$ basada en los máximos de los *scatter dots* en cada iteración por separado.
- **Solución Implementada:** Se congeló la topología de la figura. Los métodos en `plot_scatter.py` imponen rígidos límites espaciales: `ax.set_xlim(-L_DOMAIN - margin, L_DOMAIN + margin)`. Esto "ancla" el marco de referencia visual.

## 4. Conflicto de Variables Intrinsecas en Fortran

**Error:** `Error: Unexpected use of subroutine name 'random_seed'`.
- **Causa de Programación:** Colisión de semántica en el nombre. Nuestra variable de configuración se llamaba `RANDOM_SEED`, colisionando directamente con la subrutina del core GNU Fortran `random_seed()`.
- **Solución Implementada:** Refactor de variables maestras. Separación entre constantes internas (`SEED_VALUE`) y las subrutinas de núcleo de Fortran.

## 5. Falta de Convergencia ("El sistema nunca se detiene")

**Error:** La simulación finaliza sus 500,000 pasos pero la gráfica sigue cayendo en picada, o el porcentaje de aceptación de saltos es demasiado alto (>80%).
- **Causa Estadística:** El valor del paso aleatorio ($\delta$) es erróneo. Si es microscópico, las cargas gatean sin energía cinética algorítmica. Si es inmenso (ej: 5.0), todas las variaciones se salen de la caja y se rechazan.
- **Solución Implementada:** Set de validación automática a $\delta = 0.25$, forzando un equilibrio termodinámico que exhibe caída dramática y posterior estabilización.
