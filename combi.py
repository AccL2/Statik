import streamlit as st
import pandas as pd

st.set_page_config(page_title="Combinaciones Forjado", layout="wide")

# =========================================================
# ESTILO GENERAL
# =========================================================

st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.envelope-card {
    background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
    border: 1px solid #bfdbfe; border-radius: 12px; padding: 20px;
    margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.envelope-title {
    font-size: 1.1rem; font-weight: 700; color: #1e3a8a;
    margin-bottom: 8px; border-bottom: 2px solid #dbeafe; padding-bottom: 4px;
}
.val-highlight { font-size: 1.8rem; font-weight: 800; color: #111827; }
.val-sub { font-size: 0.95rem; color: #4b5563; font-weight: 500; margin-top: 4px; }
.math-box {
    background: #1e293b; color: #f8fafc; font-family: monospace;
    padding: 12px 16px; border-radius: 8px; margin: 10px 0; font-size: 1.05rem;
}
.math-res { color: #10b981; font-weight: bold; }
.badge-winner {
    background: #fef08a; color: #854d0e; padding: 4px 10px;
    border-radius: 99px; font-size: 0.85rem; font-weight: bold;
    display: inline-block; margin-bottom: 10px; border: 1px solid #fde047;
}
.expl-box {
    background: #f0fdf4; border-left: 4px solid #22c55e;
    padding: 12px 16px; border-radius: 4px; color: #166534; font-size: 0.95rem;
}
.blue-box {
    background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a;
    padding: 12px 14px; border-radius: 8px; margin-bottom: 1rem; font-size: 0.95rem;
}
.small-gray { color: #6b7280; font-size: 0.92rem; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTES (NORMATIVA)
# =========================================================

GAMMA_G = 1.35
GAMMA_Q = 1.50
PSI0_VIV = 0.70
PSI2_VIV = 0.30

# =========================================================
# FUNCIONES MECÁNICAS
# =========================================================

def convertir_a_lineal(Gk_m2, Quk_m2, s_m):
    return Gk_m2 * s_m, Quk_m2 * s_m

def calcular_esfuerzos(q_kNm, P_kN, L_m):
    M_q = q_kNm * L_m**2 / 8.0
    M_P = P_kN * L_m / 4.0
    V_q = q_kNm * L_m / 2.0
    V_P = P_kN / 2.0
    
    return {
        "M": M_q + M_P, "V": V_q + V_P,
        "Mq": M_q, "Mp": M_P,
        "Vq": V_q, "Vp": V_P
    }

# =========================================================
# GENERACIÓN DE COMBINACIONES
# =========================================================

def generar_todas_las_combinaciones(gk, quk, Qpk, L):
    combos = []
    
    # --- ELU ---
    q1 = GAMMA_G * gk; P1 = 0.0
    r1 = calcular_esfuerzos(q1, P1, L)
    combos.append({
        "id": "ELU-1", "tipo": "ELU", "nombre": "Solo permanente",
        "form_q": f"{GAMMA_G}·Gk", "num_q": f"{GAMMA_G} · {gk:.2f}",
        "form_P": "0", "num_P": "0",
        "q": q1, "P": P1, **r1,
        "explicacion": "Comprobación base. A veces la carga de uso actúa como contrapeso (favorable). Por eso se comprueba la viga solo con su peso propio mayorado al 35%."
    })

    q2 = GAMMA_G * gk + GAMMA_Q * quk; P2 = GAMMA_Q * PSI0_VIV * Qpk
    r2 = calcular_esfuerzos(q2, P2, L)
    combos.append({
        "id": "ELU-2", "tipo": "ELU", "nombre": "Uniforme dominante",
        "form_q": f"{GAMMA_G}·Gk + {GAMMA_Q}·Qu,k", "num_q": f"{GAMMA_G} · {gk:.2f} + {GAMMA_Q} · {quk:.2f}",
        "form_P": f"{GAMMA_Q}·ψ0·Qp,k", "num_P": f"{GAMMA_Q} · {PSI0_VIV} · {Qpk:.2f}",
        "q": q2, "P": P2, **r2,
        "explicacion": "La carga repartida es la 'Jefa' (al 100%). La carga puntual es 'acompañante' y se reduce con ψ0 (70%) porque es casi imposible que se den ambos máximos absolutos a la vez."
    })

    q3 = GAMMA_G * gk + GAMMA_Q * PSI0_VIV * quk; P3 = GAMMA_Q * Qpk
    r3 = calcular_esfuerzos(q3, P3, L)
    combos.append({
        "id": "ELU-3", "tipo": "ELU", "nombre": "Puntual dominante",
        "form_q": f"{GAMMA_G}·Gk + {GAMMA_Q}·ψ0·Qu,k", "num_q": f"{GAMMA_G} · {gk:.2f} + {GAMMA_Q} · {PSI0_VIV} · {quk:.2f}",
        "form_P": f"{GAMMA_Q}·Qp,k", "num_P": f"{GAMMA_Q} · {Qpk:.2f}",
        "q": q3, "P": P3, **r3,
        "explicacion": "Al revés que la anterior. La carga puntual (ej. una caja fuerte) manda al 100%. El resto de la vivienda se considera a un uso normal (reducido al 70%)."
    })

    # --- ELS INSTANTÁNEO ---
    q4 = gk + quk; P4 = PSI0_VIV * Qpk
    r4 = calcular_esfuerzos(q4, P4, L)
    combos.append({
        "id": "ELS-1", "tipo": "ELS_INST", "nombre": "Instantánea Uniforme dom.",
        "form_q": "Gk + Qu,k", "num_q": f"{gk:.2f} + {quk:.2f}",
        "form_P": "ψ0·Qp,k", "num_P": f"{PSI0_VIV} · {Qpk:.2f}",
        "q": q4, "P": P4, **r4,
        "explicacion": "Combinación sin factores de seguridad (valores reales). Sirve para ver cuánto bajará la viga el primer día (flecha instantánea)."
    })

    q5 = gk + PSI0_VIV * quk; P5 = Qpk
    r5 = calcular_esfuerzos(q5, P5, L)
    combos.append({
        "id": "ELS-2", "tipo": "ELS_INST", "nombre": "Instantánea Puntual dom.",
        "form_q": "Gk + ψ0·Qu,k", "num_q": f"{gk:.2f} + {PSI0_VIV} · {quk:.2f}",
        "form_P": "Qp,k", "num_P": f"{Qpk:.2f}",
        "q": q5, "P": P5, **r5,
        "explicacion": "Igual que la anterior, pero asumiendo que la carga puntual es la principal para la flecha del primer día."
    })

    # --- ELS CUASI-PERMANENTE ---
    q6 = gk + PSI2_VIV * quk; P6 = PSI2_VIV * Qpk
    r6 = calcular_esfuerzos(q6, P6, L)
    combos.append({
        "id": "ELS-QP", "tipo": "ELS_QP", "nombre": "Cuasi-permanente",
        "form_q": "Gk + ψ2·Qu,k", "num_q": f"{gk:.2f} + {PSI2_VIV} · {quk:.2f}",
        "form_P": "ψ2·Qp,k", "num_P": f"{PSI2_VIV} · {Qpk:.2f}",
        "q": q6, "P": P6, **r6,
        "explicacion": "Esta es la clave de la madera. Nos dice qué parte de la carga de uso se queda 'a vivir' para siempre (30% en viviendas). Solo esta carga producirá fluencia (kdef) a los 30 años."
    })

    return combos

# =========================================================
# INTERFAZ DE USUARIO
# =========================================================

st.title("Forjado: Acciones y Combinaciones")

# --- GUÍA DIVULGATIVA (COLLAPSIBLE) ---
with st.expander("📚 Guía del Maestro: ¿De dónde salen estos coeficientes?", expanded=False):
    st.markdown("""
    En el cálculo estructural no sumamos cargas a lo loco. Usamos combinaciones basadas en la probabilidad.
    
    *   **$\gamma_G = 1.35$ (Margen Peso Propio):** Añadimos un 35% de seguridad al peso de la estructura.
    *   **$\gamma_Q = 1.50$ (Margen Uso):** Añadimos un 50% de seguridad a la sobrecarga. Es impredecible saber cuánta gente entrará.
    *   **$\psi_0 = 0.70$ (Alternancia):** Si la habitación está a tope de gente (100%), es muy poco probable que además haya una carga puntual pesada en el peor sitio (100%). A la carga 'secundaria' se le aplica un 0.7.
    *   **$\psi_2 = 0.30$ (El factor del tiempo):** La madera fluye bajo carga sostenida. El Eurocódigo estima que en una vivienda, en promedio, solo el 30% de esa carga está ahí *permanentemente*. Esa es la que se multiplicará por el famoso `kdef`.
    """)

st.markdown("""
<div class="blue-box">
<b>Hipótesis del modelo:</b> Viga biapoyada de forjado residencial. 
Se combinan cargas superficiales permanentes (Gk) y de uso uniforme (Qu,k) transformadas en lineales mediante 
el ancho tributario (s), junto con una carga de uso puntual (Qp,k) centrada en el vano.
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: DATOS ---
st.sidebar.header("1. Geometría")
L_m = st.sidebar.number_input("Luz de la viga L [m]", value=4.50, step=0.10, min_value=0.50)
s_m = st.sidebar.number_input("Ancho tributario s [m]", value=0.60, step=0.05, min_value=0.10)

st.sidebar.header("2. Cargas Características")
Gk_m2 = st.sidebar.number_input("Permanente Gk [kN/m²]", value=1.50, step=0.10)
Quk_m2 = st.sidebar.number_input("Sobrecarga Uniforme Qu,k [kN/m²]", value=2.00, step=0.10)
Qpk_kN = st.sidebar.number_input("Puntual Qp,k [kN]", value=2.00, step=0.10)

# --- CÁLCULOS ---
gk, quk = convertir_a_lineal(Gk_m2, Quk_m2, s_m)
combos = generar_todas_las_combinaciones(gk, quk, Qpk_kN, L_m)

combos_elu = [c for c in combos if c["tipo"] == "ELU"]
combos_els_inst = [c for c in combos if c["tipo"] == "ELS_INST"]
combo_qp = [c for c in combos if c["tipo"] == "ELS_QP"][0]

elu_max_M = max(combos_elu, key=lambda x: x["M"])
elu_max_V = max(combos_elu, key=lambda x: x["V"])
els_inst_max_M = max(combos_els_inst, key=lambda x: x["M"])

# --- CONVERSIÓN DE CARGAS ---
st.subheader("Cargas sobre la viga (Base sin mayorar)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Luz (L)", f"{L_m:.2f} m")
c2.metric("Permanente lineal (gk)", f"{gk:.2f} kN/m")
c3.metric("Uso lineal (qu,k)", f"{quk:.2f} kN/m")
c4.metric("Uso puntual (Qp,k)", f"{Qpk_kN:.2f} kN")
st.markdown('<div class="small-gray">gk = Gk · s &nbsp;&nbsp;|&nbsp;&nbsp; qu,k = Qu,k · s</div>', unsafe_allow_html=True)
st.divider()

# --- ENVOLVENTES ---
st.subheader("Envolventes de Cálculo (Valores Críticos)")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="envelope-card">
        <div class="envelope-title">🔥 ELU (Resistencia / Rotura)</div>
        <div class="val-highlight">{elu_max_M['M']:.2f} <span style="font-size:1rem;font-weight:500;">kN·m</span></div>
        <div class="val-sub">M<sub>d</sub> máximo • <span style="color:#2563eb;">{elu_max_M['id']}</span></div>
        <div style="margin-top:12px;"></div>
        <div class="val-highlight">{elu_max_V['V']:.2f} <span style="font-size:1rem;font-weight:500;">kN</span></div>
        <div class="val-sub">V<sub>d</sub> máximo • <span style="color:#2563eb;">{elu_max_V['id']}</span></div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="envelope-card" style="background: linear-gradient(135deg, #f8fafc 0%, #f0fdf4 100%); border-color: #bbf7d0;">
        <div class="envelope-title" style="color: #166534; border-bottom-color: #dcfce7;">📏 ELS Instantáneo (Flecha)</div>
        <div class="val-highlight">{els_inst_max_M['M']:.2f} <span style="font-size:1rem;font-weight:500;">kN·m</span></div>
        <div class="val-sub">M<sub>inst</sub> máximo • <span style="color:#059669;">{els_inst_max_M['id']}</span></div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="envelope-card" style="background: linear-gradient(135deg, #fdf8f6 0%, #fef3c7 100%); border-color: #fde047;">
        <div class="envelope-title" style="color: #854d0e; border-bottom-color: #fef08a;">⏳ ELS Cuasi-permanente (Fluencia)</div>
        <div class="val-highlight">{combo_qp['q']:.2f} <span style="font-size:1rem;font-weight:500;">kN/m</span></div>
        <div class="val-sub">Carga lineal base (q<sub>qp</sub>)</div>
        <div style="margin-top:12px;"></div>
        <div class="val-highlight">{combo_qp['P']:.2f} <span style="font-size:1rem;font-weight:500;">kN</span></div>
        <div class="val-sub">Carga puntual base (P<sub>qp</sub>)</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- EXPLORADOR INTERACTIVO ---
st.header("🔍 Explorador de Combinaciones")
st.markdown("Selecciona una combinación para destripar su cálculo.")

opciones_combos = {f"[{c['id']}] {c['nombre']}": c for c in combos}
seleccion = st.selectbox("Elige combinación:", list(opciones_combos.keys()), label_visibility="collapsed")
c_sel = opciones_combos[seleccion]

# Lógica de ganador
es_max_M = (c_sel["id"] == elu_max_M["id"])
es_max_V = (c_sel["id"] == elu_max_V["id"])
if es_max_M or es_max_V:
    mensaje = []
    if es_max_M: mensaje.append("Momento (ELU)")
    if es_max_V: mensaje.append("Cortante (ELU)")
    st.markdown(f"<div class='badge-winner'>🏆 Gobernante para: {' y '.join(mensaje)}</div>", unsafe_allow_html=True)

colA, colB = st.columns([1.1, 1.3])

with colA:
    st.markdown("**1. Cargas de la combinación**")
    st.markdown(f"""
    <div class="math-box">
    q = {c_sel['form_q']}<br>
    q = {c_sel['num_q']} = <span class="math-res">{c_sel['q']:.2f} kN/m</span>
    <hr style="border-color:#334155; margin:10px 0;">
    P = {c_sel['form_P']}<br>
    P = {c_sel['num_P']} = <span class="math-res">{c_sel['P']:.2f} kN</span>
    </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown("**2. Esfuerzos resultantes (Desglose Lineal + Puntual)**")
    st.markdown(f"""
    <div class="math-box" style="background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1;">
    M<sub>max</sub> = M<sub>q</sub> + M<sub>P</sub> = (q·L²/8) + (P·L/4)<br>
    M<sub>max</sub> = {c_sel['Mq']:.2f} + {c_sel['Mp']:.2f} = <span style="color:#2563eb; font-weight:bold;">{c_sel['M']:.2f} kN·m</span>
    <hr style="border-color:#e2e8f0; margin:10px 0;">
    V<sub>max</sub> = V<sub>q</sub> + V<sub>P</sub> = (q·L/2) + (P/2)<br>
    V<sub>max</sub> = {c_sel['Vq']:.2f} + {c_sel['Vp']:.2f} = <span style="color:#2563eb; font-weight:bold;">{c_sel['V']:.2f} kN</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("**3. ¿Qué significa esto en el cálculo real?**")
st.markdown(f"<div class='expl-box'>{c_sel['explicacion']}</div>", unsafe_allow_html=True)

st.divider()

# --- TABLAS Y MATEMÁTICAS ---
st.header("Tablas Resumen y Desarrollo")

tab1, tab2 = st.tabs(["📊 Tablas de Combinaciones", "🧮 Fórmulas de Cálculo"])

with tab1:
    def mostrar_df(combos_list):
        df = pd.DataFrame(combos_list)
        df_show = df[["id", "nombre", "q", "P", "M", "V"]].copy()
        df_show.columns = ["ID", "Combinación", "q [kN/m]", "P [kN]", "Momento [kN·m]", "Cortante [kN]"]
        for col in ["q [kN/m]", "P [kN]", "Momento [kN·m]", "Cortante [kN]"]:
            df_show[col] = df_show[col].apply(lambda x: f"{x:.3f}")
        st.dataframe(df_show, use_container_width=True, hide_index=True)

    st.subheader("ELU (Estado Límite Último)")
    mostrar_df(combos_elu)
    st.subheader("ELS (Estado Límite de Servicio)")
    mostrar_df(combos_els_inst + [combo_qp])

with tab2:
    st.write("**Conversión de cargas superficiales a lineales**")
    st.latex(rf"g_k = G_k \cdot s = {Gk_m2:.2f} \cdot {s_m:.2f} = {gk:.3f}\ \mathrm{{kN/m}}")
    st.latex(rf"q_{{u,k}} = Q_{{u,k}} \cdot s = {Quk_m2:.2f} \cdot {s_m:.2f} = {quk:.3f}\ \mathrm{{kN/m}}")

    st.write("**Esfuerzos máximos en viga biapoyada**")
    st.latex(r"M_{max} = q\frac{L^2}{8} + P\frac{L}{4}")
    st.latex(r"V_{max} = q\frac{L}{2} + \frac{P}{2}")
    
    st.write("**Coeficientes Normativos**")
    st.latex(rf"\gamma_G = {GAMMA_G:.2f} \quad \gamma_Q = {GAMMA_Q:.2f} \quad \psi_0 = {PSI0_VIV:.2f} \quad \psi_2 = {PSI2_VIV:.2f}")