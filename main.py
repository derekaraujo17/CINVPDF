import streamlit as st
from converter import render_converter
from listado import render_listado

st.set_page_config(page_title="Unificador de PDFs", layout="wide")

if "pdfs_procesados" not in st.session_state:
    st.session_state.pdfs_procesados = {}

st.title("Unificación y Gestión de Expedientes PDF")

with st.sidebar:
    st.header("Navegación")
    
    ventana_actual = st.radio(
        "Ir a:",
        ["1. Subida y Conversión", "2. Listado de Alumnos"],
    )
    
    st.image("pibble_delfin.jpg")
    
if ventana_actual == "1. Subida y Conversión":
    render_converter()
elif ventana_actual == "2. Listado de Alumnos":
    render_listado()