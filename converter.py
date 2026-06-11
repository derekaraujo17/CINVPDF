import streamlit as st
from pypdf import PdfWriter
import tempfile
import os

def render_converter():
    st.header("Subida y Conversión de Archivos")
    st.write("Sube todos los archivos juntos.")

    archivos_subidos = st.file_uploader(
        "Selecciona todos los PDFs", 
        type="pdf", 
        accept_multiple_files=True
    )

    if archivos_subidos:
        archivo_dict = None
        grupos_alumnos = {}

        for archivo in archivos_subidos:
            nombre = archivo.name
            
            if "DICT" in nombre.upper():
                archivo_dict = archivo
            else:
                if "_" in nombre:
                    codigo = nombre.split("_")[0] 
                    if codigo not in grupos_alumnos:
                        grupos_alumnos[codigo] = []
                    grupos_alumnos[codigo].append(archivo)

        if not archivo_dict:
            st.error("Falta el archivo general 'DICT'. Por favor, inclúyelo en la subida.")
            return

        st.success(f"Se detectó el archivo DICT y {len(grupos_alumnos)} alumno(s) listos para procesar.")

        if st.button("Convertir"):
            diccionario_resultados = {}

            for codigo, lista_archivos in grupos_alumnos.items():
                merger = PdfWriter()
                
                merger.append(archivo_dict)
                
                def orden_especifico(archivo):
                    if "_l" in archivo.name: 
                        return 1
                    elif "_E2" in archivo.name: 
                        return 2
                    else: 
                        return 3 
                
                lista_archivos.sort(key=orden_especifico)
                
                for arch in lista_archivos:
                    merger.append(arch)
                
                fd, ruta_temp = tempfile.mkstemp(suffix=".pdf", prefix=f"Expediente_{codigo}_")
                with os.fdopen(fd,"wb") as f:
                    merger.write(f)
                
                diccionario_resultados[codigo] = {
                    "ruta":ruta_temp,
                    "archivos_unidos": [a.name for a in lista_archivos]
                }
            
            st.session_state.pdfs_procesados = diccionario_resultados
            st.balloons()
            st.success("Conversión completada. Dirígete a la segunda ventana.")