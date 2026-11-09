# Sala 6: diagnóstico y punto de partida para el equipo

Fecha: 2026-11-04. Rama revisada: `sala-6`. Base: `7e6b42c2`.
Alcance: revisión de requisitos disponibles, código de búsqueda/API/interfaz, datos, evaluación, despliegue y cambios sin commit. Sin modificar funcionalidad ni realizar commits.

**Actualización posterior a la auditoría:** se habilitó una copia aislada en VirtualBox y se ejecutaron pruebas reales. Build API/frontend correcto, IDs alineados, 17/17 pruebas de integración correctas y Qdrant con 577 puntos y Top 1 exacto verificado. Se corrigieron permisos de caché y el 422 sin archivo; se añadió configuración de staging y precarga opcional de modelos extra. Ver [guía y resultados](STAGING_VIRTUALBOX.md). Los límites de ejecución descritos al final corresponden a la auditoría inicial de Windows y ya no impiden probar en la VM. No se cerraron automáticamente las casillas de producción ni se realizaron commits.

**Actualización de implementación — 2026-11-05:** por instrucción del usuario,
`POST /search/image` consulta Qdrant con CLIP y recuperación amplia antes del
reranking; el arranque valida o crea la colección y migra los `.npy` solo si
está vacía. Las rutas `/search/image/qdrant` y `/search/image/v2` quedaron como
alias deprecated; los modos `.npy` son baseline de evaluación. Compose guarda
snapshots bajo `/qdrant/storage/snapshots`, dentro del volumen persistente, y la
recuperación solicita prioridad `snapshot` para que una colección nueva reciba
los puntos del respaldo. En esta sesión se validaron el esquema 512/Cosine,
búsqueda e IDs con Qdrant local, y el Compose se validó sintácticamente. La API
no estaba activa y el intérprete local no tiene instalados
`sentence-transformers` ni `pydantic-settings`: falta repetir las pruebas HTTP
y de restauración contra Qdrant en staging; este cambio no equivale a un
despliegue ni altera la evidencia de staging del 4 de noviembre.

## Veredicto

Se puede continuar en Sala 6, pero todavía no hay evidencia suficiente para declarar cerrada la operación ni autorizar producción. El punto de partida recomendado es una **base reproducible de staging privado**, con catálogo de 577 productos, backend/modelo explícitos y una búsqueda real verificada. Sala 6 se interpreta aquí como la rama actual y el trabajo operativo del checklist §3; no se encontró una especificación formal de esa sala.

Actualización 2026-11-05: el usuario descartó `TRABAJO.md` como requisito vigente después de revisar su historial. No es necesario recuperarlo para continuar Sala 6; consultar el alcance actualizado en `AGENTS.md`. `docs/planificacion/REQUERIMIENTOS_DESPLIEGUE.md` tiene secciones duplicadas y afirmaciones contradictorias: no basta con contar sus casillas marcadas.

## Lo comprobado en esta revisión

| Área | Evidencia actual | Qué falta para cerrarla |
| --- | --- | --- |
| Catálogo | 577 filas; columnas exactas; las 577 imágenes existen | Los 577 nombres son el ID y las 577 URLs usan ejemplo.com. §3.1 no está totalmente cerrado |
| Índices | embeddings.npy, clip y openclip: 577×512; siglip: 577×768; ids.npy: 577 elementos | Comprobar contenido y orden de IDs con NumPy y relación con los vectores. Igual cantidad no prueba alineación |
| Búsqueda | /api/search del frontend llama /search/image; este usa motores .npy | Qdrant existe como ruta separada; elegir y documentar backend canónico antes de migrar o retirar rutas |
| Modelo | API y frontend usan `clip` por defecto; es la única opción compatible con la colección Qdrant y el arranque solo precarga CLIP. Verificado el 2026-11-09 | Medir CPU antes de fijar valores de latencia (pendiente) |
| Autenticación | Dependencias de cliente/admin, compare_digest, CORS explícito; clave en proxy servidor | Pruebas negativas y de configuración en el despliegue objetivo |
| Protección de recursos | /search/image tiene límite de subida y rate limit | v2 y qdrant no aplican esos mismos controles. La retención se ejecuta con nuevas búsquedas, no con un proceso periódico |
| TLS | Caddyfile tiene auto_https off y escucha :80 | Dominio/certificado y prueba HTTPS. La casilla TLS marcada no describe esta configuración |
| Contenedores | API no-root; redes separadas; Qdrant enlazado a localhost; recursos y rotación de logs declarados | Frontend no declara USER. No afirmar que todos son no-root; comprobar permisos de escritura de data para API |
| Build | Dockerfiles e ignores presentes; Qdrant con versión fija | No existe package-lock.json y se usa npm install; falta validar build completo (el volumen persistente HF_HOME sí está en `docker-compose.yml`, validado con `docker compose config` el 2026-11-06) |
| Salud | Healthcheck Compose consulta HTTP de /health | No verifica desfase, carga efectiva del modelo ni disponibilidad de colección Qdrant |
| Monitoreo | Compose independiente y docs/despliegue/MONITOREO.md presentes | Levantar, configurar monitores y demostrar alerta/recuperación. La alternativa scripts/health_alert.py documentada no existe |
| Evaluación | JSON guardado: H2 44/50 Top1 (88%), 48/50 Top5 (96%), media 4594.1 ms | H1 tiene n=0: no hay comparación H1/H2. Falta revisión humana vigente y p50/p95; no confundir media con percentiles |
| Banco de evaluación | Hay consultas en data/consultas y 50 filas en comparación | Falta evaluation/consultas_hito2.csv usado por compare_hito1_hito2.py; su fallback apunta a imágenes AIM antiguas |
| Interfaz de evaluación | api/evaluacion.py existe pero main.py no monta su router; /eval muestra un muestrario | Conectar flujo de evaluación y persistencia canónica; hoy apunta a proyectoA/Search-10 y usa tres juicios distintos de los cuatro requeridos |

También hay divergencias de contrato: /search/image devuelve un objeto con resultados (salvo legacy), mientras AGENTS.md describe una lista; search_engine.py conserva fallback a index_embeddings.npy y solo valida cantidades de IDs, sin exigir su igualdad posicional con el CSV. Resolver estos puntos sin crear nuevos motores o índices. La nomenclatura SBX actual y los modelos comparativos requieren conciliarse con los requisitos AIM/CLIP del archivo de reglas, sin renombrar el catálogo unilateralmente.

## Revisión de los cinco archivos pendientes originales

1. `.gitignore` y `.dockerignore`: exclusiones de backups coherentes con el objetivo; `*.tar.gz` es una exclusión global, más amplia que backups/. Pueden aislarse en un commit pequeño tras revisión del equipo.
2. `scripts/backup.sh`: propuesta útil, pero pendiente de prueba Bash/Linux y simulacro de recuperación. Omite Qdrant y termina con éxito si no responde readiness, lo que puede producir un respaldo incompleto sin fallo. No carga .env: la clave debe exportarse al entorno del proceso programado. No exige todos los componentes del catálogo; basta con encontrar alguno. Falta programación, copia fuera del servidor, manifiesto/checksum y validación de MAX_BACKUPS (0 puede borrar todos). La rotación con ls/xargs falla con rutas con espacios. Conviene escribir archivo temporal y publicar solo al completar para no dejar respaldos parciales tras fallos. Parsear JSON por entrada estándar, sin incrustar la respuesta en código Python.
3. `docs/despliegue/PRODUCCION_SERVER.md`: dice que se comprime qdrant_data/, pero el script usa un snapshot y no incluye esa carpeta. Extraer el tar no importa el snapshot a Qdrant. Falta el procedimiento de recuperación del snapshot y una prueba con colección vacía. Los ejemplos localhost:8000 no corresponden a la API de Compose, que solo tiene expose; usar la ruta pública /api/health o una comprobación interna. curl -I usa HEAD y no sustituye la prueba GET. Los objetivos de latencia y memoria añadidos no tienen medición adjunta y contradicen docs/despliegue/MONITOREO.md.
4. `docs/propuestas/PROPUESTA_OPERACIONES_BACKUP_ROLLBACK.md`: contiene otra implementación, menos estricta, que copia almacenamiento Qdrant en caliente y tolera errores. Dejar una única guía vigente y retirar o identificar claramente la propuesta como obsoleta.
5. Rollback en ambas guías: los tags sublitex_api/frontend no están declarados como image en Compose. Etiquetar manualmente y luego reconstruir desde Git no demuestra recuperación de la imagen anterior. Definir imágenes versionadas reales y probar la vuelta a la versión anterior, incluyendo compatibilidad de datos.

**Recomendación de commit:** no presentar el lote actual como “backups y rollback completos”. Tras corregir guía/script y validar, separar respaldo/restauración, rollback y monitoreo en cambios revisables. Si el equipo necesita compartir antes el avance, puede versionarse explícitamente como borrador, manteniendo las casillas abiertas. Esta revisión no hizo staging, commit ni push.

## Reparto propuesto y criterios de aceptación

| Orden / responsable sugerido | Checklist | Entregable verificable |
| --- | --- | --- |
| 0. Coordinador + producto | §3.1 y requisitos | Confirmar staging o producción dentro del alcance vigente de AGENTS.md, catálogo SBX/577, backend y modelo; proporcionar nombres/URLs o declarar datos de demo; dejar Hito 3 fuera si sigue pospuesto |
| 1. Integración/backend | §3.2 | Registrar decisión de backend único y rutas experimentales; validar IDs por contenido/orden y todos los índices; fijar modelo en UI/API; conciliar contrato de respuesta |
| 2. Operaciones: backups | §3.4 respaldos | Script robusto + guía única + ejecución programada + copia fuera del VPS. Restaurar catálogo y colección Qdrant en entorno aislado y demostrar conteos, IDs y búsqueda correcta; acordar pérdida de datos y tiempo de recuperación tolerables |
| 3. Operaciones: despliegue/rollback | §3.4 build | Lockfile + npm ci, volumen HF, imágenes con tags trazables. Build limpio y retorno probado a una imagen anterior, sin depender de reconstrucción ni borrar volúmenes |
| 4. Infraestructura/seguridad | §3.3 | HTTPS real; revisar usuarios/permisos; mismos límites para todas las búsquedas; retención periódica. Evidencias 401/403/503, 413/429 y acceso exterior solo por rutas previstas |
| 5. Observabilidad | §3.4 monitoreo/alertas | Kuma ejecutándose; monitores API/frontend/Qdrant; notificación de fallo y recuperación probadas; medición independiente de recursos, errores y p95. Corregir referencia al script ausente |
| 6. QA + evaluadores | §3.5 + evaluación Hito 2 | Mismas 50 consultas, 10 por categoría, con id_correcto en catálogo; ejecutar H1/H2 y juicios humanos requeridos; publicar Top1/Top5 y p50/p95, separando clip/fusion y arranque frío/caliente |

Las tareas 2–6 pueden prepararse en paralelo por personas, después del acuerdo 0–1. Cada responsable debe adjuntar entorno, commit probado, comando/prueba, resultado y evidencia. No cerrar una casilla únicamente porque exista un archivo de instrucciones.

## Punto clave antes de repartir la ejecución

- [ ] Documento de alcance y decisiones aprobado por el equipo; requisitos recuperados.
- [ ] Cambios de operación revisados, con una sola guía de respaldo/restauración.
- [ ] Commit base identificable, construido en staging sin cambios locales ocultos.
- [ ] GET /api/health con 577 productos/vectores y sin desfase; verificar IDs aparte.
- [ ] Búsqueda real por el frontend y por API con clave, con ID esperado y rutas de imagen válidas.
- [ ] Pruebas de archivo inválido y <32 px devuelven 400; sin archivo también (File(...) actualmente puede dar 422); imagen externa no cierra el servidor.
- [ ] Responsables y aceptación de la tabla asignados; cada tarea en su rama y con evidencia.

Ese es el primer corte para repartir Sala 6 con una referencia común; la recuperación probada y las alertas son condiciones posteriores para cerrar operación. No hace falta volver a empezar ni regenerar índices solo por cambiar nombres/URLs.

## Límites de verificación de esta sesión

Windows/PowerShell: Python 3.14 disponible; sin .venv, Docker ni Bash en PATH. Validación sintáctica AST de api/, core/ y scripts/ correcta; git diff --check sin errores de whitespace. Leídos encabezados NPY sin deserializar ids.npy (dtype object); no se afirma validación del orden de sus valores. No se ejecutó inferencia, lint/build frontend ni restauración. El servicio en localhost:80 no respondió; no fue posible subir una consulta real con curl. Los resultados de calidad citados provienen de archivos históricos, no de una ejecución nueva ni necesariamente del código actual.
