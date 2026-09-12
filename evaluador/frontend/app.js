let API_URL = 'http://localhost:8001';

let casoActual = null;
let juiciosLocales = {};
let indiceCaso = 0;
let todosLosCasos = [];
let totalResultadosActual = 0;

window.onload = async function () {
    await cargarCasoActual();
};

async function cargarCasoActual() {
    try {
        if (todosLosCasos.length === 0) {
            const res = await fetch(`${API_URL}/api/casos`);
            const data = await res.json();
            todosLosCasos = data.casos || [];

            // Retomar progreso: buscar cuales casos ya tienen 5 juicios
            const resPrev = await fetch(`${API_URL}/api/resultados`);
            const dataPrev = await resPrev.json();
            if (dataPrev.resultados && dataPrev.resultados.length > 0) {
                const conteo = {};
                for (const r of dataPrev.resultados) {
                    const c = r.caso;
                    conteo[c] = (conteo[c] || 0) + 1;
                }
                // En el primer caso que no tenga 5 juicios, ahi retomamos
                for (let i = 0; i < todosLosCasos.length; i++) {
                    const nombre = todosLosCasos[i].caso;
                    if (!conteo[nombre] || conteo[nombre] < 5) {
                        indiceCaso = i;
                        break;
                    }
                    // Si todos tienen 5, quedamos en el ultimo (se mostrara pantalla final)
                    if (i === todosLosCasos.length - 1) {
                        indiceCaso = todosLosCasos.length;
                    }
                }
            }
        }

        if (indiceCaso >= todosLosCasos.length) {
            const resMet = await fetch(`${API_URL}/api/estadisticas`);
            const dataMet = await resMet.json();
            mostrarPantallaFinal(dataMet);
            return;
        }

        casoActual = todosLosCasos[indiceCaso];
        juiciosLocales = {};
        totalResultadosActual = 0;
        document.getElementById('btn-siguiente').disabled = true;
        document.getElementById('progreso').innerText = `Caso ${indiceCaso + 1} de ${todosLosCasos.length}`;
        document.getElementById('foto-consulta').src = `${API_URL}/api/caso-imagen/${casoActual.imagen}`;

        const resCaso = await fetch(`${API_URL}/api/casos/${indiceCaso + 1}`);
        const dataCaso = await resCaso.json();

        if (!dataCaso.api_ok) {
            document.getElementById('contenedor-resultados').innerHTML =
                `<p style="color:red; grid-column:1/-1;">Error: ${dataCaso.error_api || 'La API no respondio'}</p>`;
            return;
        }

        const resultados = dataCaso.resultados || [];
        totalResultadosActual = resultados.length;
        renderizadoResultados(resultados);

    } catch (error) {
        console.error("Error de conexion", error);
        document.getElementById('progreso').innerText = "Error al conectar con el servidor";
    }
}

function renderizadoResultados(resultados) {
    const contenedor = document.getElementById('contenedor-resultados');
    contenedor.innerHTML = '';

    resultados.forEach((res, index) => {
        const posicion = index + 1;
        const card = document.createElement('div');
        card.className = 'card-resultado';

        card.innerHTML = `
            <img class="img-resultado" src="${API_URL}/api/imagen/${res.imagen}" alt="${res.id}">
            <h4>ID: ${res.id}</h4>
            <div class="score">Score: ${res.score.toFixed(4)}</div>
            <div class="botones-juicio">
                <button class="btn-acierto" onclick="registrarJuicio(${posicion}, '${res.id}', ${res.score}, 'Acierto', this)">Acierto</button>
                <button class="btn-sirve" onclick="registrarJuicio(${posicion}, '${res.id}', ${res.score}, 'Sirve', this)">Sirve</button>
                <button class="btn-nosirve" onclick="registrarJuicio(${posicion}, '${res.id}', ${res.score}, 'No sirve', this)">No sirve</button>
            </div>
        `;
        contenedor.appendChild(card);
    });
}

async function registrarJuicio(posicion, idResultado, score, juicio, boton) {
    const hermanos = boton.parentElement.querySelectorAll('button');
    hermanos.forEach(b => b.classList.remove('seleccionado'));
    boton.classList.add('seleccionado');
    juiciosLocales[posicion] = juicio;

    try {
        const formData = new URLSearchParams();
        formData.append('caso', casoActual.caso);
        formData.append('id_correcto', casoActual.id_correcto);
        formData.append('posicion', posicion);
        formData.append('id_resultado', idResultado);
        formData.append('score', score);
        formData.append('juicio', juicio);
        formData.append('quien', 'Andres y Samir');

        await fetch(`${API_URL}/api/juicios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString()
        });

        if (Object.keys(juiciosLocales).length === totalResultadosActual && totalResultadosActual > 0) {
            document.getElementById('btn-siguiente').disabled = false;
        }
    } catch (error) {
        console.error("Error al guardar el juicio:", error);
        alert("No se pudo conectar con el servidor para guardar tu voto.");
    }
}

document.getElementById('btn-siguiente').addEventListener('click', async () => {
    indiceCaso++;
    await cargarCasoActual();
});

function mostrarPantallaFinal(metricas) {
    document.getElementById('pantalla-evaluacion').classList.add('oculto');
    const pFinal = document.getElementById('pantalla-final');
    pFinal.classList.remove('oculto');
    document.getElementById('progreso').innerText = "Evaluacion Completada";

    document.getElementById('metricas-generales').innerHTML = `
        <h3>Metricas de Desempeno Obtenidas</h3>
        <p><strong>Top 1:</strong> ${(metricas.top1 || 0).toFixed(1)}%</p>
        <p><strong>Top 5:</strong> ${(metricas.top5 || 0).toFixed(1)}%</p>
        <p><strong>Utilidad:</strong> ${(metricas.utilidad || 0).toFixed(2)} / 5.00</p>
    `;

    if (metricas.por_tipo && Object.keys(metricas.por_tipo).length > 0) {
        let html = '<h3>Desglose por tipo de foto</h3><table border="1" cellpadding="6" style="border-collapse:collapse; margin-top:10px;">';
        html += '<tr><th>Tipo</th><th>Casos</th><th>Top 1</th><th>Top 5</th><th>Utilidad</th></tr>';
        for (const [tipo, datos] of Object.entries(metricas.por_tipo)) {
            html += `<tr><td>${tipo}</td><td>${datos.total}</td><td>${datos.top1}%</td><td>${datos.top5}%</td><td>${datos.utilidad}/5</td></tr>`;
        }
        html += '</table>';
        document.getElementById('metricas-desglose').innerHTML = html;
    }
}
