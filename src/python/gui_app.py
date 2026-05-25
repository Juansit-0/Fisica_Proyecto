"""
GUI Interactiva para Simulación de Cargas Eléctricas
======================================================
Interfaz web desarrollada con Streamlit para configurar, ejecutar
y visualizar experimentos de simulación de cargas electrostáticas.

INCLUYE SISTEMA DE ABSTRACCIÓN COMPLETO Y EJECUCIÓN DIRECTA:
- Capa intermedia para ocultar valores técnicos crudos
- Traducción a formatos legibles para el usuario
- Presentación visual mejorada
- Etiquetas descriptivas y textos explicativos
- Ejecución de la simulación directamente desde la GUI
- Escritura automática de parámetros en el archivo

Autor: Proyecto Física II — Universidad Cooperativa de Colombia
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import json
import sys
import subprocess
import base64
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import setup_matplotlib, ensure_dirs, FIGURES_DIR


#===============================================================================
# CAPA DE ABSTRACCIÓN: CLASES Y FUNCIONES AUXILIARES
#===============================================================================

@dataclass
class ParametroVisual:
    """Clase para abstraer parámetros técnicos a presentaciones visuales."""
    etiqueta: str
    valor_legible: str
    explicacion: str
    impacto: str
    categoria: str


class AbstraccionDatos:
    """Capa intermedia para convertir valores técnicos a formatos legibles."""
    
    # Diccionarios de traducción
    TRADUCCION_CARGA = {
        1: "Solo cargas positivas (+1) — Repulsión",
        2: "Mezcla de cargas (+1 y -1) — Atracción y repulsión"
    }
    
    NIVEL_COMPLEJIDAD = {
        (5, 20): "Muy simple — Rápido",
        (20, 50): "Simple — Velocidad moderada",
        (50, 100): "Medio — Tiempo considerable",
        (100, 200): "Complejo — Requiere paciencia"
    }
    
    @staticmethod
    def obtener_nivel_complejidad(n: int) -> str:
        """Devuelve una descripción legible de la complejidad."""
        for rango, desc in AbstraccionDatos.NIVEL_COMPLEJIDAD.items():
            if rango[0] <= n < rango[1]:
                return desc
        return "Muy complejo — Tiempo prolongado"
    
    @staticmethod
    def obtener_impacto_delta(delta: float) -> str:
        """Explica el impacto del tamaño de movimiento en lenguaje simple."""
        if delta < 0.1:
            return "Muy preciso pero convergencia muy lenta"
        elif delta < 0.5:
            return "Balance óptimo entre precisión y velocidad"
        elif delta < 1.0:
            return "Más rápido pero posiblemente menos preciso"
        else:
            return "Muy rápido pero muchos movimientos serán rechazados"
    
    @staticmethod
    def formatear_energia(energia: float) -> str:
        """Formatea la energía para presentación visual."""
        if abs(energia) < 0.001:
            return f"{energia:.6f}"
        elif abs(energia) < 1000:
            return f"{energia:.4f}"
        else:
            return f"{energia:.2e}"
    
    @staticmethod
    def obtener_estado_convergencia(energia_inicial: float, energia_final: float, iteraciones: int) -> Dict[str, Any]:
        """Analiza el estado de convergencia y devuelve información legible."""
        reduccion = (energia_inicial - energia_final) / abs(energia_inicial) * 100
        
        if reduccion > 90:
            estado = "Excelente convergencia"
            color = "green"
        elif reduccion > 70:
            estado = "Buena convergencia"
            color = "lightgreen"
        elif reduccion > 50:
            estado = "Convergencia parcial"
            color = "orange"
        else:
            estado = "Necesita más iteraciones"
            color = "red"
        
        return {
            "estado": estado,
            "color": color,
            "reduccion": reduccion,
            "interpretacion": (
                f"La energía se redujo en un {reduccion:.1f}%. "
                f"{'Se alcanzó un estado muy estable.' if reduccion > 70 else 'Se recomienda ejecutar más iteraciones.'}"
            )
        }


#===============================================================================
# FUNCIONES PARA EJECUCIÓN DIRECTA DE LA SIMULACIÓN
#===============================================================================

def escribir_parametros(
    n_particulas: int,
    l_dominio: float,
    delta_mov: float,
    max_iter: int,
    charge_mode: int,
    save_every: int,
    print_every: int = 10000,
    semilla: int = 0
) -> None:
    """
    Escribe los parámetros de simulación en el archivo data/input/simulation_params.txt
    """
    params_file = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
    
    contenido = f"""{n_particulas}
{l_dominio}
{delta_mov}
{max_iter}
{charge_mode}
{save_every}
{print_every}
{semilla}
"""
    
    with open(params_file, "w", encoding="utf-8") as f:
        f.write(contenido)


def ejecutar_simulacion() -> tuple[bool, str]:
    """
    Ejecuta el pipeline completo paso a paso (más robusto)
    """
    try:
        # Paso 1: Limpiar datos antiguos
        st.info("Limpiando datos antiguos...")
        subprocess.run(
            ["make", "clean_data"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        # Paso 2: Compilar
        st.info("Compilando código Fortran...")
        resultado_compile = subprocess.run(
            ["make", "compile"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Paso 3: Ejecutar simulación
        st.info("Ejecutando simulación...")
        resultado_sim = subprocess.run(
            ["make", "run_sim"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Paso 4: Generar visualizaciones
        st.info("Generando visualizaciones...")
        resultado_vis = subprocess.run(
            ["make", "visualize"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Paso 5: Generar video
        st.info("Generando video...")
        try:
            resultado_video = subprocess.run(
                ["make", "video"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e_video:
            st.warning("El video no se generó, pero las figuras sí están disponibles.")
        
        # Verificar que las figuras se generaron
        figures_existen = (FIGURES_DIR / "comparison_initial_vs_final.png").exists()
        if figures_existen:
            return True, "Simulación completada exitosamente! Las figuras y video (si se generó) están listos."
        else:
            return False, "No se generaron las figuras, pero la simulación se ejecutó."
            
    except subprocess.CalledProcessError as e:
        # Mostrar el error
        st.error(f"Error en la simulación:\n{e.stderr}")
        return False, "Hubo un error en la simulación"


#===============================================================================
# CONFIGURACIÓN INICIAL
#===============================================================================

st.set_page_config(
    page_title="Simulación de Cargas Eléctricas",
    layout="wide",
    initial_sidebar_state="expanded"
)

setup_matplotlib()
ensure_dirs()

# Directorios
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_INPUT = PROJECT_ROOT / "data" / "input"
DATA_OUTPUT = PROJECT_ROOT / "data" / "output"

# Directorio de videos
VIDEOS_DIR = PROJECT_ROOT / "results" / "videos"

# Directorio static para Streamlit
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

#===============================================================================
# INICIALIZACIÓN DEL ESTADO (session_state)
#===============================================================================

# Opciones de modos de carga
OPCIONES_MODOS = {
    "Solo repulsión (todas +1)": 1,
    "Atracción y repulsión (mezcla +1/-1)": 2
}

# Inicializar valores por defecto en session_state
if 'N_PARTICULAS' not in st.session_state:
    st.session_state.N_PARTICULAS = 50
if 'L_DOMINIO' not in st.session_state:
    st.session_state.L_DOMINIO = 10.0
if 'DELTA_MOV' not in st.session_state:
    st.session_state.DELTA_MOV = 0.25
if 'MAX_ITER' not in st.session_state:
    st.session_state.MAX_ITER = 500000
if 'SAVE_EVERY' not in st.session_state:
    st.session_state.SAVE_EVERY = 100
if 'MODO_CARGA_TEXTO' not in st.session_state:
    st.session_state.MODO_CARGA_TEXTO = list(OPCIONES_MODOS.keys())[0]
if 'EPSILON_SOFT' not in st.session_state:
    st.session_state.EPSILON_SOFT = 0.01
if 'SEMILLA' not in st.session_state:
    st.session_state.SEMILLA = 0


#===============================================================================
# FUNCIONES AUXILIARES
#===============================================================================


#===============================================================================
# SIDEBAR: PANEL DE CONTROL CON ABSTRACCIÓN
#===============================================================================

with st.sidebar:
    st.title("Panel de Control")
    st.markdown("---")
    
    #---------------------------------------------------------------------------
    # SECCIÓN 1: CONFIGURACIÓN DEL EXPERIMENTO
    #---------------------------------------------------------------------------
    st.header("Configuración del Experimento")
    
    N_PARTICULAS = st.slider(
        label="Tamaño del sistema",
        min_value=5,
        max_value=200,
        value=st.session_state.N_PARTICULAS,
        step=5,
        help="Número de cargas eléctricas que participarán en la simulación",
        key="slider_n_particulas"
    )
    st.session_state.N_PARTICULAS = N_PARTICULAS
    
    # Mostrar abstracción del nivel de complejidad
    nivel_complejidad = AbstraccionDatos.obtener_nivel_complejidad(N_PARTICULAS)
    st.info(f"Complejidad: {nivel_complejidad}")
    
    L_DOMINIO = st.slider(
        label="Espacio de trabajo",
        min_value=2.0,
        max_value=30.0,
        value=st.session_state.L_DOMINIO,
        step=0.5,
        help="Tamaño del área cuadrada donde se moverán las partículas",
        key="slider_l_dominio"
    )
    st.session_state.L_DOMINIO = L_DOMINIO
    
    st.markdown("---")
    
    #---------------------------------------------------------------------------
    # SECCIÓN 2: COMPORTAMIENTO DINÁMICO
    #---------------------------------------------------------------------------
    st.header("Comportamiento Dinámico")
    
    DELTA_MOV = st.slider(
        label="Velocidad de ajuste",
        min_value=0.01,
        max_value=2.0,
        value=st.session_state.DELTA_MOV,
        step=0.01,
        format="%.2f",
        help="Qué tan rápido se mueven las partículas en cada paso",
        key="slider_delta_mov"
    )
    st.session_state.DELTA_MOV = DELTA_MOV
    
    # Mostrar impacto del delta
    impacto_delta = AbstraccionDatos.obtener_impacto_delta(DELTA_MOV)
    st.caption(f"{impacto_delta}")
    
    MAX_ITER = st.number_input(
        label="Duración del experimento",
        min_value=1000,
        max_value=5000000,
        value=st.session_state.MAX_ITER,
        step=10000,
        help="Cuántos pasos ejecutará la simulación",
        key="input_max_iter"
    )
    st.session_state.MAX_ITER = MAX_ITER
    
    SAVE_EVERY = st.slider(
        label="Frecuencia de registro",
        min_value=10,
        max_value=1000,
        value=st.session_state.SAVE_EVERY,
        step=10,
        help="Cada cuántos pasos se guarda un registro para el video",
        key="slider_save_every"
    )
    st.session_state.SAVE_EVERY = SAVE_EVERY
    
    st.markdown("---")
    
    #---------------------------------------------------------------------------
    # SECCIÓN 3: TIPO DE INTERACCIÓN
    #---------------------------------------------------------------------------
    st.header("Tipo de Interacción")
    
    MODO_CARGA = st.radio(
        label="¿Cómo se comportarán las cargas?",
        options=list(OPCIONES_MODOS.keys()),
        index=list(OPCIONES_MODOS.keys()).index(st.session_state.MODO_CARGA_TEXTO),
        help="Elige el tipo de interacción entre las partículas",
        key="radio_modo_carga"
    )
    st.session_state.MODO_CARGA_TEXTO = MODO_CARGA
    CHARGE_MODE = OPCIONES_MODOS[MODO_CARGA]
    
    st.markdown("---")
    
    #---------------------------------------------------------------------------
    # SECCIÓN 4: CONFIGURACIÓN AVANZADA (OCULTA POR DEFECTO)
    #---------------------------------------------------------------------------
    with st.expander("Configuración avanzada (opcional)"):
        st.markdown("Solo modifica estos parámetros si sabes lo que haces")
        
        EPSILON_SOFT = st.slider(
            label="Estabilidad numérica",
            min_value=0.001,
            max_value=0.1,
            value=st.session_state.EPSILON_SOFT,
            step=0.001,
            format="%.3f",
            help="Parámetro técnico para evitar errores matemáticos",
            key="slider_epsilon_soft"
        )
        st.session_state.EPSILON_SOFT = EPSILON_SOFT
        
        SEMILLA = st.number_input(
            label="Reproducibilidad",
            min_value=0,
            max_value=999999,
            value=st.session_state.SEMILLA,
            help="0 = resultado diferente cada vez; valor fijo = mismo resultado",
            key="input_semilla"
        )
        st.session_state.SEMILLA = SEMILLA
    
    st.markdown("---")
    
    #---------------------------------------------------------------------------
    # SECCIÓN 6: EJECUCIÓN DIRECTA
    #---------------------------------------------------------------------------
    st.header("Ejecutar Simulación")
    
    if st.button("Iniciar Simulación", type="primary", use_container_width=True):
        with st.spinner("Escribiendo parámetros..."):
            escribir_parametros(
                n_particulas=N_PARTICULAS,
                l_dominio=L_DOMINIO,
                delta_mov=DELTA_MOV,
                max_iter=MAX_ITER,
                charge_mode=CHARGE_MODE,
                save_every=SAVE_EVERY,
                semilla=SEMILLA
            )
            st.success("Parámetros guardados correctamente")
        
        st.info("Iniciando simulación... (esto puede tardar varios minutos)")
        
        with st.spinner("Ejecutando simulación..."):
            exito, mensaje = ejecutar_simulacion()
            
            if exito:
                st.success(mensaje)
                st.balloons()
            else:
                st.error(mensaje)


#===============================================================================
# PÁGINA PRINCIPAL: DASHBOARD CON ABSTRACCIÓN
#===============================================================================

st.title("Simulación de Cargas Eléctricas — Dashboard")
st.markdown("---")

#-------------------------------------------------------------------------------
# PESTAÑAS PRINCIPALES (MEJORADAS)
#-------------------------------------------------------------------------------

# Establecer directorios de figuras y videos
CURRENT_FIGURES_DIR = FIGURES_DIR
CURRENT_VIDEOS_DIR = VIDEOS_DIR
CURRENT_DATA_OUTPUT = DATA_OUTPUT

#-------------------------------------------------------------------------------
# PESTAÑAS PRINCIPALES (MEJORADAS)
#-------------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Resultados Visuales", 
    "Análisis del Experimento", 
    "Comparación de Simulaciones",
    "Ayuda y Conceptos"
])

#-------------------------------------------------------------------------------
# PESTAÑA 1: RESULTADOS VISUALES
#-------------------------------------------------------------------------------
with tab1:
    st.header("Visualización de la Simulación")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolución del Sistema")
        comparison_img = CURRENT_FIGURES_DIR / "comparison_initial_vs_final.png"
        if comparison_img.exists():
            st.image(str(comparison_img), use_container_width=True, caption="Comparación: Estado inicial vs Estado final")
        else:
            st.warning("No hay resultados aún. Ejecuta la simulación primero.")
    
    with col2:
        st.subheader("Comportamiento de la Energía")
        energy_img = CURRENT_FIGURES_DIR / "energy_vs_iteration.png"
        if energy_img.exists():
            st.image(str(energy_img), use_container_width=True, caption="Cómo disminuyó la energía a lo largo del tiempo")
        else:
            st.warning("No hay gráfica de energía disponible.")
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Potencial Eléctrico")
        potential_img = CURRENT_FIGURES_DIR / "potential_heatmap.png"
        if potential_img.exists():
            st.image(str(potential_img), use_container_width=True, caption="Mapa de 'tensión' en el espacio")
    
    with col4:
        st.subheader("Campo Eléctrico")
        field_img = CURRENT_FIGURES_DIR / "electric_field_quiver.png"
        if field_img.exists():
            st.image(str(field_img), use_container_width=True, caption="Dirección y fuerza del campo eléctrico")
    
    st.markdown("---")
    
    #---------------------------------------------------------------------------
    # VIDEO DE EVOLUCIÓN
    #---------------------------------------------------------------------------
    st.subheader("Video de la Evolución del Sistema")
    video_path = CURRENT_VIDEOS_DIR / "evolucion_cargas.mp4"
    if video_path.exists():
        # Copiar el video al directorio static para servirlo correctamente
        import shutil
        video_static_path = STATIC_DIR / "evolucion_cargas.mp4"
        shutil.copy2(video_path, video_static_path)
        
        # Usar st.video directamente - es la forma más compatible
        st.video(str(video_path), format="video/mp4", start_time=0)
        
        # Añadir un pequeño script HTML para forzar autoplay y loop si es posible
        st.components.v1.html(
            """
            <script>
            // Intenta encontrar el elemento de video y configurarlo
            const videos = document.querySelectorAll('video');
            videos.forEach(video => {
                video.autoplay = true;
                video.loop = true;
                video.muted = true;
                video.playsInline = true;
                // Reinicia la reproducción
                video.play().catch(e => console.log('Autoplay bloqueado:', e));
            });
            </script>
            """,
            height=0
        )
        
        st.caption("Cómo se organizaron las partículas a lo largo del tiempo")
    else:
        st.info("Aún no hay video disponible. Ejecuta la simulación completa para generarlo.")

#-------------------------------------------------------------------------------
# PESTAÑA 2: ANÁLISIS DEL EXPERIMENTO (CON ABSTRACCIÓN)
#-------------------------------------------------------------------------------
with tab2:
    st.header("Análisis Detallado del Experimento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Comparación de Energías entre Configuraciones")
        comp_img = FIGURES_DIR / "energy_comparison_histogram.png"
        if comp_img.exists():
            st.image(str(comp_img), use_container_width=True, caption="Energías de 10 configuraciones + la final")
    
    with col2:
        st.subheader("Distribución de Energías Durante la Simulación")
        dist_img = FIGURES_DIR / "energy_distribution.png"
        if dist_img.exists():
            st.image(str(dist_img), use_container_width=True, caption="Cómo se distribuyeron las energías durante la ejecución")
    
    st.markdown("---")
    
    # Análisis numérico con abstracción
    st.subheader("Resumen Numérico (Legible)")
    energy_log_path = DATA_OUTPUT / "energy_log.csv"
    
    if energy_log_path.exists():
        df_energy = pd.read_csv(energy_log_path)
        e_init = df_energy['energy'].iloc[0]
        e_final = df_energy['energy'].iloc[-1]
        
        # Obtener análisis con abstracción
        analisis = AbstraccionDatos.obtener_estado_convergencia(e_init, e_final, len(df_energy))
        
        # Métricas visuales
        metric1, metric2, metric3, metric4 = st.columns(4)
        metric1.metric("Energía inicial", AbstraccionDatos.formatear_energia(e_init))
        metric2.metric("Energía final", AbstraccionDatos.formatear_energia(e_final))
        metric3.metric("Reducción de energía", f"{analisis['reduccion']:.1f}%", delta=f"-{analisis['reduccion']:.1f}%")
        metric4.metric("Pasos totales", f"{len(df_energy):,}")
        
        # Estado de convergencia
        st.markdown(f"### Estado de Convergencia: {analisis['estado']}")
        st.success(analisis['interpretacion'])
    else:
        st.info("No hay datos numéricos disponibles aún.")

#-------------------------------------------------------------------------------
# PESTAÑA 3: COMPARACIÓN DE SIMULACIONES
#-------------------------------------------------------------------------------
with tab3:
    st.header("Comparación de Simulaciones")
    st.markdown("---")
    
    st.markdown("### Resumen del Proceso:")
    st.info("""
    1. **Configura tus parámetros** en el panel izquierdo
    2. **Ejecuta el batch de 15 simulaciones** con semillas diferentes (1-15)
    3. **Visualiza resultados individuales** de cada simulación
    4. **Ver la comparación integral** de todas las ejecuciones
    """)
    
    st.markdown("---")
    
    # Directorio de resultados de comparación
    COMPARISON_RESULTS_DIR = PROJECT_ROOT / "comparison_results"
    COMPARISON_RESULTS_DIR.mkdir(exist_ok=True)
    
    #---------------------------------------------------------------------------
    # SECCIÓN 1: EJECUTAR BATCH DE SIMULACIONES
    #---------------------------------------------------------------------------
    st.subheader("1. Ejecutar Batch de 15 Simulaciones")
    
    if st.button("Iniciar Batch de Comparación", type="primary", use_container_width=True):
        # Primero guardar los parámetros actuales
        with st.spinner("Guardando parámetros base..."):
            escribir_parametros(
                n_particulas=N_PARTICULAS,
                l_dominio=L_DOMINIO,
                delta_mov=DELTA_MOV,
                max_iter=MAX_ITER,
                charge_mode=CHARGE_MODE,
                save_every=SAVE_EVERY,
                semilla=SEMILLA
            )
            st.success("Parámetros base guardados!")
        
        st.warning("""
        Este proceso ejecutará 15 simulaciones consecutivas, cada una con una semilla diferente (1-15).
        Esto puede tardar MUCHOS minutos (dependiendo de tus parámetros).
        
        ¿Estás seguro de continuar?
        """)
        
        # Usamos un placeholder para mostrar el progreso
        progress_placeholder = st.empty()
        
        # Ejecutar el script de comparación
        try:
            with st.spinner("Ejecutando 15 simulaciones... (esto puede tardar mucho)"):
                resultado = subprocess.run(
                    ["python3", "src/python/run_comparison_batch.py"],
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True
                )
                
                if resultado.returncode == 0:
                    st.success("Batch completado exitosamente!")
                    st.balloons()
                    st.text(resultado.stdout)
                else:
                    st.error("Error al ejecutar el batch!")
                    st.text(resultado.stderr)
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    #---------------------------------------------------------------------------
    # SECCIÓN 2: SELECCIONAR BATCH EXISTENTE
    #---------------------------------------------------------------------------
    st.subheader("2. Ver Resultados de un Batch")
    
    batches = sorted(COMPARISON_RESULTS_DIR.glob("batch_*"), reverse=True)
    
    if batches:
        batch_seleccionado = st.selectbox(
            "Seleccionar batch de resultados",
            ["-- Seleccionar --"] + [b.name for b in batches],
            index=0
        )
        
        if batch_seleccionado != "-- Seleccionar --":
            batch_dir = COMPARISON_RESULTS_DIR / batch_seleccionado
            
            # Leer resumen del batch
            resumen_file = batch_dir / "batch_summary.txt"
            if resumen_file.exists():
                with open(resumen_file, "r", encoding="utf-8") as f:
                    st.text_area("Resumen del Batch", f.read(), height=200)
            
            # Obtener todas las simulaciones del batch
            simulaciones = sorted([d for d in batch_dir.iterdir() if d.is_dir() and d.name.startswith("simulacion_seed_")])
            
            if simulaciones:
                st.markdown("---")
                
                # Pestañas para ver resultados individuales y comparación
                tab_individual, tab_comparacion = st.tabs([
                    "Resultados Individuales", 
                    "Comparación Integral"
                ])
                
                #-------------------------------------------------------------------
                # PESTAÑA: RESULTADOS INDIVIDUALES
                #-------------------------------------------------------------------
                with tab_individual:
                    st.subheader("Resultados de Cada Simulación")
                    
                    # Selector de simulación
                    sim_seleccionada = st.selectbox(
                        "Seleccionar simulación",
                        [s.name for s in simulaciones],
                        index=0
                    )
                    
                    sim_dir = batch_dir / sim_seleccionada
                    
                    # Leer info de la simulación
                    info_file = sim_dir / "simulation_info.txt"
                    if info_file.exists():
                        with open(info_file, "r", encoding="utf-8") as f:
                            st.text_area("Información de la Simulación", f.read(), height=150)
                    
                    # Mostrar figuras
                    figuras_dir = sim_dir / "figures"
                    if figuras_dir.exists():
                        st.markdown("### Visualizaciones")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            comp_img = figuras_dir / "comparison_initial_vs_final.png"
                            if comp_img.exists():
                                st.image(str(comp_img), use_container_width=True, caption="Comparación Inicial vs Final")
                        
                        with col2:
                            energy_img = figuras_dir / "energy_vs_iteration.png"
                            if energy_img.exists():
                                st.image(str(energy_img), use_container_width=True, caption="Energía vs Iteración")
                        
                        col3, col4 = st.columns(2)
                        
                        with col3:
                            potential_img = figuras_dir / "potential_heatmap.png"
                            if potential_img.exists():
                                st.image(str(potential_img), use_container_width=True, caption="Potencial Eléctrico")
                        
                        with col4:
                            field_img = figuras_dir / "electric_field_quiver.png"
                            if field_img.exists():
                                st.image(str(field_img), use_container_width=True, caption="Campo Eléctrico")
                    
                    # Análisis detallado
                    data_dir = sim_dir / "data"
                    energy_log = data_dir / "energy_log.csv"
                    if energy_log.exists():
                        st.markdown("---")
                        st.subheader("Análisis Detallado")
                        
                        df_energy = pd.read_csv(energy_log)
                        e_init = df_energy['energy'].iloc[0]
                        e_final = df_energy['energy'].iloc[-1]
                        
                        analisis = AbstraccionDatos.obtener_estado_convergencia(e_init, e_final, len(df_energy))
                        
                        metric1, metric2, metric3, metric4 = st.columns(4)
                        metric1.metric("Energía inicial", AbstraccionDatos.formatear_energia(e_init))
                        metric2.metric("Energía final", AbstraccionDatos.formatear_energia(e_final))
                        metric3.metric("Reducción", f"{analisis['reduccion']:.1f}%")
                        metric4.metric("Iteraciones", f"{len(df_energy):,}")
                        
                        st.markdown(f"### Estado: {analisis['estado']}")
                        st.success(analisis['interpretacion'])
                
                #-------------------------------------------------------------------
                # PESTAÑA: COMPARACIÓN INTEGRAL
                #-------------------------------------------------------------------
                with tab_comparacion:
                    st.subheader("Comparación de Todas las Simulaciones")
                    
                    # Recolectar datos de todas las simulaciones
                    datos_simulaciones = []
                    for sim_dir in simulaciones:
                        data_dir = sim_dir / "data"
                        energy_log = data_dir / "energy_log.csv"
                        if energy_log.exists():
                            df = pd.read_csv(energy_log)
                            seed = int(sim_dir.name.replace("simulacion_seed_", ""))
                            datos_simulaciones.append({
                                "seed": seed,
                                "e_inicial": df['energy'].iloc[0],
                                "e_final": df['energy'].iloc[-1],
                                "iteraciones": len(df)
                            })
                    
                    if datos_simulaciones:
                        # Crear DataFrame para la comparación
                        df_comparacion = pd.DataFrame(datos_simulaciones)
                        df_comparacion = df_comparacion.sort_values("seed")
                        
                        # Mostrar tabla de resultados
                        st.markdown("### Tabla de Resultados")
                        st.dataframe(df_comparacion, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Gráfico de comparación de energías finales
                        st.markdown("### Gráfico: Energías Finales por Semilla")
                        import matplotlib.pyplot as plt
                        
                        fig, ax = plt.subplots(figsize=(14, 8))
                        
                        # Crear gráfico de barras con valores exactos
                        barras = ax.bar(
                            [str(s) for s in df_comparacion["seed"]], 
                            df_comparacion["e_final"], 
                            color='#1f77b4',
                            edgecolor='#0a3d62',
                            linewidth=1.2
                        )
                        
                        # Ajustar ejes a los rangos de los datos
                        min_energia = df_comparacion["e_final"].min()
                        max_energia = df_comparacion["e_final"].max()
                        rango = max_energia - min_energia
                        ax.set_ylim(bottom=min_energia - rango * 0.1, top=max_energia + rango * 0.1)
                        
                        # Configurar malla con subdivisiones pequeñas y precisas
                        ax.grid(True, which='both', linestyle='--', linewidth=0.8, alpha=0.7, color='gray')
                        ax.minorticks_on()
                        ax.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4, color='lightgray')
                        
                        # Etiquetas detalladas en cada punto de datos
                        for barra, energia in zip(barras, df_comparacion["e_final"]):
                            altura = barra.get_height()
                            ax.text(
                                barra.get_x() + barra.get_width()/2,
                                altura + rango * 0.02,
                                f"{energia:.6f}",
                                ha='center',
                                va='bottom',
                                fontsize=7,
                                fontweight='bold',
                                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9, edgecolor='#1f77b4')
                            )
                        
                        # Etiquetas y título
                        ax.set_xlabel('Semilla', fontsize=12, fontweight='bold')
                        ax.set_ylabel('Energía Final (valor exacto)', fontsize=12, fontweight='bold')
                        ax.set_title('Comparación de Energías Finales por Semilla (Valores Brutos y Exactos)', fontsize=14, fontweight='bold', pad=20)
                        ax.tick_params(axis='both', which='major', labelsize=10)
                        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
                        plt.tight_layout()
                        
                        st.pyplot(fig)
                        
                        st.markdown("---")
                        
                        # Estadísticas resumidas (valores brutos)
                        st.markdown("### Estadísticas de los Valores Brutos")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Energía Mínima", f"{df_comparacion['e_final'].min():.6f}")
                        col2.metric("Energía Máxima", f"{df_comparacion['e_final'].max():.6f}")
                        col3.metric("Rango Total", f"{(df_comparacion['e_final'].max() - df_comparacion['e_final'].min()):.6f}")
                        
                        st.markdown("---")
                        
                        # Conclusiones generales (solo valores brutos)
                        st.markdown("### Conclusiones de las Mediciones Brutas")
                        st.info(f"""
                        **Resumen de {len(simulaciones)} mediciones independientes:**
                        
                        1. **Valores Registrados**: Se muestran todos los valores exactos de energía final (6 decimales)
                        2. **Mínima Energía**: La simulación con semilla {df_comparacion.loc[df_comparacion['e_final'].idxmin(), 'seed']} registró {df_comparacion['e_final'].min():.6f}
                        3. **Máxima Energía**: La simulación con semilla {df_comparacion.loc[df_comparacion['e_final'].idxmax(), 'seed']} registró {df_comparacion['e_final'].max():.6f}
                        4. **Variabilidad**: La diferencia entre el valor máximo y mínimo es {(df_comparacion['e_final'].max() - df_comparacion['e_final'].min()):.6f}
                        """)
                    else:
                        st.warning("No hay datos suficientes para generar la comparación.")
    else:
        st.info("Aún no hay batches de comparación ejecutados. Usa el botón de arriba para iniciar uno!")

#-------------------------------------------------------------------------------
# PESTAÑA 4: AYUDA Y CONCEPTOS (DOCUMENTACIÓN INLINE)
#-------------------------------------------------------------------------------
with tab4:
    st.header("Aprende sobre los Conceptos")
    
    with st.expander("¿Qué es la energía electrostática?", expanded=True):
        st.markdown("""
        Es la energía almacenada en el sistema debido a la posición de las cargas.
        
        - Cargas iguales (+ y +, - y -): Se repelen, la energía es alta
        - Cargas diferentes (+ y -): Se atraen, la energía es baja
        
        El sistema busca siempre reducir esta energía para alcanzar estabilidad.
        """)
    
    with st.expander("¿Qué significa cada parámetro?"):
        st.markdown("""
        - Tamaño del sistema: Cuántas cargas hay (más = más complejo)
        - Espacio de trabajo: Área donde se mueven las cargas
        - Velocidad de ajuste: Qué tan rápido se mueven las partículas
        - Duración: Cuántos pasos ejecuta la simulación
        - Tipo de interacción: Si las cargas se repelen o se atraen y repelen
        """)
    
    with st.expander("¿Cómo interpretar los resultados?"):
        st.markdown("""
        - Energía vs Iteración: La curva debe bajar y luego aplanarse (convergencia)
        - Comparación inicial vs final: Las cargas deben organizarse mejor
        - Potencial eléctrico: Rojo = alto potencial, Azul = bajo potencial
        - Campo eléctrico: Flechas muestran la dirección de la fuerza
        """)
    
    with st.expander("¿Cómo ejecutar una nueva simulación?"):
        st.markdown("""
        1. Ajusta los parámetros en el panel izquierdo
        2. (Opcional) Guarda tu configuración
        3. Haz clic en el botón "Iniciar Simulación"
        4. Espera a que termine
        5. Los resultados se actualizarán automáticamente
        """)
    
    st.info("Consejo: Empieza con un sistema pequeño (20-30 partículas) para probar rápidamente!")


#===============================================================================
# PIE DE PÁGINA
#===============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <strong>Proyecto de Electricidad y Magnetismo</strong><br>
        Universidad Cooperativa de Colombia — Docente: M.Sc. Alejandro Molina
    </div>
    """,
    unsafe_allow_html=True
)
