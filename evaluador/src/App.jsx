import { useState } from "react";
import "./App.css";

function App() {
  const [archivo, setArchivo] = useState(null);
  const [preview, setPreview] = useState(null);
  const [resultados, setResultados] = useState([]);
  const [evaluaciones, setEvaluaciones] = useState({});
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const cargarEvaluacionesGuardadas = async (nombreArchivo) => {
    try {
      const respuesta = await fetch(
        `http://127.0.0.1:8001/evaluaciones/${encodeURIComponent(nombreArchivo)}`
      );

      if (!respuesta.ok) {
        throw new Error("No se pudieron cargar las evaluaciones guardadas.");
      }

      const data = await respuesta.json();

      const evaluacionesRecuperadas = {};

      data.evaluaciones.forEach((item) => {
        evaluacionesRecuperadas[item.resultado_id] = item.evaluacion;
      });

      setEvaluaciones(evaluacionesRecuperadas);
    } catch (error) {
      console.error(error);
      setError("No se pudieron recuperar las evaluaciones anteriores.");
    }
  };

  const seleccionarImagen = async (e) => {
    const imagen = e.target.files[0];

    if (!imagen) return;

    setArchivo(imagen);
    setPreview(URL.createObjectURL(imagen));
    setResultados([]);
    setEvaluaciones({});
    setError("");

    await cargarEvaluacionesGuardadas(imagen.name);
  };

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
        throw new Error("Error al buscar imágenes similares.");
      }

      const data = await respuesta.json();

      console.log("Respuesta API:", data);

      setResultados(data.resultados || []);

      await cargarEvaluacionesGuardadas(archivo.name);
    } catch (error) {
      console.error(error);
      setError("No se pudo realizar la búsqueda.");
    } finally {
      setCargando(false);
    }
  };

  const evaluarResultado = async (
    resultado,
    posicion,
    evaluacion
  ) => {
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
        throw new Error("No se pudo guardar la evaluación.");
      }

      const data = await respuesta.json();

      console.log("Evaluación guardada:", data);

      setEvaluaciones((anteriores) => ({
        ...anteriores,
        [resultado.id]: evaluacion,
      }));
    } catch (error) {
      console.error(error);
      setError("La evaluación no pudo guardarse.");
    }
  };

  return (
    <main className="contenedor">
      <h1>Evaluador del buscador</h1>

      <p className="descripcion">
        Selecciona uno de los casos de prueba y evalúa los resultados.
      </p>

      <section className="buscador">
        <input
          type="file"
          accept=".jpg,.jpeg,.png"
          onChange={seleccionarImagen}
        />

        {archivo && (
          <p className="archivo-seleccionado">
            Archivo: <strong>{archivo.name}</strong>
          </p>
        )}

        {preview && (
          <img
            src={preview}
            alt="Imagen seleccionada"
            className="preview"
          />
        )}

        <button
          type="button"
          onClick={buscarSimilares}
          disabled={!archivo || cargando}
          className="boton-buscar"
        >
          {cargando ? "Buscando..." : "Buscar similares"}
        </button>

        {error && (
          <p className="error">
            {error}
          </p>
        )}
      </section>

      {resultados.length > 0 && (
        <section className="resultados">
          <h2>Resultados encontrados</h2>

          <div className="lista-resultados">
            {resultados.map((resultado, index) => {
              const evaluacion = evaluaciones[resultado.id];

              const bloqueado = Boolean(evaluacion);

              return (
                <div
                  className="resultado"
                  key={`${resultado.id}-${index}`}
                >
                  <p className="posicion">
                    Resultado {index + 1}
                  </p>

                  <img
                    src={`/images/${resultado.id}.jpg`}
                    alt={resultado.nombre}
                    onError={(e) => {
                      const imagenActual = e.currentTarget.src;

                      if (imagenActual.endsWith(".jpg")) {
                        e.currentTarget.src =
                          `/images/${resultado.id}.png`;
                      } else {
                        e.currentTarget.style.display = "none";
                      }
                    }}
                  />

                  <h3>{resultado.nombre}</h3>

                  <p className="id">
                    ID: {resultado.id}
                  </p>

                  <p className="score">
                    Score: {resultado.score}
                  </p>

                  <div className="botones-evaluacion">
                    <button
                      type="button"
                      disabled={bloqueado}
                      className={
                        evaluacion === "Acierto"
                          ? "boton-evaluacion activo"
                          : "boton-evaluacion"
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
                          ? "boton-evaluacion activo"
                          : "boton-evaluacion"
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
                          ? "boton-evaluacion activo"
                          : "boton-evaluacion"
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

                  {evaluacion && (
                    <p className="seleccion">
                      Evaluación guardada: {evaluacion}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;