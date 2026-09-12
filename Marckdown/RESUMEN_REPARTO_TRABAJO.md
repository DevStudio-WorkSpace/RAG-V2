# Resumen — Evaluador del Buscador (Grupo A)

## 📌 QUÉ SE TIENE QUE HACER

Construir una **herramienta web simple** donde una persona pueda evaluar los resultados del buscador visual. La herramienta debe:

1. **Mostrar una foto** (la consulta)
2. **Mostrar 5 resultados** del buscador (con imagen, nombre y score)
3. **3 botones por resultado**: Acierto / Sirve / No sirve
4. **Guardar cada clic** en un CSV
5. **Calcular 3 métricas**: Top 1, Top 5 y Utilidad
6. **Dividir métricas por tipo** de foto (persona, producto, captura, difícil)

---

## 👥 CÓMO REPARTIRLO EN 2

### **PERSONA A — "El que construye la pantalla"**

**Su trabajo:** Que la herramienta se vea bien y funcione.

| # | Tarea | Qué hace |
|---|-------|----------|
| 1 | Armar 10 casos de prueba | Busca 10 fotos reales de camisetas en Google, las guarda en `casos/`, y crea un `casos.csv` que indique cuál es el diseño correcto de cada foto |
| 2 | Crear la interfaz | Página HTML + JavaScript que muestre: foto grande arriba, 5 resultados abajo con sus datos |
| 3 | Agregar botones | En cada resultado, 3 botones: ✅ Acierto, 👍 Sirve, ❌ No sirve |
| 4 | Navegación | Botón "Siguiente" y contador "caso 7 de 10" |
| 5 | Probar persistencia | Verificar que si cierra el navegador y vuelve, lo evaluado siga ahí |

**Resultado de Persona A:** Una pantalla funcional donde alguien puede hacer la evaluación.

---

### **PERSONA B — "El que conecta y mide"**

**Su trabajo:** Que los datos se guarden y se calculen las métricas.

| # | Tarea | Qué hace |
|---|-------|----------|
| 1 | Verificar la API | Levantar la API, comprobar que `/health` y `/search/image` funcionan |
| 2 | Crear el CSV | Definir la estructura `resultados.csv` con columnas: caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha |
| 3 | Guardado en tiempo real | Cada vez que alguien aprieta un botón, se guarda una fila EN ESE MOMENTO (no al final) |
| 4 | Script de métricas | Leer `resultados.csv` y calcular: Top 1 (% aciertos en posición 1), Top 5 (% al menos 1 acierto en top 5), Utilidad (promedio de aciertos+útiles de 0 a 5) |
| 5 | Métricas por tipo | Separar los números por: persona, producto, captura, difícil |
| 6 | Escribir README | Documento claro que diga: cómo levantar, cómo cargar casos, dónde está el CSV, qué significan los números |

**Resultado de Persona B:** Todo funciona por debajo y las métricas se calculan correctamente.

---

## 🔄 CÓMO TRABAJAN JUNTOS

```
Persona A (pantalla)          Persona B (datos)
        │                            │
        ├─ Arma 10 casos ──────────► Recibe casos.csv
        │                            │
        ├─ Crea interfaz             ├─ Verifica API
        │                            │
        ├─ Agrega botones ─────────► Conecta botones con guardado CSV
        │                            │
        ├─ Prueba persistencia       ├─ Prueba guardado en tiempo real
        │                            │
        └────────┬───────────────────┘
                 │
                 ▼
        HERRAMIENTA FUNCIONAL
                 │
                 ▼
        Métricas calculadas: Top 1, Top 5, Utilidad
                 │
                 ▼
        README listo para el lunes
```

---

## ⚠️ REGLAS CLAVE

1. **NO tocar** el buscador, embeddings ni products.csv
2. **NO usar** imágenes del catálogo para los casos de prueba
3. **ANOTAR** cada uso de IA en AI_LOG.md
4. **Si se traban 40+ minutos** → avisar al coordinador
5. **AMBOS** deben poder explicar todo el código

---

## 🎯 LO QUE EL COORDINADOR VA A PROBAR EL LUNES

1. ✅ Levantar la herramienta siguiendo solo el README
2. ✅ Cargar 10 casos y evaluarlos
3. ✅ Cerrar navegador a la mitad → lo evaluado debe seguir ahí
4. ✅ Abrir resultados.csv → filas completas
5. ✅ Ver 3 números (total y por tipo de foto)
6. ✅ Preguntar a cada uno: "¿Cómo se calcula el Top 5?"

---

*Resumen para repartir el trabajo entre 2 personas*
