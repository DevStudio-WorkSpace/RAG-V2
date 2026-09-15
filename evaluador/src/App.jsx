import { useState } from "react";
import "./App.css";

function App() {
  const [archivo, setArchivo] = useState(null);
  const [preview, setPreview] = useState(null);
  const [resultados, setResultados] = useState([]);
  const [evaluaciones, setEvaluaciones] = useState({});
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  // ==========================================
  // CARGAR EVALUACIONES GUARDADAS DEL CSV
  // ==========================================

  const cargarEvaluacionesGuardadas = async (nombreArchivo) => {
    try {
      const respuesta = await fetch(
        `http://127.0.0.1:8001/evaluaciones/${encodeURIComponent(
          nombreArchivo
        )}`
      );

      if (!respuesta.ok) {
        throw new Error(
          "No se pudieron cargar las evaluaciones guardadas."
        );
      }

      const data = await respuesta.json();

      const evaluacionesRecuperadas = {};

      data.evaluaciones.forEach((item) => {
        evaluacionesRecuperadas[item.resultado_id] =
          item.evaluacion;
      });

      setEvaluaciones(evaluacionesRecuperadas);
    } catch (error) {
      console.error(error);

      setError(
        "No se pudieron recuperar las evaluaciones anteriores."
      );
    }
  };

  // ==========================================
  // SELECCIONAR IMAGEN
  // ==========================================

  const seleccionarImagen = async (e) => {
    const imagen = e.target.files[0];

    if (!imagen) return;

    // Liberar preview anterior
    if (preview) {
      URL.revokeObjectURL(preview);
    }

    const nuevaPreview = URL.createObjectURL(imagen);

    setArchivo(imagen);
    setPreview(nuevaPreview);

    setResultados([]);
    setEvaluaciones({});
    setError("");

    // Recuperar evaluaciones anteriores
    await cargarEvaluacionesGuardadas(imagen.name);
  };

  // ==========================================
  // ELIMINAR IMAGEN SELECCIONADA
  // ==========================================

  const eliminarImagen = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setArchivo(null);
    setPreview(null);
    setResultados([]);
    setEvaluaciones({});
    setError("");

    // Limpiar también el input file
    const input = document.getElementById("selector-imagen");

    if (input) {
      input.value = "";
    }
  };

  // ==========================================
  // BUSCAR IMÁGENES SIMILARES
  // ==========================================

  const buscarSimilares = async () => {
    if (!archivo) {
      setError("Selecciona una imagen.");
      return;
    }

    try {
      setCargando(true);
      setError("");
      setResultados([]);

      const formData = new FormData();

      formData.append("file", archivo);
      formData.append("modo", "auto");
      formData.append("modelo", "clip");

      const respuesta = await fetch(
        "http://127.0.0.1:8000/search/image",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!respuesta.ok) {
        throw new Error(
          "Error al buscar imágenes similares."
        );
      }

      const data = await respuesta.json();

      console.log("Respuesta API:", data);

      setResultados(data.resultados || []);

      // Recuperar nuevamente las evaluaciones
      // después de obtener los resultados.
      await cargarEvaluacionesGuardadas(archivo.name);
    } catch (error) {
      console.error(error);

      setError(
        "No se pudo realizar la búsqueda."
      );
    } finally {
      setCargando(false);
    }
  };

  // ==========================================
  // GUARDAR EVALUACIÓN
  // ==========================================

  const evaluarResultado = async (
    resultado,
    posicion,
    evaluacion
  ) => {
    // Si ya fue evaluado, no permitir duplicarlo.
    if (evaluaciones[resultado.id]) {
      return;
    }

    try {
      setError("");

      const respuesta = await fetch(
        "http://127.0.0.1:8001/evaluar",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            consulta: archivo?.name || "sin_nombre",
            resultado_id: resultado.id,
            nombre: resultado.nombre || "",
            posicion: posicion,
            score: Number(resultado.score),
            evaluacion: evaluacion,
          }),
        }
      );

      if (!respuesta.ok) {
        throw new Error(
          "No se pudo guardar la evaluación."
        );
      }

      const data = await respuesta.json();

      console.log("Evaluación guardada:", data);

      setEvaluaciones((anteriores) => ({
        ...anteriores,
        [resultado.id]: evaluacion,
      }));
    } catch (error) {
      console.error(error);

      setError(
        "La evaluación no pudo guardarse."
      );
    }
  };

  // ==========================================
  // CONVERTIR SCORE A PORCENTAJE
  // ==========================================

  const convertirPorcentaje = (score) => {
    const numero = Number(score);

    if (Number.isNaN(numero)) {
      return "0.00";
    }

    return (numero * 100).toFixed(2);
  };

  // ==========================================
  // INTERFAZ
  // ==========================================

  return (
    <main className="contenedor">
      <h1>Evaluador del buscador</h1>

      <p className="descripcion">
        Selecciona uno de los casos de prueba y evalúa
        los resultados obtenidos por el buscador visual.
      </p>

      {/* ======================================
          ZONA DE CONSULTA
      ====================================== */}

      <section className="buscador">
        {!archivo && (
          <div className="zona-seleccion">
            <div className="icono-imagen">
              +
            </div>

            <h2>Selecciona una imagen</h2>

            <p>
              Carga uno de los casos de prueba en formato
              JPG, JPEG o PNG.
            </p>

            <label
              htmlFor="selector-imagen"
              className="boton-seleccionar"
            >
              Seleccionar archivo
            </label>

            <input
              id="selector-imagen"
              className="input-archivo"
              type="file"
              accept=".jpg,.jpeg,.png"
              onChange={seleccionarImagen}
            />
          </div>
        )}

        {archivo && (
          <div className="imagen-seleccionada">
            <div className="contenedor-preview">
              <img
                src={preview}
                alt="Imagen seleccionada"
                className="preview"
              />
            </div>

            <div className="informacion-consulta">
              <span className="etiqueta-consulta">
                IMAGEN SELECCIONADA
              </span>

              <h2>{archivo.name}</h2>

              <p>
                La imagen está lista para realizar la
                búsqueda visual.
              </p>

              <div className="acciones-consulta">
                <button
                  type="button"
                  onClick={buscarSimilares}
                  disabled={cargando}
                  className="boton-buscar"
                >
                  {cargando
                    ? "Buscando..."
                    : "Buscar similares"}
                </button>

                <button
                  type="button"
                  onClick={eliminarImagen}
                  disabled={cargando}
                  className="boton-eliminar"
                >
                  Eliminar imagen
                </button>
              </div>
            </div>
          </div>
        )}

        {error && (
          <p className="error">
            {error}
          </p>
        )}
      </section>

      {/* ======================================
          RESULTADOS
      ====================================== */}

      {resultados.length > 0 && (
        <section className="resultados">
          <div className="cabecera-resultados">
            <div>
              <span className="subtitulo-resultados">
                RESULTADOS / TOP SIMILITUD
              </span>

              <h2>Resultados encontrados</h2>
            </div>

            <div className="cantidad-resultados">
              {resultados.length} resultados
            </div>
          </div>

          <div className="lista-resultados">
            {resultados.map((resultado, index) => {
              const evaluacion =
                evaluaciones[resultado.id];

              const bloqueado =
                Boolean(evaluacion);

              const porcentaje =
                convertirPorcentaje(resultado.score);

              return (
                <article
                  className="resultado"
                  key={`${resultado.id}-${index}`}
                >
                  {/* POSICIÓN */}

                  <div className="numero-posicion">
                    #{index + 1}
                  </div>

                  {/* IMAGEN */}

                  <div className="contenedor-imagen-resultado">
                    <img
                      src={`/images/${resultado.id}.jpg`}
                      alt={resultado.nombre}
                      onError={(e) => {
                        const imagenActual =
                          e.currentTarget.src;

                        if (
                          imagenActual.endsWith(".jpg")
                        ) {
                          e.currentTarget.src =
                            `/images/${resultado.id}.png`;
                        } else {
                          e.currentTarget.style.display =
                            "none";
                        }
                      }}
                    />
                  </div>

                  {/* INFORMACIÓN */}

                  <div className="informacion-resultado">
                    <h3>
                      {resultado.nombre}
                    </h3>

                    <p className="id">
                      {resultado.id}
                    </p>

                    <div className="similitud">
                      <span>
                        SIMILITUD
                      </span>

                      <strong>
                        {porcentaje}%
                      </strong>
                    </div>
                  </div>

                  {/* BOTONES */}

                  <div className="botones-evaluacion">
                    <button
                      type="button"
                      disabled={bloqueado}
                      className={
                        evaluacion === "Acierto"
                          ? "boton-evaluacion boton-acierto activo"
                          : "boton-evaluacion boton-acierto"
                      }
                      onClick={() =>
                        evaluarResultado(
                          resultado,
                          index + 1,
                          "Acierto"
                        )
                      }
                    >
                      Acierto
                    </button>

                    <button
                      type="button"
                      disabled={bloqueado}
                      className={
                        evaluacion === "Sirve"
                          ? "boton-evaluacion boton-sirve activo"
                          : "boton-evaluacion boton-sirve"
                      }
                      onClick={() =>
                        evaluarResultado(
                          resultado,
                          index + 1,
                          "Sirve"
                        )
                      }
                    >
                      Sirve
                    </button>

                    <button
                      type="button"
                      disabled={bloqueado}
                      className={
                        evaluacion === "No sirve"
                          ? "boton-evaluacion boton-no-sirve activo"
                          : "boton-evaluacion boton-no-sirve"
                      }
                      onClick={() =>
                        evaluarResultado(
                          resultado,
                          index + 1,
                          "No sirve"
                        )
                      }
                    >
                      No sirve
                    </button>
                  </div>

                  {/* EVALUACIÓN GUARDADA */}

                  {evaluacion && (
                    <div className="evaluacion-guardada">
                      <span className="check">
                        ✓
                      </span>

                      <div>
                        <small>
                          EVALUACIÓN GUARDADA
                        </small>

                        <strong>
                          {evaluacion}
                        </strong>
                      </div>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;