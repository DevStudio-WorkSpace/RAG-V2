# -*- coding: utf-8 -*-
"""
evaluador.py
------------
Frontend del evaluador de búsqueda visual de Sublitex.

Este archivo es independiente del buscador original (app.py).
No modifica la API, el catálogo ni los embeddings.

Ejecutar desde la raíz del proyecto:
    streamlit run frontend/evaluador.py
"""

import streamlit as st


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Evaluador de búsqueda visual | Sublitex",
    page_icon="👕",
    layout="wide",
)


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    """
    <style>

    /* Fondo general */
    .stApp {
        background-color: #f5f6f8;
    }

    /* Ocultar menú y footer de Streamlit */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Contenedor principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Encabezado */
    .header {
        background: white;
        padding: 22px 28px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        margin-bottom: 22px;
    }

    .brand {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 1px;
        margin: 0;
    }

    .subtitle {
        color: #6b7280;
        margin-top: 4px;
        font-size: 15px;
    }

    /* Tarjetas */
    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .card-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .card-subtitle {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 16px;
    }

    /* Caso */
    .case-number {
        font-size: 24px;
        font-weight: 750;
    }

    .case-description {
        color: #6b7280;
        font-size: 14px;
    }

    /* Resultado */
    .result-number {
        font-size: 15px;
        font-weight: 700;
        color: #374151;
        margin-bottom: 6px;
    }

    .result-code {
        font-family: monospace;
        color: #6b7280;
        font-size: 13px;
        margin-bottom: 10px;
    }

    /* Estado */
    .saved {
        display: inline-block;
        background: #ecfdf5;
        color: #047857;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }

    /* Separador */
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 20px 0;
    }

    /* Botones */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        min-height: 40px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATOS TEMPORALES
# ============================================================

# Estos datos son solamente para visualizar el frontend.
# Después los reemplazaremos por los datos de casos_prueba.csv.

casos = [
    {
        "id": "C_01_Barcelona.jpg",
        "tipo": "Camiseta",
    },
    {
        "id": "C_02_Real-Madrid.jpg",
        "tipo": "Camiseta",
    },
    {
        "id": "C_03_Universitario.jpg",
        "tipo": "Camiseta",
    },
    {
        "id": "C_04_Alianza-Lima.jpg",
        "tipo": "Camiseta",
    },
    {
        "id": "C_05.jpg",
        "tipo": "Camiseta",
    },
    {
        "id": "C_06.jpg",
        "tipo": "Camiseta",
    },
    {
        "id": "C_07.jpg",
        "tipo": "Camiseta",
    },
    {
        "id": "C_08.jpg",
        "tipo": "Camiseta",
    },
    {
        "id": "C_09_Manchester-City.jpg",
        "tipo": "Camiseta",
    },
    {
        "id": "C_10_AC-Milan.jpg",
        "tipo": "Camiseta",
    },
]


# ============================================================
# ESTADO DE LA APLICACIÓN
# ============================================================

if "caso_actual" not in st.session_state:
    st.session_state.caso_actual = 0

if "juicios" not in st.session_state:
    st.session_state.juicios = {}


# ============================================================
# FUNCIONES
# ============================================================

def guardar_juicio(caso, posicion, juicio):
    """Guarda temporalmente el juicio seleccionado."""

    clave = f"{caso}_{posicion}"

    st.session_state.juicios[clave] = juicio


def obtener_juicio(caso, posicion):
    """Devuelve el juicio seleccionado para un resultado."""

    clave = f"{caso}_{posicion}"

    return st.session_state.juicios.get(clave)


def caso_completo(caso):
    """Comprueba si los 5 resultados tienen un juicio."""

    for posicion in range(1, 6):
        if obtener_juicio(caso, posicion) is None:
            return False

    return True


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    """
    <div class="header">
        <div class="brand">SUBLITEX</div>
        <div class="subtitle">
            Evaluador de búsqueda visual
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INFORMACIÓN DEL CASO
# ============================================================

indice = st.session_state.caso_actual
caso = casos[indice]

numero_caso = indice + 1
total_casos = len(casos)

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(
        f"""
        <div class="case-number">
            Caso {numero_caso:02d} / {total_casos}
        </div>
        <div class="case-description">
            Evalúa los 5 resultados utilizando los criterios establecidos.
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div style="text-align:right;">
            <span class="saved">● Evaluación guardada</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Barra de progreso

casos_completados = 0

for c in casos:
    if caso_completo(c["id"]):
        casos_completados += 1

st.progress(casos_completados / total_casos)

st.caption(
    f"{casos_completados} de {total_casos} casos evaluados"
)


st.divider()


# ============================================================
# COLUMNAS PRINCIPALES
# ============================================================

col_consulta, col_resultados = st.columns([1, 2])


# ============================================================
# FOTO DE CONSULTA
# ============================================================

with col_consulta:

    st.markdown(
        """
        <div class="card-title">
            Foto de consulta
        </div>
        <div class="card-subtitle">
            Imagen utilizada para realizar la búsqueda
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Imagen temporal
    # --------------------------------------------------------
    #
    # Cuando conectemos los casos reales, aquí aparecerá:
    #
    # casos/C_01_Barcelona.jpg
    #
    # --------------------------------------------------------

    st.info(
        f"Imagen de consulta:\n\n{caso['id']}"
    )

    st.markdown(
        f"""
        <div class="card">
            <strong>Archivo</strong><br>
            <span style="color:#6b7280;">
                {caso["id"]}
            </span>
            <br><br>
            <strong>Tipo</strong><br>
            <span style="color:#6b7280;">
                {caso["tipo"]}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RESULTADOS
# ============================================================

with col_resultados:

    st.markdown(
        """
        <div class="card-title">
            Resultados de búsqueda
        </div>
        <div class="card-subtitle">
            Clasifica cada resultado según su utilidad.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Resultados temporales
    resultados_demo = [
        {
            "posicion": 1,
            "codigo": "AIM-DEMO-001",
            "nombre": "Producto resultado 1",
        },
        {
            "posicion": 2,
            "codigo": "AIM-DEMO-002",
            "nombre": "Producto resultado 2",
        },
        {
            "posicion": 3,
            "codigo": "AIM-DEMO-003",
            "nombre": "Producto resultado 3",
        },
        {
            "posicion": 4,
            "codigo": "AIM-DEMO-004",
            "nombre": "Producto resultado 4",
        },
        {
            "posicion": 5,
            "codigo": "AIM-DEMO-005",
            "nombre": "Producto resultado 5",
        },
    ]

    for resultado in resultados_demo:

        posicion = resultado["posicion"]
        juicio_actual = obtener_juicio(
            caso["id"],
            posicion
        )

        st.markdown(
            f"""
            <div class="card">
                <div class="result-number">
                    Resultado #{posicion}
                </div>

                <div class="result-code">
                    {resultado["codigo"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Imagen temporal
        st.info(
            f"Imagen del resultado #{posicion}"
        )

        col_a, col_s, col_n = st.columns(3)

        with col_a:
            if st.button(
                "✓ Acierto",
                key=f"acierto_{indice}_{posicion}",
            ):
                guardar_juicio(
                    caso["id"],
                    posicion,
                    "Acierto"
                )
                st.rerun()

        with col_s:
            if st.button(
                "Sirve",
                key=f"sirve_{indice}_{posicion}",
            ):
                guardar_juicio(
                    caso["id"],
                    posicion,
                    "Sirve"
                )
                st.rerun()

        with col_n:
            if st.button(
                "No sirve",
                key=f"no_{indice}_{posicion}",
            ):
                guardar_juicio(
                    caso["id"],
                    posicion,
                    "No sirve"
                )
                st.rerun()

        if juicio_actual:
            st.caption(
                f"Juicio seleccionado: **{juicio_actual}**"
            )

        st.divider()


# ============================================================
# NAVEGACIÓN
# ============================================================

st.write("")

col_prev, col_space, col_next = st.columns([1, 2, 1])

with col_prev:

    if st.button(
        "← Anterior",
        disabled=(indice == 0),
        key="anterior",
    ):
        st.session_state.caso_actual -= 1
        st.rerun()


with col_next:

    if st.button(
        "Siguiente →",
        disabled=(indice == total_casos - 1),
        key="siguiente",
    ):
        st.session_state.caso_actual += 1
        st.rerun()


# ============================================================
# RESUMEN TEMPORAL
# ============================================================

st.divider()

st.subheader("Estado de evaluación")

col1, col2, col3 = st.columns(3)

aciertos = sum(
    1
    for juicio in st.session_state.juicios.values()
    if juicio == "Acierto"
)

sirve = sum(
    1
    for juicio in st.session_state.juicios.values()
    if juicio == "Sirve"
)

no_sirve = sum(
    1
    for juicio in st.session_state.juicios.values()
    if juicio == "No sirve"
)

with col1:
    st.metric(
        "Aciertos",
        aciertos
    )

with col2:
    st.metric(
        "Sirve",
        sirve
    )

with col3:
    st.metric(
        "No sirve",
        no_sirve
    )