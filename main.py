import streamlit as st
# Importamos las funciones de nuestros módulos locales
from converter import render_converter
from listado import render_listado

st.set_page_config(page_title="Gestor de PDFs Alumnos", layout="wide")

# Inicializar el estado global para guardar los PDFs procesados si no existe
if "pdfs_procesados" not in st.session_state:
    st.session_state.pdfs_procesados = {}

st.title("Sistema de Unificación y Gestión de Expedientes PDF")

# Crear la navegación de "ventanas" mediante pestañas (tabs) o barra lateral
ventana_actual = st.sidebar.radio("Navegación", ["1. Subida y Conversión", "2. Listado de Alumnos"])

if ventana_actual == "1. Subida y Conversión":
    render_converter()
elif ventana_actual == "2. Listado de Alumnos":
    render_listado()