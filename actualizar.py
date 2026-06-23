import streamlit as st
from pypdf import PdfReader
from converter import guardar_temp, generar_pdf_desde_blueprint

def render_actualizar():
    st.header("Actualización de Expedientes")
    st.write("Sube un expediente que ya habías descargado y añádele hojas específicas de otros documentos para corregirlo.")

    # 1. Carga de archivos dividida en columnas
    col1, col2 = st.columns(2)
    with col1:
        expediente_base = st.file_uploader("1. Sube el Expediente Base (Ya unificado)", type="pdf")
    with col2:
        archivos_extra = st.file_uploader("2. Sube Archivos Extra (Para extraer hojas)", type="pdf", accept_multiple_files=True)

    if expediente_base:
        # Intentar adivinar el código leyendo el nombre (ej. DELFIN_12345_EXPEDIENTE...)
        codigo_sugerido = ""
        if "_" in expediente_base.name:
            partes = expediente_base.name.split("_")
            if len(partes) > 1:
                codigo_sugerido = partes[1]
        
        codigo_usuario = st.text_input("Código del Alumno a actualizar", value=codigo_sugerido)
        
        paginas_extra_seleccionadas = []
        
        if archivos_extra:
            st.write("### ✂️ Extracción de Hojas")
            st.info("Selecciona exactamente qué páginas quieres extraer de los archivos nuevos. Estas se añadirán al final de tu expediente.")
            
            for arch in archivos_extra:
                reader = PdfReader(arch)
                num_paginas = len(reader.pages)
                
                # Crear lista de opciones ["Página 1", "Página 2", ...]
                opciones = [f"Página {i+1}" for i in range(num_paginas)]
                
                seleccion = st.multiselect(
                    f"Hojas a extraer de: {arch.name}", 
                    opciones, 
                    key=f"ms_{arch.name}"
                )
                
                if seleccion:
                    # Convertimos el texto "Página X" a su índice matemático (X-1)
                    indices = [int(s.split(" ")[1]) - 1 for s in seleccion]
                    paginas_extra_seleccionadas.append({
                        "archivo": arch,
                        "indices": indices
                    })

        if st.button("🛠️ Procesar y Enviar al Editor", type="primary"):
            if not codigo_usuario:
                st.error("Por favor, ingresa el código del alumno.")
                return
            
            blueprint = []
            
            # Paso 1: Leer y desarmar el PDF base completo
            ruta_base = guardar_temp(expediente_base)
            st.session_state.archivos_base[expediente_base.name] = ruta_base
            
            reader_base = PdfReader(ruta_base)
            for i in range(len(reader_base.pages)):
                blueprint.append({
                    "archivo": expediente_base.name,
                    "pagina_idx": i,
                    "id_unica": f"baseact_{codigo_usuario}_{i}"
                })
                
            # Paso 2: Procesar SOLO las páginas que elegiste de los extras (se van al fondo)
            for item in paginas_extra_seleccionadas:
                arch = item["archivo"]
                ruta_extra = guardar_temp(arch)
                st.session_state.archivos_base[arch.name] = ruta_extra
                
                # Agregamos solo los índices elegidos
                for idx in item["indices"]:
                    blueprint.append({
                        "archivo": arch.name,
                        "pagina_idx": idx,
                        "id_unica": f"extra_{arch.name}_{idx}"
                    })

            # Paso 3: Guardar en la sesión y alertar
            with st.spinner("Armando el entorno de edición..."):
                # Inicializamos el espacio del alumno si no existe
                if codigo_usuario not in st.session_state.pdfs_procesados:
                    st.session_state.pdfs_procesados[codigo_usuario] = {}
                    
                st.session_state.pdfs_procesados[codigo_usuario]["blueprint"] = blueprint
                
                # Generamos el PDF físico de respaldo
                ruta_final = generar_pdf_desde_blueprint(codigo_usuario, blueprint)
                st.session_state.pdfs_procesados[codigo_usuario]["ruta"] = ruta_final
                
                # Forzamos la apertura directa del Modo Edición
                st.session_state.editando_alumno = codigo_usuario
                
            st.balloons()
            st.success("¡Documento rearmado! Dirígete a la pestaña '2. Listado de Alumnos' para acomodar tus nuevas hojas.")