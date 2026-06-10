import streamlit as st
# 1. Importamos la nueva librería
from streamlit_pdf_viewer import pdf_viewer

def render_listado():
    st.header("Ventana 2: Listado de Alumnos y Control de Expedientes")

    # Verificar si hay datos procesados
    if not st.session_state.pdfs_procesados:
        st.info("Formato vacío. Primero debes subir y procesar los archivos en la ventana de 'Subida y Conversión'.")
        return

    # Obtener y ordenar los códigos de los alumnos
    codigos_ordenados = sorted(st.session_state.pdfs_procesados.keys())

    st.write("### Alumnos Procesados")
    
    col_cod, col_det, col_acc_prev, col_acc_desc = st.columns([2, 4, 2, 2])
    with col_cod: st.markdown("**Código**")
    with col_det: st.markdown("**Documentos Integrados**")
    with col_acc_prev: st.markdown("**Vista Previa**")
    with col_acc_desc: st.markdown("**Descarga**")

    st.markdown("<hr style='margin:0.5em 0px;'>", unsafe_allow_html=True)

    if "alumno_preview" not in st.session_state:
        st.session_state.alumno_preview = None

    for codigo in codigos_ordenados:
        datos = st.session_state.pdfs_procesados[codigo]
        archivos_texto = ", ".join(datos["archivos_unidos"])
        
        c1, c2, c3, c4 = st.columns([2, 4, 2, 2])
        
        with c1:
            st.write(f"👤 {codigo}")
        with c2:
            st.caption(f"DICT + {archivos_texto}")
        with c3:
            if st.button("👁️ Ver PDF", key=f"btn_prev_{codigo}"):
                st.session_state.alumno_preview = codigo
        with c4:
            st.download_button(
                label="📥 Descargar",
                data=datos["bytes"],
                file_name=f"Expediente_{codigo}.pdf",
                mime="application/pdf",
                key=f"btn_desc_{codigo}"
            )
        st.markdown("<hr style='margin:0.5em 0px;'>", unsafe_allow_html=True)

    # --- NUEVA SECCIÓN DE VISTA PREVIA ---
    if st.session_state.alumno_preview:
        st.write("### 📄 Visor de Documento")
        codigo_sel = st.session_state.alumno_preview
        st.info(f"Mostrando vista previa del expediente integrado para el alumno: **{codigo_sel}**")
        
        # Obtenemos los bytes directamente (sin convertirlos a base64)
        pdf_data = st.session_state.pdfs_procesados[codigo_sel]["bytes"]
        
        # 2. Usamos el visor nativo pasándole los bytes directamente
        pdf_viewer(input=pdf_data, width=700)
        
        # Botón para cerrar la vista previa
        if st.button("❌ Cerrar Vista Previa"):
            st.session_state.alumno_preview = None
            st.rerun()