# CÓMO EJECUTAR EL EVALUADOR

Como tenés esta carpeta guardada como un "respaldo" en tu Escritorio, para poder ejecutarla y que encuentre las fotos, tenés que seguir estos pasos:

## PASO 1: Devolver la carpeta al proyecto
1. Copiá esta carpeta entera (Investigacion).
2. Pegala adentro de la carpeta original de tu proyecto (C:\Users\PAOLO\Documents\TRABAJOS\RAG-V2).

## PASO 2: Encender el Buscador (API)
1. Abrí tu editor (VS Code) o una terminal en la carpeta de tu proyecto (RAG-V2).
2. Asegurate de tener activado tu entorno virtual (si usás uno).
3. Ejecutá el siguiente comando para prender el motor:
   uvicorn api.main:app --host 0.0.0.0 --port 8000
*(Importante: No cierres esta terminal, si la cerrás, el buscador se apaga).*

## PASO 3: Encender el Evaluador (Streamlit)
1. Abrí **otra terminal nueva** (dejando la anterior corriendo en segundo plano).
2. Entrá a la carpeta que acabás de pegar:
   cd Investigacion
3. Encendé la pantalla interactiva:
   streamlit run evaluador.py

Se abrirá tu navegador automáticamente y ya podrás empezar a votar usando el 1, 2 o 3 de tu teclado.
