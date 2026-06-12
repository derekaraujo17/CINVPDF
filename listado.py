import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from datetime import datetime

def render_listado():
    st.header("Listado de Alumnos y Control de Expedientes")

    if not st.session_state.pdfs_procesados:
        st.info("Formato vacío. Primero debes subir y procesar los archivos en la ventana de 'Subida y Conversión'.")
        return

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
            with open(datos["ruta"], "rb") as f:
                pdf_bytes_descarga = f.read()

            fecha_actual = datetime.now().strftime("%d-%m-%Y")

            st.download_button(
                label="📥 Descargar",
                data=pdf_bytes_descarga,
                file_name=f"DELFIN_{codigo}_EXPEDIENTE_{fecha_actual}.pdf",
                mime="application/pdf",
                key=f"btn_desc_{codigo}"
            )
        st.markdown("<hr style='margin:0.5em 0px;'>", unsafe_allow_html=True)

    if st.session_state.alumno_preview:
        st.write("### 📄 Visor de Documento")
        codigo_sel = st.session_state.alumno_preview
        st.info(f"Mostrando vista previa del expediente integrado para el alumno: **{codigo_sel}**")
        
        ruta_archivo_sel = st.session_state.pdfs_procesados[codigo_sel]["ruta"]
        with open(ruta_archivo_sel, "rb") as f:
            pdf_bytes_visor = f.read()
        
        pdf_viewer(input=pdf_bytes_visor, width=700)
        
        if st.button("❌ Cerrar Vista Previa"):
            st.session_state.alumno_preview = None
            st.rerun()