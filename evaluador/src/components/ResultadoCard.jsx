function ResultadoCard({ resultado, posicion, juicioSeleccionado, onEvaluar }) {
  const obtenerClaseBoton = (juicio) => {
    return juicioSeleccionado === juicio
      ? `boton-juicio activo ${juicio.toLowerCase().replace(" ", "-")}`
      : `boton-juicio ${juicio.toLowerCase().replace(" ", "-")}`;
  };

  return (
    <article className="resultado-card">
      <div className="resultado-posicion">
        Resultado {posicion}
      </div>

      <div className="resultado-imagen-contenedor">
        <img
          src={resultado.imagen}
          alt={resultado.nombre}
          className="resultado-imagen"
        />
      </div>

      <div className="resultado-info">
        <h3>{resultado.nombre}</h3>

        <p className="resultado-id">
          ID: {resultado.id}
        </p>

        <p className="resultado-score">
          Score: {resultado.score}
        </p>
      </div>

      <div className="resultado-botones">
        <button
          type="button"
          className={obtenerClaseBoton("Acierto")}
          onClick={() => onEvaluar("Acierto")}
        >
          Acierto
        </button>

        <button
          type="button"
          className={obtenerClaseBoton("Sirve")}
          onClick={() => onEvaluar("Sirve")}
        >
          Sirve
        </button>

        <button
          type="button"
          className={obtenerClaseBoton("No sirve")}
          onClick={() => onEvaluar("No sirve")}
        >
          No sirve
        </button>
      </div>
    </article>
  );
}

export default ResultadoCard;