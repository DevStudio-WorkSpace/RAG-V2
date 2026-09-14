# Evaluador del Buscador Visual

Este evaluador permite probar el funcionamiento del buscador visual utilizando imágenes externas y realizar una evaluación manual de los resultados obtenidos.

## Cómo levantar el proyecto

El proyecto necesita tres servicios funcionando al mismo tiempo.

Primero, desde la carpeta principal del proyecto, iniciar la API del buscador:

```bash
py -m uvicorn api.main:app --reload
```

La API estará disponible en:

`http://127.0.0.1:8000`

Luego, abrir una segunda terminal, entrar a la carpeta `evaluador` e iniciar el servidor del evaluador:

```bash
cd evaluador
py -m uvicorn server:app --reload --port 8001
```

El servidor del evaluador estará disponible en:

`http://127.0.0.1:8001`

Finalmente, abrir una tercera terminal dentro de la carpeta `evaluador` e iniciar la interfaz React:

```bash
npm install
npm run dev
```

La interfaz estará disponible en:

`http://localhost:5173`

## Cómo cargar los casos

Los casos de prueba son imágenes en formato JPG o PNG.

Para realizar una evaluación, ingresar a la interfaz, presionar el botón **Seleccionar archivo** y elegir una de las imágenes de prueba, por ejemplo `caso-001.jpg`.

Después, presionar **Buscar similares**. El sistema enviará la imagen al buscador visual y mostrará los productos encontrados.

Cada resultado debe ser evaluado utilizando uno de los tres botones disponibles: **Acierto**, **Sirve** o **No sirve**.

El procedimiento se repite con los casos desde `caso-001.jpg` hasta `caso-010.jpg`.

## Dónde se guarda el CSV

Las evaluaciones realizadas desde la interfaz se guardan automáticamente en:

`evaluador/resultados.csv`

Cada vez que se selecciona una evaluación, esta se registra inmediatamente en el archivo CSV.

El archivo almacena la consulta realizada, el ID y nombre del producto encontrado, su posición, score y la evaluación asignada.

## Significado de las tres evaluaciones

**Acierto:** el resultado corresponde al producto correcto que se esperaba encontrar.

**Sirve:** el resultado no corresponde exactamente al producto buscado, pero presenta suficiente similitud visual para considerarse útil.

**No sirve:** el resultado no corresponde al producto buscado y tampoco presenta suficiente similitud visual para considerarse útil.
