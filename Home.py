import streamlit as st

# Configuración de página principal
st.set_page_config(
    page_title="Sistema Electoral - Zacatlán",
    page_icon="🗳️",
    layout="centered"
)

# CSS personalizado para mejorar la estética (Badges, Sombras, Botones)
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
        border-color: #5D3FD3; /* Morado Institucional */
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
    st.metric("Estatus", "Activo", delta="Fase 1")

st.markdown("---")

# --- NOTIFICACIÓN DE ESTATUS ---
st.success("✅ **PROYECTO EN CURSO** • Módulo de Planeación Logística habilitado.")
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 1. MÓDULO PÚBLICO (RESULTADOS) - DESTACADO
# ==============================================================================
st.markdown("### 🏆 Tablero Ejecutivo")

with st.container(border=True):
    # Banner Azul/Morado para Resultados
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; color: white; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h2 style='margin: 0; color: white;'>📈 Resultados 2025-2026</h2>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.95; font-size: 1.1rem;'>
                Visualización interactiva, comparativos históricos y careos.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("**✓** Preferencia Bruta/Efectiva")
    with c2: st.markdown("**✓** Análisis de Atributos")
    with c3: st.markdown("**✓** Escenarios y Careos")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botón (Desactivado visualmente hasta que crees la página)
    st.button("🔒 Esperando Carga de Datos (Resultados)", disabled=True, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 2. MÓDULOS TÉCNICOS (GRID)
# ==============================================================================
st.markdown("### 🛠️ Módulos Operativos")

# Usamos columnas para crear una rejilla
col_a, col_b = st.columns(2)

# --- CARD PLANEACIÓN (ACTIVO) ---
with col_a:
    with st.container(border=True):
        st.markdown("#### 🗺️ Planeación")
        st.caption("Diseño muestral, cartografía y rutas.")
        st.progress(100, text="Completado")
        
        # Enlace directo a la página que SÍ existe
        st.page_link("pages/1_🗺️_Planeacion.py", label="▶️ ACCEDER AL MAPA", use_container_width=True)

# --- CARD MONITOREO (FUTURO) ---
with col_b:
    with st.container(border=True):
        st.markdown("#### 📊 Monitoreo")
        st.caption("Supervisión GPS y avance en campo.")
        st.progress(0, text="Pendiente de inicio")
        
        st.button("🔒 Iniciar Levantamiento", disabled=True, use_container_width=True, key="btn_monitoreo")

# ==============================================================================
# 3. PROPUESTA DE VALOR (INTELIGENCIA)
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
        * 🔌 **Directorio de Contactos** * 🤖 **Alertas Estratégicas**
        """)

# --- PIE DE PÁGINA ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col_footer1, col_footer2 = st.columns([3, 1])
with col_footer1:
    st.caption("🔒 Sistema de Inteligencia Estratégica • Zacatlán • Data & AI Tech")
with col_footer2:
    st.caption("📅 Enero 2026")