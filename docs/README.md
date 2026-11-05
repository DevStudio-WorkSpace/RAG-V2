# Documentación del proyecto

Para incorporarse al equipo, leer primero el README de la raíz y después el estado de Sala 6. Los comandos de las guías se ejecutan desde la raíz del repositorio, salvo indicación expresa.

| Necesidad | Documento | Estado |
| --- | --- | --- |
| Saber qué falta y repartir tareas | [Estado de Sala 6](sala6/ESTADO_SALA6.md) | Auditoría con actualización tras las pruebas |
| Repetir las pruebas y entender su alcance | [Staging en VirtualBox o Docker directo](sala6/STAGING_VIRTUALBOX.md) | Entorno probado; 17/17 comprobaciones |
| Consultar los resultados registrados | [Evidencia de staging](evidencias/staging-2026-11-04.json) | Datos de la ejecución; no sustituye la evaluación completa |
| Consultar checklist y decisiones | [Requerimientos de despliegue](planificacion/REQUERIMIENTOS_DESPLIEGUE.md) | Contiene discrepancias pendientes señaladas en la auditoría |
| Preparar monitoreo | [Monitoreo](despliegue/MONITOREO.md) | Guía; alertas con script probadas en local, monitoreo pendiente de validación en VPS |
| Consultar despliegue y operación | [Servidor de producción](despliegue/PRODUCCION_SERVER.md) | En revisión: respaldo, restauración y rollback pendientes de prueba |
| Consultar instrucciones Docker anteriores | [Guía Docker](despliegue/README_DOCKER.md) | Referencia anterior; revisar puertos contra Compose actual |
| Entender la migración del catálogo | [Informe de producto y datos](informes/Productos_datos_refactorizacion.md) | Informe histórico; no representa por sí solo el estado actual |

## Organización

- `sala6/`: diagnóstico y pruebas de la etapa actual.
- `despliegue/`: guías de ejecución, servidor y monitoreo.
- `planificacion/`: checklist y decisiones de alcance.
- `informes/`: antecedentes y trabajo realizado.
- `propuestas/`: borradores locales pendientes de validar; pueden no estar incluidos en Git.
- `evidencias/`: resultados registrados, sin secretos.

`AGENTS.md` y `AI_LOG.md` permanecen en la raíz. `TRABAJO.md` se conserva únicamente en el historial y quedó descartado como requisito vigente por decisión del usuario del 2026-11-05; consultar el alcance actual en `AGENTS.md`. Esta organización no cambia los estados de los checklist ni las rutas del sistema.

La documentación propia del frontend sigue en `frontend/README.md` y `frontend/UI_SECCIONES.md`. Su archivo `AGENTS.md` conserva las instrucciones aplicables a ese directorio.
