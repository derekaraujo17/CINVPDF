import streamlit as st
from pypdf import PdfReader, PdfWriter
import tempfile
import os

def guardar_temp(archivo_subido):
    fd, ruta = tempfile.mkstemp(suffix=".pdf", prefix=f"base_{archivo_subido.name}_")
    with os.fdopen(fd, 'wb') as f:
        f.write(archivo_subido.getvalue())
    return ruta

def generar_pdf_desde_blueprint(codigo, blueprint):
    merger = PdfWriter()
    for pag in blueprint:
        ruta_origen = st.session_state.archivos_base[pag["archivo"]]
        reader = PdfReader(ruta_origen)
        merger.add_page(reader.pages[pag["pagina_idx"]])
    
    fd, ruta_temp = tempfile.mkstemp(suffix=".pdf", prefix=f"Exped_{codigo}_")
    with os.fdopen(fd, 'wb') as f:
        merger.write(f)
    return ruta_temp
# ----------------------------

def render_converter():
    st.header("Subida y Conversión de Archivos")
    st.write("Sube todos los archivos juntos (CONVO, OFI, _E1, _E2, _l).")

    archivos_subidos = st.file_uploader(
        "Selecciona todos los PDFs", 
        type="pdf", 
        accept_multiple_files=True
    )

    if archivos_subidos:
        archivo_convo = None
        archivo_ofi = None
        grupos_alumnos = {}

        for archivo in archivos_subidos:
            nombre = archivo.name.upper()
            
            if "CONVO" in nombre:
                archivo_convo = archivo
            elif "OFI" in nombre or "DICT" in nombre:
                archivo_ofi = archivo
            else:
                if "_" in nombre:
                    codigo = nombre.split("_")[0] 
                    if codigo not in grupos_alumnos:
                        grupos_alumnos[codigo] = []
                    grupos_alumnos[codigo].append(archivo)

        if not archivo_convo or not archivo_ofi:
            st.error("❌ Faltan los archivos generales (CONVO y/o OFI).")
            return

        alumnos_validos = {}
        alumnos_incompletos = {}

        for codigo, lista_archivos in grupos_alumnos.items():
            nombres_archivos = [arch.name for arch in lista_archivos]
            
            tiene_E1 = any("_E1" in nombre for nombre in nombres_archivos)
            tiene_E2 = any("_E2" in nombre for nombre in nombres_archivos)
            tiene_l = any("_l" in nombre for nombre in nombres_archivos)
            
            if tiene_E1 and tiene_E2 and tiene_l:
                alumnos_validos[codigo] = lista_archivos
            else:
                faltantes = []
                if not tiene_E1: faltantes.append("_E1")
                if not tiene_E2: faltantes.append("_E2")
                if not tiene_l: faltantes.append("_l")
                alumnos_incompletos[codigo] = faltantes

        if alumnos_incompletos:
            st.warning("⚠️ **Atención:** Se detectaron códigos sin su trío completo:")
            for cod, faltas in alumnos_incompletos.items():
                st.write(f"  * Alumno **{cod}** ➔ Le falta: `{', '.join(faltas)}`")

        if alumnos_validos:
            st.success(f"{len(alumnos_validos)} alumno(s) listos con sus archivos completos.")

            if st.button("Procesar y Extraer Páginas", type="primary"):
                st.session_state.archivos_base["CONVO"] = guardar_temp(archivo_convo)
                st.session_state.archivos_base["OFI"] = guardar_temp(archivo_ofi)
                
                diccionario_resultados = {}

                for codigo, lista_archivos in alumnos_validos.items(): 
                    for arch in lista_archivos:
                        st.session_state.archivos_base[arch.name] = guardar_temp(arch)
                    
                    nombre_e1 = next(a.name for a in lista_archivos if "_E1" in a.name)
                    nombre_e2 = next(a.name for a in lista_archivos if "_E2" in a.name)
                    nombre_l = next(a.name for a in lista_archivos if "_l" in a.name)

                    blueprint = []
                    
                    def agregar_al_blueprint(nombre_arch):
                        reader = PdfReader(st.session_state.archivos_base[nombre_arch])
                        for i in range(len(reader.pages)):
                            blueprint.append({
                                "archivo": nombre_arch,
                                "pagina_idx": i,
                                "id_unica": f"{codigo}_{nombre_arch}_{i}"
                            })

                    agregar_al_blueprint("CONVO")
                    agregar_al_blueprint(nombre_l)
                    agregar_al_blueprint(nombre_e1)
                    agregar_al_blueprint(nombre_e2)
                    agregar_al_blueprint("OFI")
                    
                    ruta_final = generar_pdf_desde_blueprint(codigo, blueprint)

                    diccionario_resultados[codigo] = {
                        "blueprint": blueprint,
                        "ruta": ruta_final
                    }
                
                st.session_state.pdfs_procesados.update(diccionario_resultados)
                st.balloons()
                st.success("¡Páginas extraídas! Ve a 'Listado de Alumnos' para editarlas.")