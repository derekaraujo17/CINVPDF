import streamlit as st
from converter import render_converter
from listado import render_listado
from actualizar import render_actualizar # <--- Importamos la nueva ventana

st.set_page_config(page_title="Unificador de PDFs", layout="wide")

if "pdfs_procesados" not in st.session_state:
    st.session_state.pdfs_procesados = {}
if "archivos_base" not in st.session_state:
    st.session_state.archivos_base = {}
if "editando_alumno" not in st.session_state:
    st.session_state.editando_alumno = None

st.title("Unificación y Gestión de Expedientes PDF")

with st.sidebar:
    st.header("Navegación")
    
    # Agregamos la tercera opción a la lista
    ventana_actual = st.radio(
        "Ir a:",
        [
            "1. Subida y Conversión", 
            "2. Listado de Alumnos", 
            "3. Actualización de Expedientes" # <--- Nueva pestaña
        ],
    )
    
    st.image("pibble_delfin.jpg")
    
if ventana_actual == "1. Subida y Conversión":
    render_converter()
elif ventana_actual == "2. Listado de Alumnos":
    render_listado()
elif ventana_actual == "3. Actualización de Expedientes": # <--- Lógica de ruteo
    render_actualizar()