# Evaluador del Buscador - Documento de Decisiones

## 01 · Entender el problema (Fase 1)

### P1 · ¿Por qué la medición anterior no sirve?
**Respuesta:**
La medición anterior (92%) presenta un grave problema de **fuga de datos (data leakage)** y **sobreajuste al dominio sintético (overfitting)**. Las consultas de prueba (`generar_consultas_hito2.py`) se construyeron aplicando transformaciones deterministas a nivel píxel (recortes porcentuales, rotación de matrices de color HSV, superposición alpha) sobre las mismas imágenes exactas que componen el índice del catálogo. Por tanto, la métrica resultante no evalúa la capacidad de recuperación visual ni la generalización del modelo ante variables del mundo real (arrugas en la tela, distorsión óptica, iluminación ambiental); únicamente mide su invariancia frente a transformaciones matemáticas artificiales. 
Metodológicamente, es el equivalente a evaluar si un alumno aprendió a razonar tomándole un examen con las mismas preguntas exactas que ya memorizó del libro de texto.

**En conclusión:** Ese 92% es una métrica engañosa. Solo demuestra que el buscador es muy bueno reconociendo sus propias imágenes cuando se les aplica un filtro digital. No sabemos realmente si el motor sirve o no sirve para el negocio, porque el examen con el que se lo evaluó no refleja cómo lo usaría un cliente en la vida real.

### P2 · ¿Qué dice el único dato honesto que hay?
**Respuesta:**
El archivo `evaluation.csv` revela lo siguiente:
1. **Los resultados en Posición 1:** Tuvieron scores muy altos (entre 0.69 y 0.80) pero recibieron juicios negativos ("Poco similar" o "No relacionado"). Ningún Top 1 le sirvió al usuario real.
2. **Sobre el score de 0.76 como "No relacionado":** Demuestra que el score de CLIP (similitud coseno) es una distancia matemática abstracta, no una probabilidad estadística. Dos imágenes pueden tener características generales similares (color, forma base) y sacar 0.76, pero diferenciarse en detalles semánticos clave para un humano (escudo, sponsor), siendo inútiles comercialmente. No se puede fijar un umbral de "buen score" a ciegas, porque el umbral de utilidad real se descubre midiendo con datos etiquetados por humanos.
3. **La fila repetida con juicios opuestos:** Un mismo resultado (AIM-P022-060) evaluado dos veces recibió "Muy similar" por un lado y "No relacionado" por el otro. Esto expone la **subjetividad y el sesgo del evaluador humano**. Demuestra la necesidad crítica de establecer reglas de juicio rígidas (como *Acierto / Sirve / No sirve* estipuladas en la Ficha) para estandarizar la evaluación.

**En conclusión:** El único dato real y humano que tenemos termina siendo estadísticamente inútil. Al no haber definido reglas estrictas de votación, la evaluación quedó a merced de la subjetividad de cada persona. Un buen *score* matemático no sirve de nada si no está atado a un criterio de negocio claro e inequívoco.

### P3 · ¿Qué hay que medir exactamente?
**Respuesta (Tres métricas):**
1. **Top 1 Exacto (Precision@1 estricta):** ¿El motor es capaz de clavar el diseño exacto que busco en la primera posición? (Mide el % de veces que el resultado 1 es juzgado como "Acierto").
2. **Utilidad del Top 5 (Precision@5 relajada):** ¿Los resultados del 2 al 5 son útiles para ofrecerle al cliente o son puro relleno/basura? (Mide la proporción de los 5 resultados que reciben un juicio útil, es decir, "Acierto" o "Sirve").
3. **Calidad del Ranking (NDCG@5):** ¿El motor está ordenando bien las opciones, poniendo lo excelente arriba y lo pasable más abajo? (Da puntaje perfecto si el "Acierto" está primero y los "Sirve" debajo, penalizando si se prioriza basura).

**En conclusión:** Medir el buscador no se trata solo de ver si le pega al primer resultado. Necesitamos saber si el sistema sirve como una herramienta de apoyo a la venta. Al usar estas tres métricas combinadas (exactitud estricta, utilidad relajada y calidad de ordenamiento) cubrimos todos los ángulos comerciales.

### P4 · ¿Qué es un caso de prueba válido?
**Respuesta:**
- **De dónde NO puede salir nunca:** Del propio catálogo del buscador (para no cometer el error de "fuga de datos" que destruyó la medición anterior en la P1).
- **De dónde SÍ puede salir:** De fuentes del mundo real: una foto sacada con el celular a una camiseta arrugada, una captura de pantalla de Instagram, o fotos de otra tienda online.
- **Cómo se garantiza que la respuesta correcta existe:** El humano que prepara la evaluación tiene que mirar el catálogo *antes*, asegurarse visualmente de que el diseño está ahí, y anotar el ID correcto. De esa forma, si el buscador no la encuentra, sabemos que el algoritmo falló y no que le pedimos algo imposible.
- **Por qué conviene usar tipos distintos:** Para medir la **robustez** del modelo ante diferentes problemas. Los clientes van a mandar imágenes de todo tipo (con mala luz, puestas en personas, dobladas en una cama). Si las 10 fotos de prueba son del mismo estilo, jamás sabremos en qué situaciones falla el motor.

**En conclusión:** Un buen dataset de prueba tiene que ser hostil, variado y provenir del mundo exterior. Solo evaluando el sistema contra casos reales (pero asegurándonos de antemano de que la respuesta correcta efectivamente existe en nuestra base de datos) podemos tener la certeza de que el buscador es realmente inteligente, y no que simplemente memorizó su propio catálogo.

---

## 02 · Decidir (Fase 2)

### D1 · Interfaz (¿Un caso a la vez o todos en lista? ¿Mouse o teclado?)
**Opción elegida:** Un caso a la vez + Atajos de teclado. La pantalla muestra la foto de consulta y un resultado a la vez. El evaluador vota rápido apretando "1", "2" o "3" en el teclado, y el sistema avanza automáticamente al siguiente.
**Opción descartada:** Mostrar los 10 casos en una lista gigante para scrollear y obligar a usar clicks de mouse (descartado porque requiere mucho esfuerzo físico y visual para evaluar cientos de casos seguidos).

### D2 · Persistencia (¿Dónde queda cada juicio si se cierra el navegador?)
**Opción elegida:** Guardado continuo en un archivo local (CSV). Cada vez que se presiona una tecla para votar, el voto se anexa al disco duro en tiempo real. Si se cierra la pestaña por error, no se pierde nada.
**Opción descartada:** Guardar todo en memoria (`st.session_state`) y tener un botón de "Exportar" al final (descartado porque un simple F5 accidental borra todo el trabajo de evaluación).

### D3 · Entrada (¿En qué formato entran los casos?)
**Opción elegida:** Leer un archivo prearmado (JSON/CSV) que lista las rutas de las fotos de consulta y sus IDs correctos. La app levanta ese lote automáticamente al iniciar.
**Opción descartada:** Que el usuario tenga que subir manualmente las 10 fotos con un botón de "Upload" cada vez que abre la app (descartado porque vuelve la evaluación lenta, tediosa y difícil de reproducir).

---

## 03 · Establecer las reglas (Fase 3)

Para evitar el error de subjetividad que descubrimos en la P2, las reglas estrictas de votación en la herramienta (que además irán escritas en la propia pantalla) serán:
- **Acierto:** Es el mismo diseño, aunque cambie el color, el año, el escudo o el sponsor.
- **Sirve:** No es el mismo, pero se lo mostrarías al cliente y lo aceptaría.
- **No sirve:** Es otro diseño.

---

## 04 · Buscarle el error a lo suyo (Fase 4)

**Pregunta:** Si alguien quisiera hacer trampa con nuestra herramienta para que el buscador saliera mejor de lo que es, ¿cómo lo haría?

**Respuesta:**
Si alguien quisiera inflar la métrica (incluso sin mentir descaradamente), podría hacerlo explotando estos sesgos:

1. **Sesgo de selección de casos (Cherry-picking)**
   - **Cómo infla la métrica:** Eligiendo 10 casos de prueba "fáciles" (fotos perfectas, centradas, con luz de estudio) y evitando los difíciles.
   - **Cómo se detecta:** Comparando la complejidad visual de las 10 fotos de prueba contra las fotos reales que suben los usuarios en producción.
   - **Cómo se evita:** Exigiendo que la selección sea aleatoria desde un log de usuarios, o forzando cuotas de dificultad (ej. obligar a incluir fotos arrugadas y mal iluminadas).

2. **Sesgo del evaluador (Fatiga o Complacencia)**
   - **Cómo infla la métrica:** A medida que el humano se cansa de evaluar cientos de casos, empieza a votar "Sirve" en automático a resultados mediocres para terminar rápido.
   - **Cómo se detecta:** Inyectando resultados "trampa" (casos de control obviamente malos) en el medio de la evaluación. Si los aprueba, está votando sin mirar.
   - **Cómo se evita:** Usando las reglas estrictas de la Fase 3 y pidiendo que la evaluación se haga en tandas cortas para evitar el cansancio mental.

3. **Sesgo de posición (Position Bias)**
   - **Cómo infla la métrica:** El humano asume que la máquina tiene razón. Si el buscador pone un resultado en la Posición 1, el evaluador es más permisivo y tiende a calificarlo mejor solo por estar arriba.
   - **Cómo se detecta:** Mostrando el mismo resultado pero en la última posición para ver si recibe la misma calificación.
   - **Cómo se evita:** Ocultando el número de "Score" en la herramienta para no sugestionar al juez, y exigiendo que mire a la prenda antes de mirar en qué posición quedó.
