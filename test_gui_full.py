#!/usr/bin/env python3
"""
Script de prueba para verificar todo el flujo de la GUI con el modo de carga
"""

import streamlit as st
import sys
from pathlib import Path

# Agregar directorio de la GUI al path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

# Configuración inicial
st.set_page_config(page_title="PRUEBA - Modo de Carga", layout="wide")

st.title("🔍 PRUEBA: Modo de Carga Completo")
st.markdown("---")

# Opciones de modos
OPCIONES_MODOS = {
    "Solo repulsión (todas +1)": 1,
    "Atracción y repulsión (mezcla +1/-1)": 2
}

# Inicializar session_state
if 'MODO_CARGA_TEXTO' not in st.session_state:
    st.session_state.MODO_CARGA_TEXTO = list(OPCIONES_MODOS.keys())[0]

# Radio button
MODO_CARGA = st.radio(
    label="¿Cómo se comportarán las cargas?",
    options=list(OPCIONES_MODOS.keys()),
    index=list(OPCIONES_MODOS.keys()).index(st.session_state.MODO_CARGA_TEXTO),
    key="test_radio"
)
st.session_state.MODO_CARGA_TEXTO = MODO_CARGA
CHARGE_MODE = OPCIONES_MODOS[MODO_CARGA]

st.markdown("---")

# Mostrar valores
st.subheader("Valores Actuales")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Texto Seleccionado", MODO_CARGA)
with col2:
    st.metric("Valor Numérico", CHARGE_MODE)
with col3:
    st.metric("Es 'Solo repulsión'?", "✅" if CHARGE_MODE == 1 else "❌")

st.markdown("---")

# Escribir y leer archivo
params_file = PROJECT_ROOT / "data" / "input" / "test_params.txt"

if st.button("Escribir y leer archivo de prueba"):
    # Escribir
    contenido = f"""50
10.0
0.25
1000
{CHARGE_MODE}
100
1000
0
"""
    with open(params_file, "w", encoding="utf-8") as f:
        f.write(contenido)
    st.success("✅ Archivo escrito!")
    
    # Leer y mostrar
    with open(params_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    
    st.subheader("Contenido del Archivo")
    for i, line in enumerate(lines):
        st.write(f"Línea {i+1}: `{line}`")
    
    valor_en_archivo = int(lines[4])
    st.info(f"🔍 Charge Mode en archivo: {valor_en_archivo}")
    
    if valor_en_archivo == CHARGE_MODE:
        st.success("✅ El valor en el archivo COINCIDE con el seleccionado!")
    else:
        st.error("❌ ERROR: El valor en el archivo NO coincide!")

st.markdown("---")
st.info("💡 Prueba: Selecciona un modo, haz clic en el botón, y verifica que el valor en el archivo sea correcto!")
