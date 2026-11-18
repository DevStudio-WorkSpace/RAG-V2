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
| Índices | En el backup restaurado se comprobó que los 577 IDs de `ids.npy` coinciden en orden con `products.csv`; Qdrant restauró 577 puntos y la búsqueda vectorial controlada recuperó el primer ID. | No se volvió a auditar en esta sesión la calidad de todos los índices comparativos ni H1 vs. H2. |
| Búsqueda | El frontend llama /search/image mediante el proxy; el flujo normal usa CLIP y Qdrant. Staging informó 577 productos/vectores, sin desfase. | Los modos `.npy` permanecen para baseline histórico; contrato y cobertura de rutas antiguas aún requieren revisión. |
| Modelo | API y frontend usan `clip` por defecto; es la única opción compatible con la colección Qdrant y el arranque solo precarga CLIP. Verificado el 2026-11-09 | Medición inicial en staging: p50 5898.3 ms y p95 9766.8 ms entre 8 respuestas exitosas; 2/10 `ReadTimeout`. Ampliar muestra y carga antes de fijar SLO. [Evidencia](../evidencias/latencia-staging-2026-11-11.txt) |
| Autenticación | Dependencias de cliente/admin, compare_digest, CORS explícito; clave en proxy servidor | Pruebas negativas y de configuración en el despliegue objetivo |
| Protección de recursos | `/search/image` aplica límite de subida y rate limit; los aliases `/search/image/qdrant` y `/search/image/v2` comparten la misma función protegida. | Rate limit en memoria por IP; confirmar comportamiento detrás de proxy y diseñar retención periódica de consultas si se requiere operación continua. |
| TLS | Caddyfile tiene auto_https off y escucha :80 | Dominio/certificado y prueba HTTPS. La casilla TLS marcada no describe esta configuración |
| Contenedores | API no-root; redes separadas; Qdrant enlazado a localhost; recursos y rotación de logs declarados | Frontend no declara USER. No afirmar que todos son no-root; comprobar permisos de escritura de data para API |
| Build | `frontend/package-lock.json` existe y el Dockerfile ejecuta `npm ci`; API y frontend declaran usuario no-root; Qdrant tiene versión fija. | La evidencia del build limpio es histórica; repetir build completo con el estado actual antes de publicar. |
| Salud | El endpoint `/health` consulta Qdrant y reporta conteo de puntos; Compose usa HTTP 200 como healthcheck. | La respuesta actual fija `desfase_detectado=false` por contrato y no demuestra la carga efectiva de CLIP; verificarlo explícitamente en el despliegue objetivo. |
| Monitoreo | Compose independiente y docs/despliegue/MONITOREO.md presentes | Levantar, configurar monitores y demostrar alerta/recuperación. La alternativa scripts/health_alert.py documentada no existe |
| Evaluación | JSON guardado: H2 44/50 Top1 (88%), 48/50 Top5 (96%), media 4594.1 ms; medición adicional p50/p95 en staging con CLIP | H1 tiene n=0: no hay comparación H1/H2. Falta revisión humana vigente; la muestra de latencia es pequeña y tuvo 20% de timeout, no representa SLO ni carga multiusuario. [Evidencia](../evidencias/latencia-staging-2026-11-11.txt) |
| Banco de evaluación | Hay consultas en data/consultas y 50 filas en comparación | Falta evaluation/consultas_hito2.csv usado por compare_hito1_hito2.py; su fallback apunta a imágenes AIM antiguas |
| Interfaz de evaluación | api/evaluacion.py existe pero main.py no monta su router; /eval muestra un muestrario | Conectar flujo de evaluación y persistencia canónica; hoy apunta a proyectoA/Search-10 y usa tres juicios distintos de los cuatro requeridos |

También hay divergencias de contrato: /search/image devuelve un objeto con resultados (salvo legacy), mientras AGENTS.md describe una lista; search_engine.py conserva fallback a index_embeddings.npy y solo valida cantidades de IDs, sin exigir su igualdad posicional con el CSV. Resolver estos puntos sin crear nuevos motores o índices. La nomenclatura SBX actual y los modelos comparativos requieren conciliarse con los requisitos AIM/CLIP del archivo de reglas, sin renombrar el catálogo unilateralmente.

## Revisión de los cinco archivos pendientes originales

1. `.gitignore` y `.dockerignore`: exclusiones de backups coherentes con el objetivo; `*.tar.gz` es una exclusión global, más amplia que backups/. Pueden aislarse en un commit pequeño tras revisión del equipo.
2. `scripts/backup.sh`: se corrigió y probó el 2026-11-12 en la VM. Crea y descarga un snapshot oficial de Qdrant, empaqueta catálogo/índices/imágenes normalizadas, comprueba el tar y publica el archivo final al terminar. Falla si falta `QDRANT_API_KEY` o el snapshot/datos requeridos; no copia `qdrant_data/` en caliente. Se restauró el snapshot en un Qdrant temporal y se verificaron 577 puntos, el conjunto exacto de IDs, imágenes citadas por CSV y una búsqueda vectorial. Pendiente programar el backup, guardar una copia fuera de la VM y repetir la recuperación en el entorno final. [Evidencia](../evidencias/backup-restauracion-2026-11-12.txt).
3. `docs/despliegue/PRODUCCION_SERVER.md`: se actualizó el 2026-11-12 para describir el backup por snapshot y la restauración aislada probada. La restauración no debe hacerse sobre la colección activa durante un simulacro. Sigue pendiente probar recuperación en el entorno definitivo. Revisar aparte los comandos históricos de localhost:8000, porque Compose solo expone la API dentro de la red Docker.
4. `docs/propuestas/PROPUESTA_OPERACIONES_BACKUP_ROLLBACK.md`: contiene otra implementación, menos estricta, que copia almacenamiento Qdrant en caliente y tolera errores. Dejar una única guía vigente y retirar o identificar claramente la propuesta como obsoleta.
5. Rollback: Compose asigna tags configurables a API/frontend. El 2026-11-09 se probó en VirtualBox el retorno entre `rollback-candidate` y `rollback-base` con `--no-build --pull never --no-deps`; health 200, 577 productos/embeddings y Top 1 SBX-01-0001 antes y después. Qdrant conservó ID, hora de inicio y bind mount durante el ciclo con `--no-deps`. La primera reconciliación sin `--no-deps` sí recreó Qdrant, por lo que la guía ahora exige esa opción y health previo. La restauración aislada del backup se comprobó el 2026-11-12; siguen sin probarse producción y compatibilidad ante cambios incompatibles de esquema/datos. [Evidencia](../evidencias/rollback-2026-11-09.txt).

**Recomendación de commit:** separar el backup/restauración local validado de los pendientes de operación externa. No declarar completos programación, copia fuera del servidor ni monitoreo de producción. El rollback por tags y la restauración aislada tienen evidencias distintas. Esta revisión no hizo commit ni push.

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

## Límites de verificación de la auditoría inicial (2026-11-04)

## Actualización — backup y restauración aislada (2026-11-12)

- VM accesible por SSH; staging activo. El backup se generó desde la copia de
  pruebas con un script sincronizado desde el repositorio. Archivo de 526 MiB,
  con SHA-256 registrado en la evidencia; no se expusieron claves.
- Se extrajo el archivo y se restauró la colección en un contenedor Qdrant
  temporal, separado de la colección de staging. Los 577 IDs restaurados
  coincidieron con `products.csv` e `ids.npy`; las 577 imágenes referidas por
  CSV estaban presentes. El vector correspondiente al primer ID recuperó
  `SBX-01-0001` como Top 1. La búsqueda normal por el proxy/frontend activo
  también devolvió `SBX-01-0001`.
- Se retiraron solo el contenedor, volumen y carpeta temporal creados para el
  simulacro. El staging siguió saludable; el archivo de backup se conserva en
  `backups/` dentro de la VM. El disco quedó al 93 % (2.2 GiB libres): copiar el
  backup a almacenamiento externo y revisar capacidad antes de nuevos ciclos.
- Esta prueba cierra la validación local de creación/restauración; no cierra
  programación, copia fuera del servidor, objetivos RPO/RTO ni restauración en
  producción. Ver [evidencia](../evidencias/backup-restauracion-2026-11-12.txt).

En aquella auditoría inicial de Windows/PowerShell no había `.venv`, Docker ni Bash en PATH. No se ejecutó inferencia ni restauración en ese turno. Esta limitación histórica quedó superada para la prueba de backup/restauración del 2026-11-12 en la VM; no implica que se hayan repetido allí todas las pruebas de la aplicación.
