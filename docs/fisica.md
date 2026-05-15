# Fundamentos Físicos de la Simulación

## 1. El Modelo de Interacción

El sistema se basa en la Ley de Coulomb para partículas puntuales. La interacción es de alcance infinito y su magnitud decae de forma proporcional al inverso del cuadrado de la distancia, produciendo una energía potencial proporcional al inverso de la distancia.

### 1.1 Energía Potencial Electrostática

La energía total del sistema $U$ es la suma de las contribuciones de todos los pares de partículas posibles:
$$ U = k_e \sum_{i=1}^{N-1} \sum_{j=i+1}^N \frac{q_i q_j}{|\vec{r}_i - \vec{r}_j|} $$

En nuestra simulación, optimizamos el cálculo por iteración (que tomaría $O(N^2)$) calculando únicamente la diferencia de energía ($\Delta U$) al perturbar la partícula $k$:
$$ \Delta U = U_{\text{nuevo}}^{(k)} - U_{\text{viejo}}^{(k)} = k_e \sum_{j \neq k} \left( \frac{q_k q_j}{|\vec{r}_{k,\text{nuevo}} - \vec{r}_j|} - \frac{q_k q_j}{|\vec{r}_{k,\text{viejo}} - \vec{r}_j|} \right) $$
Esto reduce la complejidad de cada paso a $O(N)$.

## 2. Termodinámica Computacional y Minimización (T=0)

El modelo utilizado es equivalente a un modelo Monte Carlo operando a temperatura cero ($T = 0$). En termodinámica estadística, la probabilidad de aceptar un estado viene dada por el criterio de Metropolis-Hastings:
$$ P(\text{aceptar}) = \min(1, \exp(-\Delta U / k_B T)) $$

Al hacer $T \to 0$:
- Si $\Delta U < 0$, $P \to 1$ (siempre aceptado).
- Si $\Delta U > 0$, $P \to 0$ (siempre rechazado).

Esto corresponde a un **descenso puro del gradiente de energía**, garantizando una reducción monótona, pero sujeta a la captura por mínimos locales (formación de dominios metaestables).

## 3. Dinámica Emergente Observada

### 3.1 Fase de Repulsión (Cargas de Igual Signo)
Si solo hay cargas $+1$:
- Las cargas intentan maximizar sus distancias mutuas.
- Migran invariablemente hacia la periferia del dominio $[-L, L]$.
- Emergen geometrías ordenadas (como arreglos casi cristalinos distribuidos en las paredes debido a la topología de la restricción fronteriza cuadrada).

### 3.2 Fase de Atracción/Repulsión (Cargas Mixtas)
Al incluir cargas $+1$ y $-1$:
- El sistema sufre inestabilidad tipo colapso de Jeans si no existiese el *softening*.
- Cargas opuestas colapsan generando dominios cristalinos neutros locales (dipolos, cuadrupolos).
- Estas formaciones neutralizan el campo eléctrico a gran distancia reduciendo la energía abruptamente.

## 4. Campos Derivados

### 4.1 Potencial Eléctrico $V(\vec{r})$
Un mapa de calor escalar de las tensiones del sistema:
$$ V(\vec{r}) = k_e \sum_{i=1}^N \frac{q_i}{|\vec{r} - \vec{r}_i|} $$

### 4.2 Campo Eléctrico $\vec{E}(\vec{r})$
Un mapa vectorial mostrando la "fuerza" que experimentaría una carga de prueba positiva $+1$:
$$ \vec{E}(\vec{r}) = -\nabla V(\vec{r}) = k_e \sum_{i=1}^N \frac{q_i (\vec{r} - \vec{r}_i)}{|\vec{r} - \vec{r}_i|^3} $$
