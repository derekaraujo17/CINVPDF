import pytesseract
from pdf2image import convert_from_path

# El orden estricto, añadiendo CARTA_CONSEJO en la penúltima posición antes de OFI
PRIORIDADES = {
    "CONVO": 0, "_l": 1, "KARDEX": 2, "CURP": 3, "CSF": 4,
    "VALIDACION_RFC": 5, "ESTADO_CUENTA": 6, "INE": 7,
    "CREDENCIAL_EST": 8, "VALIDACION_EST": 9, "FICHA_DELFIN": 10,
    "COMPROBANTE_DOM": 11, "CARTA_ACEPTACION": 12, "CARTA_CONSEJO": 13,
    "OFI": 14, "BASURA": 99
}

def extraer_texto(ruta_pdf, index_pagina):
    try:
        imagenes = convert_from_path(ruta_pdf, first_page=index_pagina+1, last_page=index_pagina+1)
        if imagenes:
            return pytesseract.image_to_string(imagenes[0], lang='spa').upper()
    except: pass
    return ""

def auto_acomodar_blueprint(blueprint_actual, archivos_base):
    intocables_inicio = [p for p in blueprint_actual if any(x in p["archivo"] for x in ["CONVO", "_l"])]
    intocables_fin = [p for p in blueprint_actual if "OFI" in p["archivo"]]
    
    paginas_procesar = [p for p in blueprint_actual if p not in intocables_inicio and p not in intocables_fin]
    
    for pag in paginas_procesar:
        texto = extraer_texto(archivos_base[pag["archivo"]], pag["pagina_idx"])
        pag["tag"] = "BASURA" # Todo es basura por defecto
        
        # --- 1. REGLAS DE ELIMINACIÓN DIRECTA ---
        if "CARTA COMPROMISO" in texto:
            pag["tag"] = "BASURA"
            continue
        # Cambiamos "IMSS" por frases completas para no afectar la credencial de estudiante
        if "VIGENCIA DE DERECHOS" in texto or "INSTITUTO MEXICANO DEL SEGURO SOCIAL" in texto:
            pag["tag"] = "BASURA"
            continue
            
        # --- 2. REGLAS DE IDENTIFICACIÓN (De más específicas a más generales) ---
        if "ID DELFÍN" in texto or "INFORMACIÓN PERSONAL DEL ESTUDIANTE" in texto: 
            pag["tag"] = "FICHA_DELFIN"
        elif "HONORABLE CONSEJO" in texto: 
            # Todas las cartas al consejo se agruparán en su propio lugar
            pag["tag"] = "CARTA_CONSEJO"
        elif "KARLA ALEJANDRINA PLANTER PEREZ" in texto or ("ESTUDIANTE" in texto and "CUCEI" in texto): 
            pag["tag"] = "CREDENCIAL_EST"
        elif "PROGRAMA INTERINSTITUCIONAL PARA EL FORTALECIMIENTO" in texto or "ACEPTO RECIBIRLO" in texto: 
            pag["tag"] = "CARTA_ACEPTACION"
        elif "KARDEX" in texto or "CALIFICACIONES" in texto: 
            pag["tag"] = "KARDEX"
        elif "VALIDADOR" in texto or "VALIDACIÓN DE DATOS" in texto: 
            pag["tag"] = "VALIDACION_EST"
        elif "SITUACIÓN FISCAL" in texto: 
            pag["tag"] = "CSF"
        elif "RFC VÁLIDO" in texto or "VALIDACIÓN DE RFC" in texto: 
            pag["tag"] = "VALIDACION_RFC"
        elif any(s in texto for s in ["TELMEX", "CFE", "SIAPA", "IZZI", "TOTALPLAY", "AGUA"]): 
            # Detecta servicios incluso si el papel dice "Estado de Cuenta"
            pag["tag"] = "COMPROBANTE_DOM"
        elif any(b in texto for b in ["BBVA", "SANTANDER", "BANAMEX", "BANORTE", "HSBC"]): 
            pag["tag"] = "ESTADO_CUENTA"
        elif "CREDENCIAL PARA VOTAR" in texto or "NACIONAL ELECTORAL" in texto: 
            pag["tag"] = "INE"
        elif "ROSA ICELA" in texto or "RENAPO" in texto: 
            pag["tag"] = "CURP"
            
    # --- HERENCIA HACIA ADELANTE ---
    for i in range(1, len(paginas_procesar)):
        if paginas_procesar[i]["tag"] == "BASURA" and paginas_procesar[i-1]["tag"] != "BASURA":
            # Documentos que suelen tener varias hojas heredan su etiqueta
            if paginas_procesar[i-1]["tag"] in ["KARDEX", "CSF", "ESTADO_CUENTA", "FICHA_DELFIN"]:
                paginas_procesar[i]["tag"] = paginas_procesar[i-1]["tag"]

    # Ordenar y Ensamblar
    paginas_procesar.sort(key=lambda p: PRIORIDADES.get(p["tag"], 99))
    
    finales = [p for p in paginas_procesar if p["tag"] == "BASURA"]
    validos = [p for p in paginas_procesar if p["tag"] != "BASURA"]
    
    return intocables_inicio + validos + intocables_fin + finales