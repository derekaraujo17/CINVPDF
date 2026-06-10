import streamlit as st
from pypdf import PdfWriter
import io

def render_converter():
    st.header("Ventana 1: Subida y Conversión de Archivos")
    st.write("Sube todos los archivos juntos. El sistema agrupará automáticamente los archivos correspondientes a cada código junto con el DICT.")

    archivos_subidos = st.file_uploader(
        "Selecciona todos los PDFs (DICT y archivos de alumnos)", 
        type="pdf", 
        accept_multiple_files=True
    )

    if archivos_subidos:
        archivo_dict = None
        grupos_alumnos = {}

        # Paso 1: Clasificar y agrupar los archivos en memoria
        for archivo in archivos_subidos:
            nombre = archivo.name
            
            if "DICT" in nombre.upper():
                archivo_dict = archivo
            else:
                if "_" in nombre:
                    # Extrae exactamente el código (ej. "12345")
                    codigo = nombre.split("_")[0] 
                    if codigo not in grupos_alumnos:
                        grupos_alumnos[codigo] = []
                    grupos_alumnos[codigo].append(archivo)

        # Paso 2: Validar y Procesar
        if not archivo_dict:
            st.error("❌ Falta el archivo general 'DICT'. Por favor, inclúyelo en la subida.")
            return

        st.success(f"✅ Se detectó el archivo DICT y {len(grupos_alumnos)} alumno(s) listos para procesar.")

        if st.button("Ejecutar Conversión Masiva"):
            diccionario_resultados = {}

            for codigo, lista_archivos in grupos_alumnos.items():
                merger = PdfWriter()
                
                # 1. Agrega el DICT como portada/base
                merger.append(archivo_dict)
                
                # Opcional: Ordenar los archivos del alumno para que _E2 vaya antes que _l
                lista_archivos.sort(key=lambda x: x.name)
                
                # 2. Agrega estrictamente los archivos que pertenecen a ESTE código
                for arch in lista_archivos:
                    merger.append(arch)
                
                # Guardar el resultado en un buffer de bytes (memoria RAM)
                pdf_bytes = io.BytesIO()
                merger.write(pdf_bytes)
                pdf_bytes.seek(0)
                
                # Almacenar en el diccionario temporal
                diccionario_resultados[codigo] = {
                    "bytes": pdf_bytes.getvalue(),
                    "archivos_unidos": [a.name for a in lista_archivos]
                }
            
            # Guardar el resultado final en el estado global para que Listado.py lo vea
            st.session_state.pdfs_procesados = diccionario_resultados
            st.balloons()
            st.success("🎉 ¡Conversión completada con éxito! Dirígete a la ventana '2. Listado de Alumnos' para ver los resultados.")