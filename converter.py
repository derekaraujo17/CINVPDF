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

        alumnos_validos = {}
        alumnos_incompletos = {}

        for codigo, lista_archivos in grupos_alumnos.items():
            nombres_archivos = [arch.name for arch in lista_archivos]
            
            tiene_E2 = any("_E2" in nombre for nombre in nombres_archivos)
            tiene_l = any("_l" in nombre for nombre in nombres_archivos)
            
            if tiene_E2 and tiene_l:
                alumnos_validos[codigo] = lista_archivos
            else:
                faltantes = []
                if not tiene_E2: faltantes.append("_E2")
                if not tiene_l: faltantes.append("_l")
                alumnos_incompletos[codigo] = faltantes

        if alumnos_incompletos:
            st.warning("**Atención:** Se detectaron códigos sin su par completo. Estos alumnos NO serán procesados hasta que subas sus archivos faltantes:")
            for cod, faltas in alumnos_incompletos.items():
                st.write(f"  * Alumno **{cod}** ➔ Le falta: `{', '.join(faltas)}`")

        if alumnos_validos:
            st.success(f"✅ {len(alumnos_validos)} alumno(s) listos con sus pares completos (DICT + _l + _E2).")

            if st.button("Ejecutar Conversión"):
                diccionario_resultados = {}

                for codigo, lista_archivos in alumnos_validos.items(): 
                    merger = PdfWriter()
                    
                    merger.append(archivo_dict)
                    
                    def orden_especifico(archivo):
                        if "_l" in archivo.name: return 1
                        elif "_E2" in archivo.name: return 2
                        else: return 3
                    lista_archivos.sort(key=orden_especifico)
                    
                    for arch in lista_archivos:
                        merger.append(arch)
                    
                    fd, ruta_temp = tempfile.mkstemp(suffix=".pdf", prefix=f"Expediente_{codigo}_")
                    with os.fdopen(fd, 'wb') as f:
                        merger.write(f)
                    
                    diccionario_resultados[codigo] = {
                        "ruta": ruta_temp,
                        "archivos_unidos": [a.name for a in lista_archivos]
                    }
                
                if "pdfs_procesados" not in st.session_state:
                    st.session_state.pdfs_procesados = {}
                
                st.session_state.pdfs_procesados.update(diccionario_resultados)
                
                st.balloons()
                st.success("¡Conversión completada con éxito!")