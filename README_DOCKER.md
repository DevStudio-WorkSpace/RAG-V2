# Ejecución con Docker y Verificación — RAG Visual Sublitex

Guía rápida y directa para compilar, levantar y verificar el stack completo (**FastAPI + Qdrant + Next.js**) con Docker.

---

## 1. Requisitos previos

- **Docker Desktop** (o Docker Engine en Linux) en ejecución.
- Tener clonado el repositorio y situarse en la raíz del proyecto:
  ```bash
  cd C:\Users\lucia\Downloads\RAG-V2\RAG-V2
  ```

---

## 2. Levantar el stack completo

Construye las imágenes e inicia los 3 servicios en segundo plano:

```bash
docker compose up --build -d
```

_(Si usas versión antigua de Docker, usa `docker-compose up --build -d`)_

### Servicios que se levantan:

| Servicio        | Contenedor          | Puerto local   | Descripción                              |
| --------------- | ------------------- | -------------- | ---------------------------------------- |
| **Qdrant**      | `sublitex_qdrant`   | `6333`, `6334` | Base de datos vectorial                  |
| **API Backend** | `sublitex_api`      | `8000`         | FastAPI (Motores CLIP, OpenCLIP, SigLIP) |
| **Frontend**    | `sublitex_frontend` | `3000`         | Interfaz web Next.js                     |

---

## 3. Verificación rápida (Paso a Paso)

### Paso 1: Comprobar estado de los contenedores

```bash
docker compose ps
```

**Resultado esperado:** Los tres contenedores deben figurar en estado `Up` / `running`.

---

### Paso 2: Verificar la base vectorial (Qdrant)

Ejecuta en terminal o navegador:

```bash
curl http://localhost:6333/dashboard
```

O visita en tu navegador: [http://localhost:6333/dashboard](http://localhost:6333/dashboard).

---

### Paso 3: Verificar la API (Healthcheck)

```bash
curl http://localhost:8000/health
```

**Resultado esperado (JSON):**

```json
{
  "status": "ok",
  "total_productos": 284,
  "indices_disponibles": ["clip", "openclip", "siglip"],
  "qdrant": {
    "status": "connected",
    "total_puntos": 284
  }
}
```

Documentación interactiva disponible en: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Paso 4: Probar una búsqueda real por imagen en la API

Envía cualquier imagen de prueba para validar que los modelos carguen y calculen el Top 5:

```bash
curl -X POST "http://localhost:8000/search/image" -F "file=@data/images_normalized/SBX-01-0001.jpg" -F "top_k=5" -F "modelo=clip"
```

**Resultado esperado:** Un JSON con los 5 mejores resultados, `id`, `score`, `url` y `nombre_original`.

---

### Paso 5: Verificar el Frontend Web

Abre en tu navegador:
👉 **[http://localhost:3000](http://localhost:3000)**

1. Accede a la pestaña **Búsqueda / Search**.
2. Arrastra o sube una imagen de una camiseta deportiva.
3. Comprueba que muestre los resultados visualmente coincidentes del catálogo.

---

## 4. Comandos útiles de mantenimiento

### Ver logs en tiempo real:

```bash
# Todos los servicios
docker compose logs -f

# Solo API
docker compose logs -f api

# Solo Frontend
docker compose logs -f frontend
```

### Reiniciar un servicio específico:

```bash
docker compose restart api
```

### Detener todo el stack:

```bash
docker compose down
```

### Detener y borrar volúmenes (limpieza total):

```bash
docker compose down -v
```
