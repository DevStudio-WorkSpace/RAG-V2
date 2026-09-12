// 1. Configuración del Puerto del Servidor de Samir
const API_URL = 'http://localhost:8001'; 

let casoActual = null;
let juiciosLocales = {}; // Guarda temporalmente los clics del caso activo

// Variables de control para navegar por el arreglo de 10 casos
let indiceCaso = 0; 
let todosLosCasos = [];

// Arrancar la aplicación al cargar la página
window.onload = async function () {
    await cargarCasoActual();
};

// Paso 1: Administrar y cargar los casos secuencialmente
async function cargarCasoActual() {
    try {
        // Si es la primera carga de la página, solicitamos los casos al servidor
        if (todosLosCasos.length === 0) {
            const responde = await fetch(`${API_URL}/api/casos`);
            const data = await responde.json();
            
            // Guardamos el arreglo de casos que viene dentro del objeto de Samir
            todosLosCasos = data.casos || [];
        }

        // Si ya evaluamos todos los casos disponibles, pasamos a la pantalla de métricas
        if (indiceCaso >= todosLosCasos.length) {
            // Solicitamos las métricas finales calculadas al backend
            const respondeMetricas = await fetch(`${API_URL}/api/casos`);
            const dataMetricas = await respondeMetricas.json();
            mostrarPantallaFinal(dataMetricas.metricas || dataMetricas);
            return;
        }

        // Seleccionamos el caso activo correspondiente al índice actual
        casoActual = todosLosCasos[indiceCaso];
        juiciosLocales = {}; // Reiniciar votaciones locales
        document.getElementById('btn-siguiente').disabled = true;

        // Actualizar indicadores del progreso en la pantalla HTML
        document.getElementById('progreso').innerText = `Caso ${indiceCaso + 1} de ${todosLosCasos.length}`;

        // Cargar la imagen del caso activo usando los campos del objeto de Samir
        document.getElementById('foto-consulta').src = `${API_URL}/casos/${casoActual.imagen_consulta || casoActual.imagen}`;
        
        // Extraer los 5 resultados correspondientes al caso activo
        const resultadosAEnviar = casoActual.resultados_buscador || [];
        renderizadoResultados(resultadosAEnviar);

    } catch (error) {
        console.error("Error de conexión", error);
        document.getElementById('progreso').innerText = "Error al conectar con el servidor";
    }
}

// Paso 2: Dibujar dinámicamente las 5 tarjetas de resultados con sus 3 botones
function renderizadoResultados(resultados) {
    const contenedor = document.getElementById('contenedor-resultados');
    contenedor.innerHTML = ''; // Limpiar elementos previos

    resultados.forEach((res, index) => {
        const posicion = index + 1; // Posición del 1 al 5
        const card = document.createElement('div');
        card.className = 'card-resultado';

        // Estructura interna adaptada a las propiedades id_resultado, imagen y score
        card.innerHTML = `
            <img class="img-resultado" src="${API_URL}/casos/${res.imagen_resultado}" alt="${res.id_resultado}">
            <h4>ID: ${res.id_resultado}</h4>
            <div class="score">Score: ${res.score.toFixed(4)}</div>
            <div class="botones-juicio">
                <button class="btn-acierto" onclick="registrarJuicio(${posicion}, '${res.id_resultado}', ${res.score}, 'Acierto', this)">Acierto</button>
                <button class="btn-sirve" onclick="registrarJuicio(${posicion}, '${res.id_resultado}', ${res.score}, 'Sirve', this)">Sirve</button>
                <button class="btn-nosirve" onclick="registrarJuicio(${posicion}, '${res.id_resultado}', ${res.score}, 'No sirve', this)">No sirve</button>
            </div>
        `;
        contenedor.appendChild(card);
    });
}

// Paso 3: Guardar el clic inmediatamente en el servidor (Persistencia exigida)
async function registrarJuicio(posicion, idResultado, score, juicio, boton) {
    // Resaltar visualmente el botón seleccionado por el usuario
    const hermanos = boton.parentElement.querySelectorAll('button');
    hermanos.forEach(b => b.classList.remove('seleccionado'));
    boton.classList.add('seleccionado');

    // Registrar la votación en el control temporal local
    juiciosLocales[posicion] = juicio;

    try {
        // Enviar el clic al backend para que se agregue directamente a resultados.csv
        await fetch(`${API_URL}/api/guardar-juicio`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                caso: casoActual.id || casoActual.caso,
                id_correcto: casoActual.id_correcto,
                posicion: posicion,
                id_resultado: idResultado,
                score: score,
                juicio: juicio,
                who: "Andres y Samir"
            })
        });

        // Habilitar el botón "Siguiente" únicamente si ya se votó en las 5 tarjetas
        if (Object.keys(juiciosLocales).length === 5) {
            document.getElementById('btn-siguiente').disabled = false;
        } 
    } catch (error) {
        console.error("Error al guardar el juicio:", error);
        alert("No se pudo conectar con el servidor para guardar tu voto.");
    }
}

// Paso 4: Escuchar el clic del botón Siguiente para avanzar de caso en el Frontend
document.getElementById('btn-siguiente').addEventListener('click', async () => {
    try {
        // Notificamos el cambio de caso al backend por si ejecuta algún guardado interno
        await fetch(`${API_URL}/api/siguiente-caso`, { method: 'POST' });
    } catch (error) {
        console.error("Error al avanzar de caso en el servidor:", error);
    } finally {
        // Avanzamos nuestro puntero local independientemente de la respuesta e implementamos la carga
        indiceCaso++;
        await cargarCasoActual();
    }
});

// Paso 5: Mostrar la pantalla final con los cálculos automáticos requeridos
function mostrarPantallaFinal(metricas) {
    document.getElementById('pantalla-evaluacion').classList.add('oculto');

    const pFinal = document.getElementById('pantalla-final');
    pFinal.classList.remove('oculto');
    document.getElementById('progreso').innerText = "Evaluación Completada";

    document.getElementById('metricas-generales').innerHTML = `
        <h3>Métricas de Desempeño Obtenidas</h3>
        <p><strong>Métrica Top 1:</strong> ${(metricas.top1 * 100 || 0).toFixed(1)}%</p>
        <p><strong>Métrica Top 5 (Clave):</strong> ${(metricas.top5 * 100 || 0).toFixed(1)}%</p>
        <p><strong>Grado de Utilidad Promedio:</strong> ${(metricas.utilidad || 0).toFixed(2)} / 5.00</p>
    `;
}
