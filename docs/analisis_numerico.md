# Análisis Numérico y Algorítmico

## 1. Problemas de Escala (O(N²)) y la Optimización O(N)

En el problema de N-Cuerpos, calcular la energía total implica evaluar iteraciones sobre cada par del sistema:
```fortran
U = 0.0
do i = 1, N-1
    do j = i+1, N
        U = U + k * q(i)*q(j) / r(i,j)
    end do
end do
```
Esta doble iteración cuesta $O(N^2)$ operaciones matemáticas. Si en cada paso de nuestro algoritmo de Monte Carlo recalculamos esto, para 500,000 pasos y N=50, significaría $500,000 \times \frac{50 \times 49}{2} = 612.5 \text{ millones}$ de cálculos. 

**Solución Implementada:**
Solo movemos **una** partícula por iteración. Las otras $N-1$ partículas no cambian su distancia mutua. En vez de recalcular todo, se implementó un `compute_delta_energy()` de orden $O(N)$ que evalúa únicamente la contribución de la partícula perturbada antes y después del movimiento:
```fortran
delta_U = U_nueva_contribucion(idx) - U_vieja_contribucion(idx)
```
Si el movimiento se acepta, `U_total_nueva = U_total_vieja + delta_U`. Esto divide la carga computacional por 50, acelerando la simulación masivamente.

## 2. La Singularidad del Cero y el "Softening Parameter"

En la ecuación de energía y campo eléctrico, existe el término $|\vec{r}_i - \vec{r}_j|$ en el denominador.
Si dos cargas colapsan espacialmente, o el algoritmo propone mover una carga a la ubicación exacta de otra, la división por cero detiene la simulación y genera un desbordamiento de memoria (`NaN` o `Inf`).

**Solución Implementada:**
Adición del parámetro de ablandamiento (Softening Parameter) $\epsilon \approx 10^{-2}$:
$$ r_{\text{efectivo}} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2 + \epsilon^2} $$
Esto pone un techo físico y numérico a la fuerza repulsiva/atractiva al acercarse mucho, impidiendo el colapso numérico garantizando la estabilidad de doble precisión IEEE 754 y manteniendo el flujo físico correcto para largas distancias ($r \gg \epsilon$).

## 3. Limitaciones en la Convergencia y el Mínimo Local

El algoritmo implementado es "Greedy". Al aceptar *solo* variaciones $\Delta U < 0$, las cargas "descienden la montaña" buscando el punto más bajo en su vecindad. El sistema se paraliza al llegar al fondo de un "Mínimo Local" del cual es matemáticamente imposible escapar sin añadir temperatura.

Para mitigarlo sin recurrir al recocido simulado (Simulated Annealing), el tamaño del paso $\delta$ (delta) permite "brincar" baches energéticos pequeños, pero pasos muy largos implican demasiados rechazos (acceptance rate colapsa). Se escogió $\delta = 0.25$ como balance óptimo empírico.

## 4. Mejoras Avanzadas y Escalamiento a HPC

Si se deseara escalar esta simulación de $N=50$ a $N=1,000,000$ de partículas o para escapar de mínimos locales complejos, la arquitectura actual llegaría a sus límites. A continuación, se proponen las extensiones profesionales requeridas para escalar el sistema a nivel industrial (High Performance Computing):

### 4.1 Mejoras Algorítmicas y Dinámicas
- **Simulated Annealing (Recocido Simulado):** Actualmente el sistema usa "Greedy Descent" ($T=0$). Al implementar Simulated Annealing, se introduce una Temperatura inicial $T>0$ que permite *aceptar temporalmente* pasos donde $\Delta U > 0$ mediante la probabilidad de Boltzmann $P = e^{-\Delta U / k T}$. Esto es estrictamente necesario para escapar de mínimos locales y encontrar el mínimo global verdadero de energía.
- **Árboles Barnes-Hut (O(N log N)):** Actualmente el sistema evalúa a pares las distancias, costando $O(N)$ por cada paso de partícula. Barnes-Hut agrupa clústeres lejanos de partículas en un solo "centro de carga" macroscópico mediante un octree (o quadtree en 2D), reduciendo la complejidad computacional a $O(N \log N)$. Es indispensable cuando $N > 10,000$.
- **Verlet Lists y Neighbor Lists:** Mantener una lista en memoria de las partículas vecinas dentro de un radio de corte (cutoff radius). Al mover una partícula, solo se calcula la energía con sus vecinos en la lista de Verlet en lugar de todo el sistema. Esto requeriría añadir fuerzas locales e ignorar los aportes electrostáticos a larga distancia, lo cual se suele mitigar con sumas de Ewald.

### 4.2 Paralelización y Hardware (HPC)
- **OpenMP (Memoria Compartida):** Ideal para computadoras multi-núcleo (CPUs de escritorio/servidor). Permite paralelizar el cálculo inicial $O(N^2)$ de energía usando `#pragma omp parallel do` sobre los loops `i` y `j` en Fortran. Es fácil de implementar y escala linealmente hasta ~64 hilos.
- **MPI (Memoria Distribuida):** Message Passing Interface. Requerido si simulamos $10^9$ partículas utilizando clústeres de supercomputadoras en red. El dominio espacial $[-L, L]$ se divide en sub-cajas, y cada nodo de servidor computa una sub-caja, comunicando solo las cargas de frontera a sus nodos vecinos.
- **CUDA/OpenACC (Aceleración por GPU):** Reescribir los núcleos de cálculo de energía (`mod_energy.f90`) para ejecutarlos en miles de núcleos de una tarjeta gráfica NVIDIA. El cálculo paralelo de la suma matricial masiva es donde la GPU brilla, permitiendo aceleraciones de hasta 100x respecto a una CPU moderna.

