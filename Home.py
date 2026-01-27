import streamlit as st

# Configuración de página principal
st.set_page_config(
    page_title="Sistema Electoral - Zacatlán",
    page_icon="🗳️",
    layout="centered"
)

# CSS personalizado para mejorar la estética
st.markdown("""
<style>
    /* Espaciado general */
    .main > div { padding-top: 2rem; }
    
    /* Estilo para los contenedores (Cards) */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        gap: 1rem;
    }
    
    /* Efecto hover suave en botones */
    div.stButton > button:first-child {
        transition: transform 0.2s ease;
        border: 1px solid #e0e0e0;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        border-color: #5D3FD3;
        color: #5D3FD3;
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
    st.metric("Estatus", "Fase 1", delta="Planeación")

st.markdown("---")

# --- NOTIFICACIÓN DE ESTATUS ---
st.success("✅ **SISTEMA ACTIVO** • Módulo de Planeación habilitado. Resto de módulos en espera de levantamiento.")
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# MÓDULOS OPERATIVOS (GRID 2x2)
# ==============================================================================
st.markdown("### 🛠️ Suite Operativa")

# FILA 1: Planeación y Monitoreo
col_a, col_b = st.columns(2)

# --- 1. PLANEACIÓN (ACTIVO) ---
with col_a:
    with st.container(border=True):
        st.markdown("#### 🗺️ 1. Planeación")
        st.caption("Diseño de muestra, asignación de manzanas y rutas lógicas.")
        st.progress(100, text="Habilitado")
        
        # Enlace directo a la página que SÍ existe
        st.page_link("pages/1_🗺️_Planeacion.py", label="▶️ ACCEDER AL MAPA", use_container_width=True)

# --- 2. MONITOREO (PENDIENTE) ---
with col_b:
    with st.container(border=True):
        st.markdown("#### 📊 2. Monitoreo GPS")
        st.caption("Supervisión en tiempo real del equipo de campo y cobertura.")
        st.progress(0, text="En espera de arranque")
        
        st.button("🔒 Iniciar Supervisión", disabled=True, use_container_width=True, key="btn_mon")

# FILA 2: Auditoría y Resultados
col_c, col_d = st.columns(2)

# --- 3. AUDITORÍA (PENDIENTE) ---
with col_c:
    with st.container(border=True):
        st.markdown("#### 🔍 3. Auditoría")
        st.caption("Validación de audios, revisión de lógica y control de calidad.")
        st.progress(0, text="Requiere datos")
        
        st.button("🔒 Panel de Calidad", disabled=True, use_container_width=True, key="btn_audit")

# --- 4. RESULTADOS (PENDIENTE) ---
with col_d:
    with st.container(border=True):
        st.markdown("#### 📈 4. Resultados")
        st.caption("Tableros finales, cruces de variables, sábanas y careos.")
        st.progress(0, text="Al finalizar captura")
        
        st.button("🔒 Ver Dashboard", disabled=True, use_container_width=True, key="btn_res")

# ==============================================================================
# PROPUESTA DE VALOR (INTELIGENCIA)
# ==============================================================================
st.divider()
st.markdown("### 🚀 Fase 2: Inteligencia Territorial")

with st.container(border=True):
    # Banner Oscuro/Cian
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%); 
                    padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1rem;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h2 style='margin: 0; color: white; font-size: 1.5rem;'>🧠 Micro-Targeting & Activación</h2>
                <span style='background-color: #FFD700; color: #000; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 800;'>PRÓXIMAMENTE</span>
            </div>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9; font-style: italic;'>
                "De la medición a la movilización: Directorio de contactos y mapa de calor."
            </p>
        </div>
    """, unsafe_allow_html=True)

    c_prop1, c_prop2 = st.columns([1.2, 1])
    with c_prop1:
        st.info("**Objetivo:** Conectar directamente vía SMS o Correo con el directorio de contactos recopilado en territorio.")
    with c_prop2:
        st.markdown("""
        * 🗺️ **Mapa de Swing/Bastiones**
        * 🔌 **Directorio de Contactos**
        * 🤖 **Alertas Estratégicas**
        """)

# --- PIE DE PÁGINA ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col_footer1, col_footer2 = st.columns([3, 1])
with col_footer1:
    st.caption("🔒 Sistema de Inteligencia Estratégica • Zacatlán • Data & AI Tech")
with col_footer2:
    st.caption("📅 Enero 2026")