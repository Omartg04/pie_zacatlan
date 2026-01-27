import streamlit as st

# Configuración de página principal
st.set_page_config(
    page_title="Sistema Electoral - Zacatlán",
    page_icon="🗳️",
    layout="centered"
)

# CSS para estética
st.markdown("""
<style>
    .main > div { padding-top: 2rem; }
    div.stButton > button:first-child {
        border: 1px solid #d0d0d0;
        transition: transform 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        border-color: #007bff;
    }
</style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🗳️ Sistema de Inteligencia Electoral")
    st.markdown("### Municipio de Zacatlán | Enero 2026")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.metric("Fase", "Planeación", delta="Dev")

st.markdown("---")
st.info("🛠️ **MODO DESARROLLO** • Acceso libre habilitado para configuración.")
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# MÓDULO ACTIVO: PLANEACIÓN
# ==============================================================================
st.markdown("### 📍 Módulo Activo")

with st.container(border=True):
    st.markdown("""
        <div style='background: linear-gradient(135deg, #2C3E50 0%, #4CA1AF 100%); 
                    padding: 2rem; border-radius: 10px; color: white; margin-bottom: 1rem;'>
            <div style='display: flex; align-items: center; gap: 15px;'>
                <h1 style='margin: 0; font-size: 3rem;'>🗺️</h1>
                <div>
                    <h2 style='margin: 0; color: white;'>Planeación Logística</h2>
                    <p style='margin: 0.5rem 0 0 0; opacity: 0.95; font-size: 1rem;'>
                        Zonificación y rutas para Zacatlán.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Botón directo al mapa
    st.page_link(
        "pages/1_🗺️_Planeacion.py", 
        label="🚀 IR AL MAPA DE PLANEACIÓN",
        use_container_width=True
    )

st.divider()

# Footer
col_f1, col_f2 = st.columns([3,1])
with col_f1: st.caption("Sistema de Inteligencia Estratégica • Zacatlán")
with col_f2: st.caption("v1.0 Dev")