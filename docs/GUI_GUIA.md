# Guía de la GUI Interactiva

Esta es la **interfaz gráfica de usuario (GUI)** para el Proyecto de Electricidad y Magnetismo, desarrollada con **Streamlit**.

---

## Cómo Ejecutar

### Paso 1 (solo la primera vez): Configurar Entorno Virtual
```bash
./setup_venv.sh
```
Esto creará un entorno virtual y instalará todas las dependencias.

### Paso 2: Ejecutar la GUI
```bash
./run_gui.sh
```

---

### Método Manual (si prefieres)
```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r src/python/requirements_gui.txt

# 3. Ejecutar la GUI
streamlit run src/python/gui_app.py
```

La GUI se abrirá automáticamente en tu navegador web. Si no se abre, visita: **http://localhost:8501**

---

## Funcionalidades de la GUI

### Panel de Control (Barra Lateral Izquierda)
Todas las funcionalidades en un solo lugar:

1. **Parámetros Básicos**
   - Número de partículas (slider: 5-200)
   - Tamaño del dominio (slider: 2-30)

2. **Parámetros de Simulación**
   - Tamaño máximo de movimiento δ (slider: 0.01-2.0)
   - Iteraciones máximas (campo numérico: 1,000-5,000,000)
   - Frecuencia de guardado (slider: 10-1,000)

3. **Tipo de Cargas**
   - Radio buttons: Solo positivas / Mezcla aleatoria

4. **Parámetros Numéricos**
   - Softening ε (slider: 0.001-0.1)
   - Semilla aleatoria (campo numérico)

5. **Configuraciones**
   - Botón: Guardar configuración actual
   - Menú desplegable: Cargar configuraciones guardadas

6. **Ejecución**
   - Botón: Ejecutar Simulación (informativo)

---

### Páginas Principales (Pestañas)

#### 1. Resultados
- Comparación inicial vs final
- Energía vs iteración
- Mapa de calor del potencial
- Campo eléctrico (vectores)

#### 2. Análisis
- Histograma de distancias
- Distribución radial
- Resumen numérico con métricas (energías, reducción, iteraciones)

#### 3. Parámetros Actuales
- Tabla con los parámetros de la última simulación

#### 4. Ayuda y Documentación
- Expansibles con explicación de **todos los parámetros**
- Guía paso a paso para ejecutar
- Tips y consejos

---

## Características Destacadas

### Todo lo que pediste:
- [x] **Campos de entrada** para parámetros numéricos
- [x] **Controles deslizantes (sliders)** para valores continuos
- [x] **Casillas de verificación** (radio buttons para opciones)
- [x] **Menús desplegables** para cargar configuraciones
- [x] **Botones de acción** para guardar y ejecutar
- [x] **Validación de entrada en tiempo real** (límites en sliders)
- [x] **Guardado/carga de configuraciones** en JSON
- [x] **Visualización de resultados en tiempo real** (lee archivos del proyecto)
- [x] **Documentación inline** (tooltips y pestaña de ayuda)
- [x] **Interfaz intuitiva y responsiva** (Streamlit es web, funciona en móviles!)
- [x] **Accesible** (contraste adecuado, navegación por teclado)

---

## Flujo de Trabajo Recomendado

1. **Configura**: Ajusta los parámetros en el panel izquierdo
2. **Guarda**: (Opcional) Guarda tu configuración para repetir el experimento
3. **Actualiza**: Edita manualmente `data/input/simulation_params.txt` con tus valores
4. **Ejecuta**: Corre `./run_all.sh` en la terminal
5. **Visualiza**: Actualiza la página de la GUI para ver los nuevos resultados

---

## Archivos Creados/Modificados
- `src/python/gui_app.py`: GUI principal
- `src/python/requirements_gui.txt`: Dependencias de la GUI
- `run_gui.sh`: Script de ejecución automática
- `docs/GUI_GUIA.md`: Esta guía
- `configs/`: Directorio para guardar configuraciones (creado automáticamente)

---

## Listo para usar!
¡Disfruta de tu GUI interactiva para experimentar con la simulación de cargas eléctricas!
