import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from datetime import datetime
import io
from pypdf import PdfReader, PdfWriter
from converter import generar_pdf_desde_blueprint 

# --- FUNCIONES CALLBACK OPTIMIZADAS (Con versionado) ---
def cambiar_posicion(codigo, index_actual, id_unica):
    # Obtenemos la versión actual del estado visual
    version = st.session_state.get(f"v_{codigo}", 0)
    clave_widget = f"pos_{codigo}_{id_unica}_v{version}"
    
    nueva_pos = st.session_state[clave_widget]
    nuevo_index = nueva_pos - 1
    
    if nuevo_index != index_actual:
        blueprint = st.session_state.pdfs_procesados[codigo]["blueprint"]
        # Movemos el elemento en la memoria
        item = blueprint.pop(index_actual)
        blueprint.insert(nuevo_index, item)
        
        # EL TRUCO: Aumentamos la versión para forzar el redibujado limpio
        st.session_state[f"v_{codigo}"] = version + 1

def borrar_hoja(codigo, index_actual):
    blueprint = st.session_state.pdfs_procesados[codigo]["blueprint"]
    blueprint.pop(index_actual)
    
    # EL TRUCO: Aumentamos la versión
    version = st.session_state.get(f"v_{codigo}", 0)
    st.session_state[f"v_{codigo}"] = version + 1
# -------------------------------------------------------------------------

def render_listado():
    st.header("Listado y Edición de Expedientes")

    if not st.session_state.pdfs_procesados:
        st.info("No hay documentos. Primero procesa los archivos en 'Subida y Conversión'.")
        return

    if st.session_state.editando_alumno:
        codigo = st.session_state.editando_alumno
        st.subheader(f"Editor de Páginas: Expediente {codigo}")
        
        if st.button("⬅ Volver al listado general"):
            st.session_state.editando_alumno = None
            if "hoja_preview" in st.session_state:
                st.session_state.hoja_preview = None
            if f"listo_descarga_{codigo}" in st.session_state:
                del st.session_state[f"listo_descarga_{codigo}"]
            st.rerun()

        blueprint = st.session_state.pdfs_procesados[codigo]["blueprint"]
        
        # Leemos la versión actual (o creamos un 0 si es la primera vez)
        version = st.session_state.get(f"v_{codigo}", 0)
        
        col_lista, col_visor = st.columns([1.2, 1])

        with col_lista:
            st.write("**Orden actual del documento:**")
            
            for i, pag in enumerate(blueprint):
                c1, c2, c3, c4 = st.columns([5, 2, 1, 2])
                
                with c1: 
                    st.caption(f"📄 `{pag['archivo']}` (Hoja {pag['pagina_idx'] + 1})")
                with c2:
                    lista_posiciones = list(range(1, len(blueprint) + 1))
                    
                    # Agregamos la versión al final del 'key' para evitar el bug visual
                    st.selectbox(
                        "Posición", 
                        lista_posiciones, 
                        index=i, 
                        key=f"pos_{codigo}_{pag['id_unica']}_v{version}", 
                        label_visibility="collapsed",
                        on_change=cambiar_posicion,
                        args=(codigo, i, pag['id_unica'])
                    )
                with c3:
                    st.button("❌", key=f"del_{codigo}_{pag['id_unica']}_v{version}", on_click=borrar_hoja, args=(codigo, i))
                with c4:
                    if st.button("👁️ Ver", key=f"ver_{codigo}_{pag['id_unica']}_v{version}"):
                        st.session_state.hoja_preview = pag
                        
            st.markdown("---")
            if st.button("💾 Guardar y Reconstruir PDF", type="primary"):
                with st.spinner("Reconstruyendo el documento..."):
                    nueva_ruta = generar_pdf_desde_blueprint(codigo, blueprint)
                    st.session_state.pdfs_procesados[codigo]["ruta"] = nueva_ruta
                    st.session_state[f"listo_descarga_{codigo}"] = True
                st.success("¡Expediente actualizado exitosamente!")

            if st.session_state.get(f"listo_descarga_{codigo}"):
                ruta = st.session_state.pdfs_procesados[codigo]["ruta"]
                with open(ruta, "rb") as f:
                    pdf_bytes_descarga = f.read()

                fecha_actual = datetime.now().strftime("%d-%m-%Y")

                st.download_button(
                    label="📥 Descargar PDF Actualizado",
                    data=pdf_bytes_descarga,
                    file_name=f"DELFIN_{codigo}_EXPEDIENTE_{fecha_actual}.pdf",
                    mime="application/pdf",
                    key=f"btn_desc_inmediata_{codigo}_v{version}"
                )

        with col_visor:
            st.markdown("""
                <style>
                    /* Cubrimos ambas etiquetas internas de Streamlit y forzamos la prioridad */
                    div[data-testid="stColumn"]:has(#visor-flotante),
                    div[data-testid="column"]:has(#visor-flotante) {
                        position: -webkit-sticky !important;
                        position: sticky !important;
                        top: 70px !important; 
                        align-self: flex-start !important; 
                        z-index: 999 !important;
                    }
                </style>
                <div id="visor-flotante"></div>
            """, unsafe_allow_html=True)

            if "hoja_preview" in st.session_state and st.session_state.hoja_preview:
                pag = st.session_state.hoja_preview
                st.info(f"Vista Previa: **{pag['archivo']}** - Hoja {pag['pagina_idx'] + 1}")
                
                ruta_origen = st.session_state.archivos_base[pag["archivo"]]
                reader = PdfReader(ruta_origen)
                writer = PdfWriter()
                writer.add_page(reader.pages[pag["pagina_idx"]])
                
                pdf_bytes = io.BytesIO()
                writer.write(pdf_bytes)
                
                pdf_viewer(
                    input=pdf_bytes.getvalue(), 
                    width=500,
                    height=650,     
                    zoom_level=2.0  
                )
        
        return 

    codigos_ordenados = sorted(st.session_state.pdfs_procesados.keys())
    st.write("### Alumnos Procesados")
    
    col_cod, col_det, col_acc_edit, col_acc_desc = st.columns([2, 3, 2, 2])
    with col_cod: st.markdown("**Código**")
    with col_det: st.markdown("**Total de Páginas**")
    with col_acc_edit: st.markdown("**Editar Orden**")
    with col_acc_desc: st.markdown("**Descarga**")

    st.markdown("<hr style='margin:0.5em 0px;'>", unsafe_allow_html=True)

    for codigo in codigos_ordenados:
        datos = st.session_state.pdfs_procesados[codigo]
        
        c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
        
        with c1:
            st.write(f"👤 {codigo}")
        with c2:
            st.caption(f"{len(datos['blueprint'])} páginas listas")
        with c3:
            if st.button("✏️ Editar Hojas", key=f"btn_edit_{codigo}"):
                st.session_state.editando_alumno = codigo
                st.rerun()
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