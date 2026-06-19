import streamlit as st

st.set_page_config(page_title="Holzbau Swiss Tool", layout="wide")

st.title("🏗️ Masterclass: Viga Cajón de Doble Nervio")
st.write("Configuración: Tablero CLT inferior + 2 Nervios (Tricapa + Obergurt superior).")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📐 1. Geometría", "⚖️ 2. Cargas", "📊 3. Memoria de Cálculo"])

# --- PESTAÑA 1: GEOMETRÍA ---
with tab1:
    st.header("Definición de la Sección")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Base (Untergurt)")
        b_clt = st.number_input("Ancho tablero CLT (mm)", value=1000)
        h_clt = st.number_input("Espesor tablero CLT (mm)", value=60)
        
    with col2:
        st.subheader("Nervios (Stege + Obergurt)")
        n_nervios = st.number_input("Número de nervios", value=2)
        b_tricapa = st.number_input("Ancho viga Tricapa (mm)", value=40)
        h_tricapa = st.number_input("Canto viga Tricapa (mm)", value=240)
        b_ober = st.number_input("Ancho Obergurt superior (mm)", value=80)
        h_ober = st.number_input("Espesor Obergurt superior (mm)", value=40)

    # --- CÁLCULOS GEOMÉTRICOS ---
    # Alturas de centros de gravedad desde la base (y=0)
    y_clt = h_clt / 2
    y_tri = h_clt + (h_tricapa / 2)
    y_obe = h_clt + h_tricapa + (h_ober / 2)
    h_total = h_clt + h_tricapa + h_ober

    # Áreas
    A_clt = b_clt * h_clt
    A_tri_tot = n_nervios * (b_tricapa * h_tricapa)
    A_obe_tot = n_nervios * (b_ober * h_ober)
    A_total = A_clt + A_tri_tot + A_obe_tot

    # Eje Neutro (Steiner)
    y_gc = (A_clt * y_clt + A_tri_tot * y_tri + A_obe_tot * y_obe) / A_total

    # Inercia Total (I_propio + A*d^2)
    I_clt = (b_clt * h_clt**3)/12 + A_clt * (y_clt - y_gc)**2
    I_tri = n_nervios * ((b_tricapa * h_tricapa**3)/12 + (b_tricapa * h_tricapa) * (y_tri - y_gc)**2)
    I_obe = n_nervios * ((b_ober * h_ober**3)/12 + (b_ober * h_ober) * (y_obe - y_gc)**2)
    I_total = I_clt + I_tri + I_obe

    st.success(f"Sección procesada. Eje Neutro a {y_gc:.2f} mm de la base.")

# --- PESTAÑA 2: CARGAS ---
with tab2:
    st.header("Solicitaciones")
    L_m = st.number_input("Luz de la viga (m)", value=4.5)
    q_knm = st.number_input("Carga total (kN/m)", value=5.0)
    
    M_ed = (q_knm * L_m**2 / 8) * 1e6 # Nmm
    V_ed = (q_knm * L_m / 2) * 1000   # N

# --- PESTAÑA 3: MEMORIA DE CÁLCULO ---
with tab3:
    st.header("🧮 Análisis Mecánico Paso a Paso")
    
    # 1. Inercia
    st.subheader("1. Rigidez Flexural")
    st.write(f"Inercia total de la sección compuesta: **{I_total:,.0f} mm⁴**")
    
    # 2. Tensiones de Flexión
    st.subheader("2. Tensiones Normales")
    sigma_top = (M_ed * (h_total - y_gc)) / I_total
    sigma_bot = (M_ed * y_gc) / I_total
    
    c1, c2 = st.columns(2)
    c1.metric("Compresión en Obergurt", f"{sigma_top:.2f} N/mm²")
    c2.metric("Tracción en CLT inferior", f"{sigma_bot:.2f} N/mm²")

    st.divider()

    # 3. Cortante (El alma Tricapa)
    st.subheader("3. Esfuerzo Cortante")
    # Momento estático del Obergurt superior para ver el rasante
    Q_ober = A_obe_tot * (y_obe - y_gc)
    b_almas = n_nervios * b_tricapa
    tau_alma = (V_ed * Q_ober) / (I_total * b_almas)
    
    st.latex(r"\tau = \frac{V \cdot Q}{I \cdot b_{almas}}")
    st.info(f"Tensión cortante en almas: **{tau_alma:.2f} N/mm²**")

    st.divider()

    # 4. Flecha
    st.subheader("4. Deformación (Estado Límite de Servicio)")
    E_mean = 11000
    L_mm = L_m * 1000
    flecha = (5 * q_knm * L_mm**4) / (384 * E_mean * I_total)
    
    st.metric("FLECHA MÁXIMA", f"{flecha:.2f} mm")
    st.write(f"Límite L/300: **{L_mm/300:.2f} mm**")
    
    if flecha < (L_mm/300):
        st.success("La rigidez es adecuada.")
    else:
        st.error("La viga flecta demasiado. Aumenta el canto de la Tricapa.")
