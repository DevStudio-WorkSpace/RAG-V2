import os
import pandas as pd

PLANILLA_PRELIMINAR = "data/planilla_preliminar_auditada.csv"
ARCHIVO_FINAL_LIMPIO = "data/planilla_oficial_limpia.csv"

def cerrar_auditoria_dinamica():
    print("="*60)
    print("   AUDITORÍA EVOLUTIVA SUB-LITEX — RE-REVISIÓN DE SET")
    print("="*60)
    
    if not os.path.exists(PLANILLA_PRELIMINAR):
        print(f"❌ Error: No se encuentra {PLANILLA_PRELIMINAR}.")
        return
        
    df_preliminar = pd.read_csv(PLANILLA_PRELIMINAR)
    
    # 1. Valores fijos de la primera fase automática
    descartes_catalogo_auto = 5
    descartes_fantasma = 14
    descartes_duplicados = 10
    casos_recibidos_iniciales = 67
    
    casos_validos = []
    descartes_visuales_manuales = 0
    
    # Contadores oficiales Paso 3
    conteo_tipos = {"persona": 0, "producto": 0, "captura": 0, "dificil": 0}
    
    for _, fila in df_preliminar.iterrows():
        tipo_original = str(fila['tipo']).lower().strip()
        
        # NUEVA LÓGICA DINÁMICA (Tu criterio de auditor del futuro):
        # Si la celda contiene palabras de catálogos que sobrevivieron a la primera fase
        # o está vacía/inválida, se descarta por discrepancia/falso positivo.
        palabras_invalidas = ['exact', 'sin_m', 'sin m', 'catalogo', 'plantilla', 'vector', 'render']
        
        if any(p_inv in tipo_original for p_inv in palabras_invalidas) or tipo_original in ["", "nan"]:
            descartes_visuales_manuales += 1
            continue
            
        # Si la fila tiene una categoría real, se aprueba de forma automática sin importar la sala
        casos_validos.append(fila)
        
        # Mapeo y distribución analítica del Paso 3
        if "pers" in tipo_original or "cuer" in tipo_original or "con_" in tipo_original:
            conteo_tipos["persona"] += 1
        elif "prod" in tipo_original:
            conteo_tipos["producto"] += 1
        elif "capt" in tipo_original:
            conteo_tipos["captura"] += 1
        else:
            conteo_tipos["dificil"] += 1

    # Guardar la nueva planilla oficial en caliente
    if casos_validos:
        df_final = pd.DataFrame(casos_validos)
        df_final.to_csv(ARCHIVO_FINAL_LIMPIO, index=False)
        total_final_medicion = len(df_final)
    else:
        total_final_medicion = 0

    print("📊 [PASO 2] NUEVAS MÉTRICAS DEL SET MODIFICADO:")
    print("-" * 50)
    print(f"Casos recibidos inicialmente                      : {casos_recibidos_iniciales}")
    print(f"Descartados: la foto salía del catálogo             : {descartes_catalogo_auto}")
    print(f"Descartados: el id_correcto no existe en products.csv: {descartes_fantasma}")
    print(f"Descartados: foto repetida entre dos salas           : {descartes_duplicados}")
    print(f"Descartados: remanentes de catálogo / plantillas    : {descartes_visuales_manuales}")
    print(f"Casos finales netos que entran a la medición        : {total_final_medicion}")
    print("-" * 50)
    
    print("\n📊 [PASO 3] NUEVA DISTRIBUCIÓN POR TIPOS:")
    print("-" * 50)
    alerta_coordinador = False
    for tipo, num in conteo_tipos.items():
        print(f" • {tipo.ljust(10)}: {num} casos")
        if num < 8:
            alerta_coordinador = True
            
    if alerta_coordinador:
        print("\n⚠️ ALERTA: Siguen existiendo categorías por debajo del mínimo estadístico (< 8).")
    else:
        print("\n✅ ÉXITO: El set ahora es estadísticamente confiable en todas las categorías.")
    print("="*60)

if __name__ == "__main__":
    cerrar_auditoria_completa = cerrar_auditoria_dinamica()