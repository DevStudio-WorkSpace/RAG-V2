import os
import pandas as pd

PLANILLA_PRELIMINAR = "data/planilla_preliminar_auditada.csv"
ARCHIVO_FINAL_LIMPIO = "data/planilla_oficial_limpia.csv"

def cerrar_auditoria_completa():
    print("="*60)
    print("   CONSOLIDACIÓN FINAL DE AUDITORÍA — SECCIONES 2 Y 3 (RE-CALIBRADO)")
    print("="*60)
    
    if not os.path.exists(PLANILLA_PRELIMINAR):
        print(f"❌ Error: No se encuentra {PLANILLA_PRELIMINAR}.")
        return
        
    df_preliminar = pd.read_csv(PLANILLA_PRELIMINAR)
    
    # Valores fijos de la auditoría automática
    descartes_catalogo_auto = 5
    descartes_fantasma = 14
    descartes_duplicados = 10
    casos_recibidos_iniciales = 67
    
    casos_validos = []
    descartes_visuales_manuales = 0
    
    # Contadores oficiales Paso 3
    conteo_tipos = {"persona": 0, "producto": 0, "captura": 0, "dificil": 0}
    
    for _, fila in df_preliminar.iterrows():
        # Limpieza absoluta de la columna para machear nombres exactos de archivos
        sala_origen = str(fila['sala_origen']).lower().strip()
        tipo_original = str(fila['tipo']).lower().strip()
        
        # APLICACIÓN FILTRO 4 (Tus hallazgos visuales de plantillas)
        # 1. Descartar Sala 3 de raíz usando el nombre exacto de su archivo
        if "sala-3" in sala_origen or "sala3" in sala_origen:
            descartes_visuales_manuales += 1
            continue
            
        # 2. Descartar Sala 7 si NO contiene una persona real
        if "sala-7" in sala_origen or "sala7" in sala_origen:
            if "pers" not in tipo_original:
                descartes_visuales_manuales += 1
                continue
            
        # Si supera el Filtro 4 de discrepancia visual humana
        casos_validos.append(fila)
        
        # CLASIFICACIÓN PASO 3 (Normalización analítica por categorías oficiales)
        # Mapeamos 'cuerpo' y 'con_marco' como 'persona' porque son usuarios vistiendo la prenda
        if "pers" in tipo_original or "cuer" in tipo_original or "con_" in tipo_original:
            conteo_tipos["persona"] += 1
        elif "prod" in tipo_original:
            conteo_tipos["producto"] += 1
        elif "capt" in tipo_original:
            conteo_tipos["captura"] += 1
        else:
            conteo_tipos["dificil"] += 1

    # Guardar el set oficial limpio de la medición
    if casos_validos:
        df_final = pd.DataFrame(casos_validos)
        df_final.to_csv(ARCHIVO_FINAL_LIMPIO, index=False)
        total_final_medicion = len(df_final)
    else:
        total_final_medicion = 0

    print("📊 [PASO 2] MÉTRICAS FINALES CORRECTAS:")
    print("-" * 50)
    print(f"Casos recibidos de las 7 salas                       : {casos_recibidos_iniciales}")
    print(f"Descartados: la foto salía del catálogo             : {descartes_catalogo_auto}")
    print(f"Descartados: el id_correcto no existe en products.csv: {descartes_fantasma}")
    print(f"Descartados: foto repetida entre dos salas           : {descartes_duplicados}")
    print(f"Descartados: mirando las dos imágenes (Filtro 4)     : {descartes_visuales_manuales}")
    print(f"Casos finales que entran a la medición               : {total_final_medicion}")
    print("-" * 50)
    
    print("\n📊 [PASO 3] DISTRIBUCIÓN DE TIPOS CORREGIDA:")
    print("-" * 50)
    for tipo, num in conteo_tipos.items():
        print(f" • {tipo.ljust(10)}: {num} casos")
    print("="*60)

if __name__ == "__main__":
    cerrar_auditoria_completa()
