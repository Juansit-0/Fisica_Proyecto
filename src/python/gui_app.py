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
CONFIGS_DIR = PROJECT_ROOT / "configs"
CONFIGS_DIR.mkdir(exist_ok=True)

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
# FUNCIONES AUXILIARES (ACTUALIZADAS)
#===============================================================================

def guardar_configuracion(nombre: str, params: Dict[str, Any]) -> Path:
    """Guarda una configuración con metadatos descriptivos."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Agregar metadatos legibles
    params_legibles = {
        "metadatos": {
            "nombre_experimento": nombre,
            "fecha": datetime.now().isoformat(),
            "descripcion": AbstraccionDatos.obtener_nivel_complejidad(params.get("N_PARTICULAS", 50)),
        },
        "parametros_tecnicos": params
    }
    
    filename = CONFIGS_DIR / f"config_{nombre}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(params_legibles, f, indent=2, ensure_ascii=False)
    return filename


def cargar_configuracion(filepath: Path) -> Dict[str, Any]:
    """Carga una configuración y extrae los parámetros técnicos."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("parametros_tecnicos", data)


def listar_configuraciones():
    """Lista configuraciones con información legible."""
    return sorted(CONFIGS_DIR.glob("config_*.json"), reverse=True)


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
    # SECCIÓN 5: GUARDAR/CARGAR CONFIGURACIONES
    #---------------------------------------------------------------------------
    st.header("Gestionar Configuraciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_exp = st.text_input(
            label="Nombre del experimento",
            value="experimento",
            label_visibility="collapsed",
            placeholder="Nombre del experimento..."
        )
        
        if st.button("Guardar", use_container_width=True):
            params = {
                "N_PARTICULAS": N_PARTICULAS,
                "L_DOMINIO": L_DOMINIO,
                "DELTA_MOV": DELTA_MOV,
                "MAX_ITER": MAX_ITER,
                "SAVE_EVERY": SAVE_EVERY,
                "CHARGE_MODE": CHARGE_MODE,
                "EPSILON_SOFT": EPSILON_SOFT,
                "SEMILLA": SEMILLA
            }
            filepath = guardar_configuracion(nombre_exp, params)
            st.success(f"Guardado: {filepath.name}")
    
    with col2:
        config_files = listar_configuraciones()
        if config_files:
            selected_config = st.selectbox(
                label="Cargar",
                options=["-- Seleccionar --"] + [f.name for f in config_files],
                label_visibility="collapsed",
                key="select_config"
            )
            if selected_config != "-- Seleccionar --":
                # Cargar la configuración seleccionada
                config_path = CONFIGS_DIR / selected_config
                params = cargar_configuracion(config_path)
                
                # Actualizar session_state con los valores cargados
                st.session_state.N_PARTICULAS = params.get("N_PARTICULAS", 50)
                st.session_state.L_DOMINIO = params.get("L_DOMINIO", 10.0)
                st.session_state.DELTA_MOV = params.get("DELTA_MOV", 0.25)
                st.session_state.MAX_ITER = params.get("MAX_ITER", 500000)
                st.session_state.SAVE_EVERY = params.get("SAVE_EVERY", 100)
                
                # Convertir CHARGE_MODE numérico a texto
                charge_mode_num = params.get("CHARGE_MODE", 1)
                for texto, num in OPCIONES_MODOS.items():
                    if num == charge_mode_num:
                        st.session_state.MODO_CARGA_TEXTO = texto
                        break
                
                st.session_state.EPSILON_SOFT = params.get("EPSILON_SOFT", 0.01)
                st.session_state.SEMILLA = params.get("SEMILLA", 0)
                
                st.success(f"Configuración {selected_config} cargada!")
                st.rerun()
    
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

tab1, tab2, tab3, tab4 = st.tabs([
    "Resultados Visuales", 
    "Análisis del Experimento", 
    "Resumen de Parámetros", 
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
        comparison_img = FIGURES_DIR / "comparison_initial_vs_final.png"
        if comparison_img.exists():
            st.image(str(comparison_img), use_container_width=True, caption="Comparación: Estado inicial vs Estado final")
        else:
            st.warning("No hay resultados aún. Ejecuta la simulación primero.")
    
    with col2:
        st.subheader("Comportamiento de la Energía")
        energy_img = FIGURES_DIR / "energy_vs_iteration.png"
        if energy_img.exists():
            st.image(str(energy_img), use_container_width=True, caption="Cómo disminuyó la energía a lo largo del tiempo")
        else:
            st.warning("No hay gráfica de energía disponible.")
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Potencial Eléctrico")
        potential_img = FIGURES_DIR / "potential_heatmap.png"
        if potential_img.exists():
            st.image(str(potential_img), use_container_width=True, caption="Mapa de 'tensión' en el espacio")
    
    with col4:
        st.subheader("Campo Eléctrico")
        field_img = FIGURES_DIR / "electric_field_quiver.png"
        if field_img.exists():
            st.image(str(field_img), use_container_width=True, caption="Dirección y fuerza del campo eléctrico")
    
    st.markdown("---")
    
    #---------------------------------------------------------------------------
    # VIDEO DE EVOLUCIÓN
    #---------------------------------------------------------------------------
    st.subheader("Video de la Evolución del Sistema")
    video_path = VIDEOS_DIR / "evolucion_cargas.mp4"
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
        st.subheader("Distancias entre Partículas")
        dist_img = FIGURES_DIR / "distance_histogram.png"
        if dist_img.exists():
            st.image(str(dist_img), use_container_width=True, caption="Cómo se distribuyeron las distancias entre las cargas")
    
    with col2:
        st.subheader("Posición Respecto al Centro")
        radial_img = FIGURES_DIR / "radial_distribution.png"
        if radial_img.exists():
            st.image(str(radial_img), use_container_width=True, caption="Dónde se ubicaron las cargas dentro del espacio")
    
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
# PESTAÑA 3: RESUMEN DE PARÁMETROS (CON ABSTRACCIÓN)
#-------------------------------------------------------------------------------
with tab3:
    st.header("Resumen de la Configuración Utilizada")
    
    params_file = DATA_INPUT / "simulation_params.txt"
    if params_file.exists():
        with open(params_file, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # Presentar parámetros con abstracción y etiquetas legibles
        param_info = [
            ("Tamaño del sistema", "Número de partículas", lines[0]),
            ("Espacio de trabajo", "Tamaño del dominio (L)", lines[1]),
            ("Velocidad de ajuste", "Tamaño de movimiento (δ)", lines[2]),
            ("Duración", "Iteraciones máximas", lines[3]),
            ("Tipo de interacción", "Modo de cargas (1=+, 2=±)", 
             AbstraccionDatos.TRADUCCION_CARGA.get(int(lines[4]), lines[4])),
            ("Frecuencia de registro", "Guardar cada N aceptaciones", lines[5]),
        ]
        
        # Tarjetas visuales para cada parámetro
        for categoria, etiqueta, valor in param_info:
            with st.container():
                st.markdown(f"#### {categoria}")
                col_a, col_b = st.columns([1, 2])
                col_a.markdown(f"**{etiqueta}:**")
                col_b.markdown(f"`{valor}`")
                st.markdown("---")
    else:
        st.info("No hay información de parámetros disponible.")

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
