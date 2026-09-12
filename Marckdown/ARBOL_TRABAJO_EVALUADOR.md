# Árbol de Trabajo — Evaluador del Buscador (Grupo A)

## 🎯 Objetivo
Construir una herramienta que permita evaluar los resultados del buscador visual y calcular métricas objetivas (Top 1, Top 5, Utilidad).

---

## 📋 ESTRUCTURA DEL ÁRBOL

```
EVALUADOR DEL BUSCADOR
├── 1. PREPARACIÓN
│   ├── 1.1 Levantar la API
│   │   ├── Verificar GET /health
│   │   ├── Anotar: productos y embeddings
│   │   └── Verificar que sean iguales
│   │
│   ├── 1.2 Probar la API a mano
│   │   ├── Swagger (GET /docs)
│   │   ├── Postman o curl
│   │   └── Ver JSON de respuesta
│   │
│   └── 1.3 Armar 10 casos de prueba
│       ├── Buscar diseños en data/images_normalized/
│       ├── Encontrar fotos reales en Google
│       ├── Guardar en casos/caso-001.jpg ...
│       └── Crear casos.csv (caso, id_correcto, tipo)
│
├── 2. DESARROLLO DE LA PANTALLA
│   ├── 2.1 Interfaz HTML/JS (o Next.js)
│   │   ├── Arriba: foto de consulta (grande)
│   │   ├── Abajo: 5 resultados en fila
│   │   ├── Cada resultado: imagen + nombre + score
│   │   └── Indicador: "caso X de 10"
│   │
│   ├── 2.2 Los 3 botones por resultado
│   │   ├── ✅ Acierto: mismo diseño (aunque cambie color/año/escudo)
│   │   ├── 👍 Sirve: no es el mismo, pero se lo mostrarías al cliente
│   │   └── ❌ No sirve: es otro diseño
│   │
│   └── 2.3 Botón "Siguiente"
│       └── Pasa al siguiente caso
│
├── 3. GUARDAR RESULTADOS
│   ├── 3.1 Guardar cada clic en resultados.csv
│   │   ├── Columnas: caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha
│   │   └── Guardar EN EL MOMENTO del clic (no al final)
│   │
│   └── 3.2 Persistencia
│       └── Si el navegador se cierra, el trabajo hecho no se pierde
│
├── 4. CALCULAR MÉTRICAS
│   ├── 4.1 Los 3 números principales
│   │   ├── Top 1: % casos donde posición 1 recibió "Acierto"
│   │   ├── Top 5: % casos donde hubo "Acierto" en cualquiera de las 5 posiciones
│   │   └── Utilidad: promedio de cuántos de 5 resultados recibieron "Acierto" o "Sirve" (0 a 5)
│   │
│   └── 4.2 División por tipo de foto
│       ├── persona
│       ├── producto
│       ├── captura
│       └── difícil
│
└── 5. DOCUMENTACIÓN
    └── 5.1 README
        ├── Cómo se levanta
        ├── Cómo se cargan los casos
        ├── Dónde queda el CSV
        └── Qué significan los 3 números
```

---

## 👥 REPARTO EN 2 PERSONAS

### Persona A (Frontend + Casos de Prueba)
| Tarea | Descripción | Tiempo Est. |
|-------|-------------|-------------|
| Armar los 10 casos de prueba | Buscar fotos reales de camisetas en Google, asociarlas a IDs del catálogo | 2-3 horas |
| Crear la interfaz HTML/JS | Pantalla con foto grande arriba, 5 resultados abajo, botones | 3-4 horas |
| Implementar botones | Acierto / Sirve / No sirve por cada resultado | 1-2 horas |
| Botón "Siguiente" + avance | Navegación entre casos, indicador "caso X de 10" | 1 hora |
| Verificar persistencia | Probar que si se cierra el navegador, no se pierde el trabajo | 1 hora |

**TOTAL Persona A: ~8-11 horas**

### Persona B (Backend + Métricas + Documentación)
| Tarea | Descripción | Tiempo Est. |
|-------|-------------|-------------|
| Verificar que la API funcione | Levantar API, probar /health y /search/image | 1-2 horas |
| Crear CSV de resultados | Estructura: caso, id_correcto, posicion, id_resultado, score, juicio, quien, fecha | 2-3 horas |
| Guardar cada clic en tiempo real | Implementar que cada click se guarde inmediatamente en el CSV | 2-3 horas |
| Calcular las métricas | Script para calcular Top 1, Top 5 y Utilidad desde resultados.csv | 2-3 horas |
| División por tipo de foto | Segmentar métricas por: persona, producto, captura, difícil | 1-2 horas |
| Escribir README | Instrucciones claras para que otra persona lo levante | 1 hora |

**TOTAL Persona B: ~9-14 horas**

---

## ⏰ CRONOGRAMA SUGERIDO

### Día 1 (Viernes)
- **Mañana (4h):**
  - Persona B: Verificar API, probar endpoints
  - Persona A: Buscar y armar los 10 casos de prueba
  - Ambos: Definir la estructura del CSV y cómo se conectan

- **Tarde (4h):**
  - Persona A: Empezar la interfaz HTML/JS
  - Persona B: Crear la estructura del CSV y la lógica de guardado

### Día 2 (Sábado)
- **Mañana (4h):**
  - Persona A: Terminar interfaz + botones
  - Persona B: Implementar guardado en tiempo real + script de métricas

- **Tarde (4h):**
  - Ambos: Integrar interfaz con guardado CSV
  - Persona B: Calcular métricas + dividir por tipo de foto
  - Persona A: Escribir README

### Día 3 (Domingo)
- **Mañana (4h):**
  - Pruebas completas de la herramienta
  - Verificar persistencia (cerrar/abrir navegador)
  - Revisar que los números cuadren

- **Tarde (2h):**
  - Preparar demo para el lunes
  - Ambos: Repasar cómo explicar cada parte del código

---

## 📊 RESUMEN DE ENTREGABLES

1. **Carpeta casos/** con 10 fotos y casos.csv
2. **Interfaz HTML/JS** que muestre la pantalla descrita
3. **resultados.csv** con todas las evaluaciones
4. **Script de métricas** que calcule Top 1, Top 5 y Utilidad
5. **Métricas por tipo** (persona, producto, captura, difícil)
6. **README** con instrucciones completas

---

## ⚠️ REGLAS IMPORTANTES

- **NO tocar** el buscador, embeddings, products.csv ni el motor
- **NO usar** imágenes del catálogo como casos de prueba
- **ANOTAR** cada prompt de IA en AI_LOG.md
- Si se traban **más de 40 minutos**: avisar al coordinador
- **Ambos** deben poder explicar CUALQUIER parte del código

---

## 🎯 PRUEBA FINAL (Lo que hará el coordinador el lunes)

1. Seguir solo el README para levantar la herramienta
2. Cargar los 10 casos y evaluarlos
3. Cerrar el navegador a la mitad y volver a abrir
4. Verificar que el CSV tenga filas completas
5. Ver los 3 números (total y por tipo de foto)
6. Preguntar a cada uno cómo se calcula el Top 5

---

*Árbol de trabajo generado para el Grupo A — Evaluador del Buscador*
