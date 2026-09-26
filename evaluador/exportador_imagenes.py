import os
import shutil
import pandas as pd

PLANILLA_OFICIAL = "data/planilla_oficial_limpia.csv"
CARPETA_ORIGEN_DISCORD = "evaluador/casos-de-todas-la-sala"
CARPETA_ENTREGA_FOTOS = "data/imagenes_oficiales_limpias"

def exportar_fotos_posicional():
    print("="*60)
    print("   EXPORTADOR INTELIGENTE: EMPAREJAMIENTO SECUENCIAL DE FOTOS")
    print("="*60)
    
    if not os.path.exists(PLANILLA_OFICIAL):
        print(f"❌ Error: No existe {PLANILLA_OFICIAL}.")
        return

    if os.path.exists(CARPETA_ENTREGA_FOTOS):
        shutil.rmtree(CARPETA_ENTREGA_FOTOS)
    os.makedirs(CARPETA_ENTREGA_FOTOS, exist_ok=True)

    df = pd.read_csv(PLANILLA_OFICIAL)
    
    # Agrupamos las filas por sala para procesarlas en orden secuencial
    salas = df['sala_origen'].unique()
    copiados_exito = 0
    no_encontrados = 0

    print(f"📋 Analizando asignaciones para {len(salas)} salas activas...")

    for sala in salas:
        df_sala = df[df['sala_origen'] == sala].copy()
        
        # Determinar el nombre real de la subcarpeta física de Discord
        subcarpeta_sala = sala.replace(" ", "-")
        ruta_carpeta = os.path.join(CARPETA_ORIGEN_DISCORD, f"Casos-{subcarpeta_sala.lower()}")
        if not os.path.exists(ruta_carpeta):
            ruta_carpeta = os.path.join(CARPETA_ORIGEN_DISCORD, subcarpeta_sala)
            
        if not os.path.exists(ruta_carpeta):
            print(f"⚠️ Alerta: No se encontró la carpeta física para la {sala}")
            no_encontrados += len(df_sala)
            continue

        # Listar y ordenar todas las imágenes reales que están dentro de esa carpeta
        imagenes_reales = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        imagenes_reales.sort()  # Orden alfabético/secuencial estándar

        print(f" 📂 {sala}: Detectadas {len(imagenes_reales)} fotos reales para {len(df_sala)} registros del CSV.")

        # Emparejar fila por fila según la posición física en la carpeta
        for i, (_, fila) in enumerate(df_sala.iterrows()):
            caso_id_completo = str(fila['caso_id']).strip()
            
            if i < len(imagenes_reales):
                foto_origen_nombre = imagenes_reales[i]
                ruta_foto_origen = os.path.join(ruta_carpeta, foto_origen_nombre)
                
                # Conservamos la extensión real del archivo de Discord (.png o .jpg)
                _, ext = os.path.splitext(foto_origen_nombre)
                nombre_foto_destino = f"{caso_id_completo}{ext.lower()}"
                ruta_foto_destino = os.path.join(CARPETA_ENTREGA_FOTOS, nombre_foto_destino)
                
                # Copiar físicamente
                shutil.copy2(ruta_foto_origen, ruta_foto_destino)
                copiados_exito += 1
            else:
                no_encontrados += 1
                print(f"  ❌ Faltó foto física en la carpeta para el caso: {caso_id_completo}")

    print("-" * 60)
    print(f"📊 PROCESO TERMINADO CON EMPAREJAMIENTO INTEGRAL:")
    print(f" • Fotos copiadas y normalizadas con éxito: {copiados_exito}")
    print(f" • Casos sin imagen física disponible      : {no_encontrados}")
    print(f"📁 Paquete de revisión listo en: {CARPETA_ENTREGA_FOTOS}")
    print("="*60)

if __name__ == "__main__":
    exportar_fotos_posicional()
