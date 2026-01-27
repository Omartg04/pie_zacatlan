import streamlit as st
import bcrypt

# ==============================================================================
# 🔐 CONFIGURACIÓN DE SEGURIDAD
# ==============================================================================
# Hashes por defecto para desarrollo (Usuario: admin / Clave: admin123)
# Puedes generar nuevos hashes con tu script generador si lo deseas.
CREDENCIALES_HASH = {
    "admin": "$2b$12$E9/z.z.z.z.z.z.z.z.z.z.z.z.z.z.z.z.z.z.z.z.z.z.z.z", # admin123 (Simulado para que no falle si no tienes hash real)
    "zacatlan": "$2b$12$R9..." # Placeholder
}

# Si quieres entrar RÁPIDO sin pelearte con hashes ahora mismo, 
# podemos usar un modo "Dev" que acepta texto plano temporalmente,
# o usar el hash real de "admin123" si lo tienes.

def bloquear_acceso():
    """
    Verifica credenciales.
    """
    # 1. Inicializar sesión
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if "usuario_actual" not in st.session_state:
        st.session_state["usuario_actual"] = None

    # 2. Si NO está autenticado, mostrar Login
    if not st.session_state["autenticado"]:
        # Diseño limpio del Login
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Acceso Zacatlán")
            
            user_input = st.text_input("Usuario")
            pass_input = st.text_input("Contraseña", type="password")
            
            if st.button("Iniciar Sesión", type="primary", use_container_width=True):
                # --- MODO DESARROLLO RÁPIDO ---
                # Para que puedas trabajar YA, permitimos 'admin' / 'admin'
                if user_input == "admin" and pass_input == "admin":
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_actual"] = user_input
                    st.toast(f"¡Bienvenido, {user_input}!", icon="👋")
                    st.rerun()
                # ------------------------------
                
                # Validación real con Hash (cuando tengas los hashes listos)
                elif user_input in CREDENCIALES_HASH:
                    # Aquí iría la validación bcrypt real
                    # if bcrypt.checkpw(...)
                    st.error("Por favor usa usuario: admin / contraseña: admin para desarrollo.")
                else:
                    st.error("❌ Credenciales incorrectas.")
        
        st.stop()

    # 3. Si YA está autenticado, mostrar Sidebar
    else:
        with st.sidebar:
            st.write(f"👤 **{st.session_state['usuario_actual']}**")
            if st.button("🔒 Salir", use_container_width=True):
                st.session_state["autenticado"] = False
                st.session_state["usuario_actual"] = None
                st.rerun()
            st.divider()
            
    return True