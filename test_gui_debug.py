#!/usr/bin/env python3
"""
Versión de depuración de la GUI para identificar el problema en el modo de carga
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import json
import sys
import subprocess
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Configuración
PROJECT_ROOT = Path(__file__).resolve().parent


#===============================================================================
# GUI DE DEPURACIÓN
#===============================================================================

st.set_page_config(page_title="DEPURACIÓN - Modo de Carga", layout="wide")

st.title("🔍 DEPURACIÓN: Modo de Carga")
st.markdown("---")

#-------------------------------------------------------------------------------
# PRUEBA DEL RADIO BUTTON
#-------------------------------------------------------------------------------
st.header("1. Prueba del Radio Button")

MODO_CARGA = st.radio(
    label="¿Cómo se comportarán las cargas?",
    options=["Solo repulsión (todas +1)", "Atracción y repulsión (mezcla +1/-1)"],
    index=0,
    help="Elige el tipo de interacción entre las partículas",
    key="debug_radio"
)

st.write(f"- **Texto seleccionado**: `{MODO_CARGA}`")
st.write(f"- **'Solo repulsión' en texto?**: `{'Solo repulsión' in MODO_CARGA}`")

CHARGE_MODE = 1 if "Solo repulsión" in MODO_CARGA else 2
st.write(f"- **CHARGE_MODE calculado**: `{CHARGE_MODE}`")

st.markdown("---")

#-------------------------------------------------------------------------------
# PRUEBA DE ESCRITURA EN ARCHIVO
#-------------------------------------------------------------------------------
st.header("2. Prueba de Escritura en Archivo")

def escribir_parametros_debug(charge_mode: int):
    params_file = PROJECT_ROOT / "data" / "input" / "simulation_params_debug.txt"
    contenido = f"""50
10.0
0.25
1000
{charge_mode}
100
1000
0
"""
    with open(params_file, "w", encoding="utf-8") as f:
        f.write(contenido)
    return params_file

if st.button("Escribir parámetros"):
    archivo = escribir_parametros_debug(CHARGE_MODE)
    st.success(f"✅ Parámetros escritos en: {archivo.name}")
    
    # Leer y mostrar contenido
    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()
    st.code(contenido, language="text")

st.markdown("---")

#-------------------------------------------------------------------------------
# VERIFICACIÓN DEL ARCHIVO ACTUAL
#-------------------------------------------------------------------------------
st.header("3. Verificación del Archivo Actual (simulation_params.txt)")

params_file_original = PROJECT_ROOT / "data" / "input" / "simulation_params.txt"
if params_file_original.exists():
    with open(params_file_original, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    st.write("Contenido actual:")
    for i, line in enumerate(lines):
        st.write(f"- Línea {i+1}: {line}")
    if len(lines) >= 5:
        st.info(f"🔍 Charge Mode en archivo: {lines[4]}")
else:
    st.warning("Archivo no encontrado")

st.markdown("---")

#-------------------------------------------------------------------------------
# HISTORIAL DE CAMBIOS
#-------------------------------------------------------------------------------
st.header("4. Historial de Cambios")

if 'historial' not in st.session_state:
    st.session_state.historial = []

# Registrar cambio
if len(st.session_state.historial) == 0 or st.session_state.historial[-1] != (MODO_CARGA, CHARGE_MODE):
    st.session_state.historial.append((MODO_CARGA, CHARGE_MODE))

st.write("Historial de selecciones:")
for i, (modo_texto, modo_num) in enumerate(reversed(st.session_state.historial)):
    st.write(f"{len(st.session_state.historial)-i}. Texto: '{modo_texto}' → Número: {modo_num}")

if st.button("Limpiar historial"):
    st.session_state.historial = []
    st.rerun()
