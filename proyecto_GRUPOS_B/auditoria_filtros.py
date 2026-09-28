import os
import pandas as pd
import re

# Configuración de rutas oficiales unificadas
MAESTRO_PRODUCTOS = "data/products.csv"
CARPETA_CASOS = "evaluador/casos-de-todas-la-sala"  
ARCHIVO_SALIDA_PRELIMINAR = "data/planilla_preliminar_auditada.csv"
LOG_DESCARTES = "data/lista_casos_descartados.txt"

def ejecutar_auditoria_oficial():
    print("="*60)
    print("      AUDITORÍA SUB-LITEX: FILTRADO CON IDENTIFICADORES NORMALIZADOS")
    print("="*60)
    
    if not os.path.exists(MAESTRO_PRODUCTOS):
        print(f"❌ Error: Falta el archivo maestro de productos en {MAESTRO_PRODUCTOS}")
        return
        
    df_maestro = pd.read_csv(MAESTRO_PRODUCTOS)
    ids_validos = set(df_maestro['id'].astype(str).str.strip().unique())
    
    # Contadores Paso 2
    casos_recibidos_totales = 0
    descartes_catalogo = 0
    descartes_fantasma = 0
    descartes_duplicados = 0
    
    registro_descartes = []
    mapa_casos_unicos = {}
    descartes_por_sala = {}

    if not os.path.exists(CARPETA_CASOS):
        print(f"❌ Error: Carpeta no encontrada en {CARPETA_CASOS}")
        return

    archivos_validos = []
    for raiz, dirs, archivos in os.walk(CARPETA_CASOS):
        for archivo in archivos:
            if 'casos' in archivo.lower() and 'sala' in archivo.lower() and archivo.endswith('.csv'):
                archivos_validos.append(os.path.join(raiz, archivo))
    
    if not archivos_validos:
        print("⚠️ No se encontraron archivos de casos con el formato 'casos-sala-x.csv'.")
        return

    print(f"📋 Se encontraron {len(archivos_validos)} planillas oficiales para procesar.\n")

    for ruta_completa in archivos_validos:
        archivo_nombre = os.path.basename(ruta_completa)
        df_sala = pd.read_csv(ruta_completa)
        
        match = re.search(r'[Cc]asos-sala-(\d+)', archivo_nombre)
        sala_nombre = f"Sala {match.group(1)}" if match else archivo_nombre
        
        # Generamos un prefijo único basado en el número de sala (ej: sala3_)
        sala_prefijo = f"sala{match.group(1)}_" if match else "sala_desconocida_"
        
        if sala_nombre not in descartes_por_sala:
            descartes_por_sala[sala_nombre] = 0
            
        for _, fila in df_sala.iterrows():
            # MAPEO FLEXIBLE: Detecta cualquier variante de nombre de columna de identificación
            caso_original = ""
            for col_posible in ['caso_id', 'caso', 'id_caso', 'imagen']:
                if col_posible in fila.index:
                    caso_original = str(fila[col_posible]).strip()
                    break
                    
            if caso_original == "" or caso_original == "nan":
                continue
                
            id_correcto = str(fila.get('id_correcto', '')).strip()
            tipo = str(fila.get('tipo', '')).strip().lower()
            quien_eligio = str(fila.get('quien_eligio', 'Desconocido')).strip()
            
            casos_recibidos_totales += 1
            
            # FILTRO 1: Fotos sacadas del catálogo (Falsos Positivos)
            palabras_catalogo = ['exacta', 'exacto', 'recoloreada', 'sin_marco', 'sin m']
            if any(p_clv in tipo for p_clv in palabras_catalogo):
                descartes_catalogo += 1
                descartes_por_sala[sala_nombre] += 1
                registro_descartes.append(f"Caso: {caso_original} | {sala_nombre} | Motivo: Foto salía del catálogo (Tipo: {tipo})")
                continue
                
            # FILTRO 2: ID Correcto no existe en products.csv (IDs Fantasma)
            if id_correcto not in ids_validos:
                descartes_fantasma += 1
                descartes_por_sala[sala_nombre] += 1
                registro_descartes.append(f"Caso: {caso_original} | {sala_nombre} | Motivo: id_correcto ({id_correcto}) no existe en products.csv")
                continue
            
            # NORMALIZACIÓN: Inyectamos el prefijo para volverlo único global y evitar colisiones
            caso_unico_global = f"{sala_prefijo}{caso_original}".lower().replace(" ", "")
            
            datos_limpios = {
                "caso_id": caso_unico_global,  # ID Blindado para que el buscador de Sala 3 no explote
                "id_correcto": id_correcto,
                "tipo": tipo,
                "sala_origen": sala_nombre,
                "quien_eligio": quien_eligio
            }
            
            # FILTRO 3: Fotos repetidas (Ahora solo detectará si una misma sala duplicó datos internamente)
            if caso_unico_global in mapa_casos_unicos:
                descartes_duplicados += 1
                descartes_por_sala[sala_nombre] += 1
                registro_descartes.append(f"Caso: {caso_original} | {sala_nombre} | Motivo: Identificador duplicado interno de la misma sala")
            else:
                mapa_casos_unicos[caso_unico_global] = datos_limpios

    lista_final = list(mapa_casos_unicos.values())
    if not lista_final:
        print("⚠️ No quedaron casos activos tras aplicar los filtros.")
        return
        
    df_resultado = pd.DataFrame(lista_final)
    columnas_oficiales = ["caso_id", "id_correcto", "tipo", "sala_origen", "quien_eligio"]
    df_resultado = df_resultado[columnas_oficiales]
    df_resultado.to_csv(ARCHIVO_SALIDA_PRELIMINAR, index=False)
    
    with open(LOG_DESCARTES, "w", encoding="utf-8") as f:
        f.write("\n".join(registro_descartes))

    sala_mas_descartes = max(descartes_por_sala, key=descartes_por_sala.get) if descartes_por_sala else "Ninguna"

    print("📊 [PASO 2] DATOS DIRECTOS PARA LA SECCIÓN 2 DE TU PLANTILLA:")
    print("-" * 50)
    print(f"Casos recibidos de las 7 salas                       : {casos_recibidos_totales}")
    print(f"Descartados: la foto salía del catálogo             : {descartes_catalogo}")
    print(f"Descartados: el id_correcto no existe en products.csv: {descartes_fantasma}")
    print(f"Descartados: foto repetida real interna de sala      : {descartes_duplicados}")
    print(f"Casos listos para Filtro 4 (Revisión Visual Manual) : {len(lista_final)}")
    print("-" * 50)
    print(f"📍 Sala con mayores conflictos: {sala_mas_descartes} ({descartes_por_sala[sala_mas_descartes]} descartes totales).")
    print("="*60)

if __name__ == "__main__":
    ejecutar_auditoria_oficial()
