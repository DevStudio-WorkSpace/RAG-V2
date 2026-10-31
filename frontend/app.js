const inputImagen = document.getElementById("input-imagen");
const queryImage = document.getElementById("query-image");
const resultadosBox = document.getElementById("resultados");


// ======================================
// 1. MOSTRAR IMAGEN DE CONSULTA
// ======================================

inputImagen.addEventListener("change", function () {

    const archivo = inputImagen.files[0];

    if (!archivo) {
        return;
    }

    // Mostrar la imagen seleccionada
    queryImage.src = URL.createObjectURL(archivo);

    // Mostrar nombre del archivo
    document.getElementById("query-name").textContent = archivo.name;
    document.getElementById("query-file").textContent = archivo.name;

    // Buscar automáticamente
    buscarImagen(archivo);
});


// ======================================
// 2. ENVIAR IMAGEN AL BUSCADOR
// ======================================

async function buscarImagen(archivo) {

    resultadosBox.innerHTML = `
        <p style="padding:20px;">
            Buscando resultados...
        </p>
    `;

    try {

        // Creamos el formulario que recibirá la API
        const formulario = new FormData();

        formulario.append("file", archivo);
        formulario.append("modo", "auto");
        formulario.append("modelo", "clip");


        // Enviamos la imagen a la API existente
        const respuesta = await fetch(
            "http://localhost:8000/search/image",
            {
                method: "POST",
                body: formulario
            }
        );


        // Verificar respuesta
        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.error || `Error de la API: ${respuesta.status}`);
        }

        console.log("Respuesta de la API:", datos);


        // Obtener los resultados
        const resultados = datos.resultados || [];


        if (resultados.length === 0) {

            resultadosBox.innerHTML = `
                <p style="padding:20px;">
                    No se encontraron resultados.
                </p>
            `;

            return;
        }


        // Mostrar los resultados
        mostrarResultados(resultados);

    } catch (error) {

        console.error("ERROR REAL:", error);

        resultadosBox.innerHTML = `
            <div style="
                padding:20px;
                color:red;
                background:#fee2e2;
                border-radius:10px;
            ">
                <strong>ERROR:</strong>
                <br><br>
                ${error}
            </div>
        `;
    }   
}


// ======================================
// 3. MOSTRAR LOS 5 RESULTADOS
// ======================================

function mostrarResultados(resultados) {

    resultadosBox.innerHTML = "";


    resultados.slice(0, 5).forEach((resultado, index) => {

        const posicion = index + 1;


        // Imagen del resultado
        let imagen = resultado.url;

        if (resultado.imagen) {
            imagen = resultado.imagen;
        }


        // Crear tarjeta
        const tarjeta = document.createElement("div");

        tarjeta.className = "result-card";


        tarjeta.innerHTML = `

            <div class="result-image">

                <img
                    src="${imagen}"
                    alt="Resultado ${posicion}"
                    style="
                        width:100%;
                        height:100%;
                        object-fit:contain;
                        border-radius:8px;
                    "
                    onerror="this.style.display='none'"
                >

            </div>


            <div class="result-content">

                <div class="result-title">

                    <div class="position">
                        #${posicion}
                    </div>

                    <div>

                        <span class="result-label">
                            RESULTADO
                        </span>

                        <strong>
                            ${resultado.nombre || resultado.id || "Sin nombre"}
                        </strong>

                    </div>

                </div>


                <div class="judgment-buttons">

                    <button
                        class="judgment success"
                        onclick="evaluarResultado(${posicion}, 'Acierto', this)"
                    >
                        ✓ Acierto
                    </button>


                    <button
                        class="judgment useful"
                        onclick="evaluarResultado(${posicion}, 'Sirve', this)"
                    >
                        ~ Sirve
                    </button>


                    <button
                        class="judgment wrong"
                        onclick="evaluarResultado(${posicion}, 'No sirve', this)"
                    >
                        ✕ No sirve
                    </button>

                </div>

            </div>

        `;


        resultadosBox.appendChild(tarjeta);

    });

}


// ======================================
// 4. EVALUAR UN RESULTADO
// ======================================

function evaluarResultado(posicion, juicio, boton) {

    console.log(
        "Resultado:",
        posicion,
        "Juicio:",
        juicio
    );


    // Buscar los botones de la misma tarjeta
    const botones =
        boton.parentElement.querySelectorAll(".judgment");


    // Quitar selección anterior
    botones.forEach(b => {

        b.style.background = "";
        b.style.borderColor = "";

    });


    // Marcar botón seleccionado
    boton.style.background = "#e5e7eb";
    boton.style.borderColor = "#111827";


    // Guardar temporalmente el juicio
    boton.parentElement.dataset.juicio = juicio;


    console.log(
        `Resultado #${posicion}: ${juicio}`
    );
}