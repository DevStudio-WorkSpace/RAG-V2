import streamlit as st
import pandas as pd
import requests
import os
import streamlit.components.v1 as components
import numpy as np

st.set_page_config(page_title="Evaluador RAG", layout="centered")

# Config
API_URL = "http://localhost:8000/search/image"
CASOS_FILE = os.path.join(os.path.dirname(__file__), "casos_prueba_2.csv")
RESULTADOS_FILE = os.path.join(os.path.dirname(__file__), "sala6evaluasala5.csv")

# Load cases
@st.cache_data
def load_cases():
    if not os.path.exists(CASOS_FILE):
        return pd.DataFrame()
    return pd.read_csv(CASOS_FILE)

cases_df = load_cases()

if cases_df.empty:
    st.error(f"No se encontró {CASOS_FILE} o está vacío.")
    st.stop()

# Initialize state
if "current_case_idx" not in st.session_state:
    st.session_state.current_case_idx = 0
if "current_result_idx" not in st.session_state:
    st.session_state.current_result_idx = 0
if "api_results" not in st.session_state:
    st.session_state.api_results = None

# Shortcut injection
components.html("""
<script>
const doc = window.parent.document;
document.addEventListener('keydown', function(e) {
    if(['1', '2', '3'].includes(e.key)) {
        let btnText = "";
        if(e.key === '1') btnText = "Acierto (3)";
        else if(e.key === '2') btnText = "Sirve (1)";
        else if(e.key === '3') btnText = "No sirve (0)";
        
        const btns = Array.from(doc.querySelectorAll('button')).filter(b => b.innerText.includes(btnText));
        if(btns.length > 0) {
            btns[0].click();
        }
    }
});
</script>
""", height=0, width=0)

def fetch_api(img_path, modo):
    # Call the actual API
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), img_path)
    if not os.path.exists(abs_path):
        return None
    
    with open(abs_path, "rb") as f:
        files = {"file": f}
        data = {"modo": modo} 
        try:
            r = requests.post(API_URL, files=files, data=data)
            if r.status_code == 200:
                return r.json()
        except:
            return None
    return None

def save_vote(case_img, true_id, res_id, pos, label, score):
    # Save to CSV
    file_exists = os.path.exists(RESULTADOS_FILE)
    df = pd.DataFrame([{
        "caso_imagen": case_img,
        "id_correcto": true_id,
        "resultado_id": res_id,
        "posicion": pos,
        "juicio": label,
        "puntos": score
    }])
    df.to_csv(RESULTADOS_FILE, mode='a', header=not file_exists, index=False)
    
    # Advance state
    st.session_state.current_result_idx += 1
    if st.session_state.current_result_idx >= 5:
        st.session_state.current_result_idx = 0
        st.session_state.current_case_idx += 1
        st.session_state.api_results = None

def render_metrics():
    st.success("¡Evaluación de 10 casos finalizada!")
    df = pd.read_csv(RESULTADOS_FILE)
    
    # Calc Metrics
    # Precision@1: % of cases where Pos 1 is Acierto (3 pts)
    p1_df = df[df['posicion'] == 1]
    p1_score = (p1_df['puntos'] == 3).mean() * 100 if len(p1_df) > 0 else 0
    
    # Precision@5: % of results (pos 1-5) that are useful (Acierto=3 or Sirve=1)
    p5_score = (df['puntos'] > 0).mean() * 100 if len(df) > 0 else 0
    
    # NDCG@5: simplified per case and averaged
    def calc_ndcg(group):
        dcg = 0
        idcg = 0
        # sort group by position just in case
        group = group.sort_values('posicion')
        ideal = sorted(group['puntos'].tolist(), reverse=True)
        for i, (p, ip) in enumerate(zip(group['puntos'].tolist(), ideal)):
            dcg += p / np.log2(i + 2)
            idcg += ip / np.log2(i + 2)
        return dcg / idcg if idcg > 0 else 0
    
    ndcg_score = df.groupby('caso_imagen').apply(calc_ndcg).mean() * 100
    
    st.header("Métricas Finales")
    c1, c2, c3 = st.columns(3)
    c1.metric("Precision@1 (Exacto)", f"{p1_score:.1f}%")
    c2.metric("Precision@5 (Utilidad)", f"{p5_score:.1f}%")
    c3.metric("NDCG@5 (Ranking)", f"{ndcg_score:.1f}%")
    
    if st.button("Reiniciar"):
        st.session_state.current_case_idx = 0
        st.session_state.current_result_idx = 0
        st.session_state.api_results = None
        st.rerun()

# Main Flow
if "modo" not in st.session_state:
    st.session_state.modo = "original"

st.sidebar.title("Configuración")
modos_disponibles = ["original", "auto", "clasico", "legacy", "procesada"]
modo_seleccionado = st.sidebar.selectbox("Modo de búsqueda", modos_disponibles, index=modos_disponibles.index(st.session_state.modo))

if modo_seleccionado != st.session_state.modo:
    st.session_state.modo = modo_seleccionado
    st.session_state.api_results = None
    st.rerun()

if st.session_state.current_case_idx >= len(cases_df):
    render_metrics()
    st.stop()

case = cases_df.iloc[st.session_state.current_case_idx]
img_path = case['ruta_imagen']
true_id = case['id_correcto']

if st.session_state.api_results is None:
    with st.spinner(f"Consultando API en modo {st.session_state.modo}..."):
        res = fetch_api(img_path, st.session_state.modo)
        if not res or "resultados" not in res:
            st.error("No se pudieron obtener resultados de la API.")
            st.stop()
        st.session_state.api_results = res

results = st.session_state.api_results.get("resultados", [])
img_b64 = st.session_state.api_results.get("imagen_procesada_b64")
curr_res_idx = st.session_state.current_result_idx

if curr_res_idx < len(results):
    current_res = results[curr_res_idx]
    
    st.progress((st.session_state.current_case_idx) / len(cases_df), text=f"Caso {st.session_state.current_case_idx + 1} de {len(cases_df)}")
    st.subheader(f"Comparación (Top {curr_res_idx + 1} de 5)")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**1. Foto de consulta**")
        abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), img_path)
        st.image(abs_path, use_container_width=True)
        if img_b64:
            import base64
            from io import BytesIO
            from PIL import Image
            try:
                img_data = base64.b64decode(img_b64)
                st.markdown("**Recorte de la consulta**")
                st.image(Image.open(BytesIO(img_data)), use_container_width=True)
            except:
                pass
    
    with c2:
        st.markdown(f"**2. Resultado sugerido (ID: {current_res['id']})**")
        # Find original image for result
        res_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "images_normalized", current_res['imagen'])
        if os.path.exists(res_img_path):
            st.image(res_img_path, use_container_width=True)
        else:
            base_name = os.path.splitext(current_res['imagen'])[0]
            jpg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "images_normalized", f"{base_name}.jpg")
            png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "images_normalized", f"{base_name}.png")
            if os.path.exists(jpg_path):
                st.image(jpg_path, use_container_width=True)
            elif os.path.exists(png_path):
                st.image(png_path, use_container_width=True)
            else:
                st.warning(f"Imagen del resultado no encontrada: {current_res['imagen']}")
            
        st.write("---")
        st.markdown("### ¿Qué puntaje le das?")
        
        # Botones de votación
        b1, b2, b3 = st.columns(3)
        if b1.button("1 - Acierto (3)", use_container_width=True):
            save_vote(img_path, true_id, current_res['id'], curr_res_idx + 1, "Acierto", 3)
            st.rerun()
        b1.caption("Es el mismo diseño, aunque cambie el color, el año, el escudo o el sponsor.")
            
        if b2.button("2 - Sirve (1)", use_container_width=True):
            save_vote(img_path, true_id, current_res['id'], curr_res_idx + 1, "Sirve", 1)
            st.rerun()
        b2.caption("No es el mismo, pero se lo mostrarías al cliente y lo aceptaría.")
            
        if b3.button("3 - No sirve (0)", use_container_width=True):
            save_vote(img_path, true_id, current_res['id'], curr_res_idx + 1, "No sirve", 0)
            st.rerun()
        b3.caption("Es otro diseño.")
