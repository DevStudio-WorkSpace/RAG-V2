import os
import shutil
import pandas as pd

PLANILLA_OFICIAL = "data/planilla_oficial_limpia.csv"
CARPETA_ORIGEN_DISCORD = "evaluador/casos-de-todas-la-sala"
CARPETA_ENTREGA_FOTOS = "data/imagenes_oficiales_limpias"

def exportar_fotos_auditadas():
    print("="*60)
    print("   ASISTENTE DE EXPORTACIÓN: COPIADO DE IMÁGENES VALIDADAS")
    print("="*60)
    
    if not os.path.exists(PLANILLA_OFFICIAL := PLANILLA_OFICIAL):
        print(f"❌ Error: No existe la planilla oficial en {PLANILLA_OFICIAL}. Corre los filtros primero.")
        return

    # Crear o limpiar la carpeta de entrega local
    if os.path.exists(CARPETA_ENTREGA_FOTOS):
        shutil.rmtree(CARPETA_ENTREGA_FOTOS)
    os.makedirs(CARPETA_ENTREGA_FOTOS, exist_ok=True)

    df = pd.read_csv(PLANILLA_OFICIAL)
    total_casos = len(df)
    copiados_exito = 0
    no_encontrados = 0

    print(f"📋 Leyendo {total_casos} casos aprobados en el CSV oficial...")
    print("Buscando y renombrando archivos físicos de origen...\n")

    # Extensiones de imagen comerciales más comunes
    extensiones = ['.jpg', '.jpeg', '.png', '.JPG', '.PNG']

    for _, fila in df.iterrows():
        # Recuperamos el ID único global (ej: sala3_caso_01) y la sala
        caso_id_completo = str(fila['caso_id']).strip()
        sala_origen = str(fila['sala_origen']).strip()
        
        # Extraemos el nombre original del caso quitándole el prefijo de la sala
        # ej: de 'sala3_caso_01' extrae 'caso_01'
        partes = caso_id_completo.split('_', 1)
        nombre_base_archivo = partes[1] if len(partes) > 1 else caso_id_completo

        # Mapeamos el nombre de la carpeta según el formato real de Discord
        # Convierte 'Sala 3' en 'Sala-3'
        subcarpeta_sala = sala_origen.replace(" ", "-") 
        
        # Intentamos buscar en la ruta estándar 'Casos-Sala-X'
        ruta_buscar_carpeta = os.path.join(CARPETA_ORIGEN_DISCORD, f"Casos-{subcarpeta_sala.lower()}")
        if not os.path.exists(ruta_buscar_carpeta):
            # Intento alternativo por si la carpeta no lleva el prefijo 'Casos-'
            ruta_buscar_carpeta = os.path.join(CARPETA_ORIGEN_DISCORD, subcarpeta_sala)

        # Buscar el archivo físico probando las distintas extensiones
        archivo_encontrado = False
        for ext in extensiones:
            ruta_foto_origen = os.path.join(ruta_buscar_carpeta, f"{nombre_base_archivo}{ext}")
            
            if os.path.exists(ruta_foto_origen):
                # Destino final blindado para que no choque en la carpeta única
                nombre_foto_destino = f"{caso_id_completo}{ext}"
                ruta_foto_destino = os.path.join(CARPETA_ENTREGA_FOTOS, nombre_foto_destino)
                
                # Copiar archivo físico manteniendo sus metadatos
                shutil.copy2(ruta_foto_origen, ruta_foto_destino)
                copiados_exito += 1
                archivo_encontrado = True
                break
        
        if not archivo_encontrado:
            no_encontrados += 1
            print(f"⚠️ Alerta: No se encontró la foto física para {caso_id_completo} en su subcarpeta.")

    print("-" * 60)
    print(f"📊 PROCESO TERMINADO:")
    print(f" • Fotos copiadas y renombradas con éxito : {copiados_exito}")
    print(f" • Archivos físicos faltantes en carpetas   : {no_encontrados}")
    print(f"📁 Todo consolidado para tu revisión en   : {CARPETA_ENTREGA_FOTOS}")
    print("="*60)

if __name__ == "__main__":
    exportar_fotos_auditadas()
