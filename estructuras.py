import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import math
import plotly.graph_objects as go

# =========================================================
# CONFIGURACIÓN Y ESTILO GLOBAL
# =========================================================
st.set_page_config(page_title="Holzbau Pro", layout="wide", page_icon="🌲")

st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.envelope-card { background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border: 1px solid #bfdbfe; border-radius: 12px; padding: 20px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
.envelope-title { font-size: 1.1rem; font-weight: 700; color: #1e3a8a; margin-bottom: 8px; border-bottom: 2px solid #dbeafe; padding-bottom: 4px; }
.val-highlight { font-size: 1.8rem; font-weight: 800; color: #111827; }
.val-sub { font-size: 0.95rem; color: #4b5563; font-weight: 500; margin-top: 4px; }
.math-box { background: #1e293b; color: #f8fafc; font-family: monospace; padding: 12px 16px; border-radius: 8px; margin: 10px 0; font-size: 1.05rem; }
.math-res { color: #10b981; font-weight: bold; }
.badge-winner { background: #fef08a; color: #854d0e; padding: 4px 10px; border-radius: 99px; font-size: 0.85rem; font-weight: bold; display: inline-block; margin-bottom: 10px; border: 1px solid #fde047; }
.expl-box { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 12px 16px; border-radius: 4px; color: #166534; font-size: 0.95rem; margin-top: 10px; }
.blue-box { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; padding: 12px 14px; border-radius: 8px; margin-bottom: 1rem; font-size: 0.95rem; }
.link-box { background: #faf5ff; border: 1px dashed #fde047; color: #854d0e; padding: 10px 14px; border-radius: 8px; margin-bottom: 1rem; font-size: 0.95rem; font-weight: 500;}
.small-gray { color: #6b7280; font-size: 0.92rem; }
.result-box { padding: 1rem 1.2rem; border-radius: 14px; margin-bottom: 1rem; border: 1px solid #e5e7eb; background: #f9fafb; }
.result-ok { background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border: 1px solid #10b981; color: #065f46; }
.result-bad { background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border: 1px solid #ef4444; color: #991b1b; }
.title-day1 { color: #2563eb; font-size: 1.2rem; font-weight: 700; border-bottom: 2px solid #bfdbfe; padding-bottom: 5px;}
.title-activa { color: #d97706; font-size: 1.2rem; font-weight: 700; border-bottom: 2px solid #fde047; padding-bottom: 5px;}
.title-day10k { color: #dc2626; font-size: 1.2rem; font-weight: 700; border-bottom: 2px solid #fca5a5; padding-bottom: 5px;}
.badge-ok { background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 99px; font-weight: bold; border: 1px solid #bbf7d0;}
.badge-bad { background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 99px; font-weight: bold; border: 1px solid #fecaca;}
.title-main { color: #1e293b; font-size: 1.3rem; font-weight: 700; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 15px;}
.story-box { padding: 15px; border-radius: 8px; margin-bottom: 15px; height: 100%;}
.story-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 8px; margin-top: 0;}
.global-summary { background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px 12px; border-radius: 6px; font-size: 0.9rem; color: #475569; margin-bottom: 15px; display: flex; gap: 20px; flex-wrap: wrap; }
/* NUEVA TABLA COMBINACIONES */
.tabla-combis { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.95rem; margin-top: 15px; margin-bottom: 25px;}
.tabla-combis th { background-color: #f1f5f9; color: #334155; font-weight: 700; text-align: left; padding: 12px 10px; border-bottom: 2px solid #cbd5e1; }
.tabla-combis td { padding: 10px; border-bottom: 1px solid #e2e8f0; color: #475569; }
.tabla-combis tr:nth-child(even) { background-color: #f8fafc; }
.tabla-combis td.bold-col { font-weight: 700; color: #0f172a; }
.tabla-combis td.val-col { color: #0369a1; font-weight: 600; text-align: center; }
.tabla-combis th.center { text-align: center; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# BASES DE DATOS GLOBALES
# =========================================================
MATERIALES = {
    "C14": {"f_m_k": 14.0, "f_t_0_k": 8.0,  "f_c_0_k": 16.0, "f_v_k": 3.0, "E_0_mean": 7000, "E_0_05": 4700, "rho_k": 290, "rho_mean": 350},
    "C16": {"f_m_k": 16.0, "f_t_0_k": 10.0, "f_c_0_k": 17.0, "f_v_k": 3.2, "E_0_mean": 8000, "E_0_05": 5400, "rho_k": 310, "rho_mean": 370},
    "C18": {"f_m_k": 18.0, "f_t_0_k": 11.0, "f_c_0_k": 18.0, "f_v_k": 3.4, "E_0_mean": 9000, "E_0_05": 6000, "rho_k": 320, "rho_mean": 380},
    "C24": {"f_m_k": 24.0, "f_t_0_k": 14.5, "f_c_0_k": 21.0, "f_v_k": 4.0, "E_0_mean": 11000, "E_0_05": 7400, "rho_k": 350, "rho_mean": 420},
    "C30": {"f_m_k": 30.0, "f_t_0_k": 18.0, "f_c_0_k": 26.0, "f_v_k": 4.0, "E_0_mean": 12000, "E_0_05": 8000, "rho_k": 380, "rho_mean": 460},
    "GL24h": {"f_m_k": 24.0, "f_t_0_k": 16.5, "f_c_0_k": 24.0, "f_v_k": 3.5, "E_0_mean": 11600, "E_0_05": 9600, "rho_k": 385, "rho_mean": 430},
    "GL28h": {"f_m_k": 28.0, "f_t_0_k": 19.5, "f_c_0_k": 26.5, "f_v_k": 3.5, "E_0_mean": 12600, "E_0_05": 10500, "rho_k": 425, "rho_mean": 460},
    "GL32h": {"f_m_k": 32.0, "f_t_0_k": 22.5, "f_c_0_k": 29.0, "f_v_k": 3.8, "E_0_mean": 13700, "E_0_05": 11400, "rho_k": 440, "rho_mean": 490},
}
KMOD_TABLA = {
    "1": {"Permanente": 0.60, "Larga": 0.70, "Media": 0.80, "Corta": 0.90, "Instantánea": 1.10},
    "2": {"Permanente": 0.60, "Larga": 0.70, "Media": 0.80, "Corta": 0.90, "Instantánea": 1.10},
    "3": {"Permanente": 0.50, "Larga": 0.55, "Media": 0.65, "Corta": 0.70, "Instantánea": 0.90},
}
KDEF_DICT = {"1": 0.60, "2": 0.80, "3": 2.00}

GAMMA_G, GAMMA_Q, PSI2_VIV = 1.35, 1.50, 0.30
K_CR = 0.67

# =========================================================
# FUNCIONES AUXILIARES GLOBALES
# =========================================================
def obtener_propiedades_material(material): return MATERIALES[material]
def obtener_k_mod(clase_servicio, duracion): return KMOD_TABLA[clase_servicio][duracion]
def calcular_propiedades_geometricas_rectangulo(b_mm, h_mm):
    A = b_mm * h_mm
    I_y = b_mm * h_mm**3 / 12
    I_z = h_mm * b_mm**3 / 12
    W_y = I_y / (h_mm / 2) if h_mm > 0 else 0
    W_z = I_z / (b_mm / 2) if b_mm > 0 else 0
    return {"A": A, "I_y": I_y, "I_z": I_z, "W_y": W_y, "W_z": W_z}

def convertir_a_lineal(Gk_m2, Quk_m2, s_m, b_mm, h_mm, densidad_mean): 
    area_m2 = (b_mm / 1000) * (h_mm / 1000)
    peso_viga_kN_m = area_m2 * (densidad_mean * 9.81 / 1000) 
    gk_total = (Gk_m2 * s_m) + peso_viga_kN_m
    quk = Quk_m2 * s_m
    return gk_total, quk, peso_viga_kN_m

def calcular_esfuerzos(q_kNm, P_kN, L_m, pos_P=None):
    if pos_P is None:
        pos_P = L_m / 2.0
        
    Ra = q_kNm * L_m / 2.0 + P_kN * (L_m - pos_P) / L_m
    Rb = q_kNm * L_m / 2.0 + P_kN * pos_P / L_m
    V_max = max(Ra, Rb)
    
    M_candidatos = []
    M_candidatos.append(Ra * pos_P - 0.5 * q_kNm * pos_P**2) 
    if q_kNm > 0:
        x_zero_shear = Ra / q_kNm
        if 0 <= x_zero_shear <= pos_P:
            M_candidatos.append(Ra * x_zero_shear - 0.5 * q_kNm * x_zero_shear**2)
    M_candidatos.append(q_kNm * L_m**2 / 8.0) 
    M_max = max(M_candidatos)
    
    return {"M": M_max, "V": V_max, "pos_P": pos_P}

def generar_todas_las_combinaciones(gk, quk, Qpk, L, h_m):
    combos = []
    
    # ELU-1
    q1 = GAMMA_G * gk; P1 = 0.0
    combos.append({"id": "ELU1", "tipo": "ELU", "nombre": "1.35·CC1", "form_q": f"{GAMMA_G}·Gk", "num_q": f"{GAMMA_G} · {gk:.3f}", "form_P": "0", "num_P": "0", "q": q1, "P": P1, "duracion": "Permanente", **calcular_esfuerzos(q1, P1, L, L/2), "explicacion": "Solo carga permanente mayorada."})
    
    # ELU-2 (Uniforme)
    q2 = GAMMA_G * gk + GAMMA_Q * quk; P2 = 0.0
    combos.append({"id": "ELU2", "tipo": "ELU", "nombre": "1.35·CC1 + 1.50·CC2", "form_q": f"{GAMMA_G}·Gk + {GAMMA_Q}·Qu,k", "num_q": f"{GAMMA_G} · {gk:.3f} + {GAMMA_Q} · {quk:.3f}", "form_P": "0", "num_P": "0", "q": q2, "P": P2, "duracion": "Media", **calcular_esfuerzos(q2, P2, L, L/2), "explicacion": "Carga de uso uniforme. Situación persistente dominante."})
    
    # ELU-3 (Puntual al centro -> Flector)
    q3 = GAMMA_G * gk; P3 = GAMMA_Q * Qpk
    combos.append({"id": "ELU3", "tipo": "ELU", "nombre": "1.35·CC1 + 1.50·CC2.1", "form_q": f"{GAMMA_G}·Gk", "num_q": f"{GAMMA_G} · {gk:.3f}", "form_P": f"{GAMMA_Q}·Qp,k", "num_P": f"{GAMMA_Q} · {Qpk:.3f}", "q": q3, "P": P3, "duracion": "Media", **calcular_esfuerzos(q3, P3, L, L/2), "explicacion": "Carga puntual situada en el centro (L/2). Esta posición genera el máximo Momento Flector."})
    
    # ELU-4 (Puntual al apoyo -> Cortante)
    pos_P4 = max(L - h_m, L/2) 
    combos.append({"id": "ELU4", "tipo": "ELU", "nombre": "1.35·CC1 + 1.50·CC2.2", "form_q": f"{GAMMA_G}·Gk", "num_q": f"{GAMMA_G} · {gk:.3f}", "form_P": f"{GAMMA_Q}·Qp,k", "num_P": f"{GAMMA_Q} · {Qpk:.3f}", "q": q3, "P": P3, "duracion": "Media", **calcular_esfuerzos(q3, P3, L, pos_P4), "explicacion": "Carga puntual situada a distancia 'h' del apoyo (L-h). Esta posición genera el máximo Esfuerzo Cortante."})
    
    # ELS
    q4 = gk + quk; P4 = 0.0
    combos.append({"id": "ELS-1", "tipo": "ELS_INST", "nombre": "Inst. Uniforme dom.", "form_q": "Gk + Qu,k", "num_q": f"{gk:.3f} + {quk:.3f}", "form_P": "0", "num_P": "0", "q": q4, "P": P4, "duracion": "Instantánea", **calcular_esfuerzos(q4, P4, L, L/2), "explicacion": "Flecha instantánea asumiendo el forjado con la carga uniforme."})
    
    q5 = gk; P5 = Qpk
    combos.append({"id": "ELS-2", "tipo": "ELS_INST", "nombre": "Inst. Puntual dom.", "form_q": "Gk", "num_q": f"{gk:.3f}", "form_P": "Qp,k", "num_P": f"{Qpk:.3f}", "q": q5, "P": P5, "duracion": "Instantánea", **calcular_esfuerzos(q5, P5, L, L/2), "explicacion": "Flecha instantánea local producida por el objeto pesado en el centro."})
    
    q6 = gk + PSI2_VIV * quk; P6 = 0.0
    combos.append({"id": "ELS-QP", "tipo": "ELS_QP", "nombre": "Cuasi-permanente", "form_q": "Gk + ψ2·Qu,k", "num_q": f"{gk:.3f} + {PSI2_VIV} · {quk:.3f}", "form_P": "0", "num_P": "0", "q": q6, "P": P6, "duracion": "Permanente", **calcular_esfuerzos(q6, P6, L, L/2), "explicacion": "Cargas que se quedan a vivir. Generan fluencia a lo largo de los años."})
    
    return combos

def mostrar_resumen_global():
    st.markdown(f"""
    <div class="global-summary">
        <div><b>Sección:</b> {b_mm}x{h_mm} mm</div>
        <div><b>Luz:</b> {L_m:.2f} m</div>
        <div><b>Material:</b> {mat} (Clase Serv. {clase_servicio})</div>
        <div><b>k_sys:</b> {k_sys:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# MENÚ LATERAL GLOBAL (Navegación e Inputs Globales)
# =========================================================
st.sidebar.markdown("## 🧭 Navegación")
page = st.sidebar.radio(
    "Ir a...",
    [
        "🏠 1. Combinaciones",
        "📐 2. Flexión y Axil",
        "✂️ 3. Cortante ($k_{cr}$)",
        "📏 4. Flecha y $k_{def}$",
        "📳 5. Vibraciones",
        "🔥 6. Fuego (EC5)",
        "📊 7. Diagramas de Esfuerzos",
        "📑 8. Resultados"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.markdown("### 📐 Geometría y Sección")
L_m = st.sidebar.number_input("Luz de la viga L [m]", value=5.00, step=0.10, min_value=0.50)
s_m = st.sidebar.number_input("Ancho tributario s [m]", value=1.00, step=0.05, min_value=0.10)
b_mm = st.sidebar.number_input("Base viga b [mm]", value=120, step=10)
h_mm = st.sidebar.number_input("Canto viga h [mm]", value=280, step=10)

st.sidebar.markdown("### ⚖️ Cargas (Valores Base)")
Gk_m2 = st.sidebar.number_input("Permanente Gk [kN/m²]", value=1.00, step=0.10)
Quk_m2 = st.sidebar.number_input("Uso Uniforme Qu,k [kN/m²]", value=2.00, step=0.10)
Qpk_kN = st.sidebar.number_input("Sobrecarga Puntual Qp,k [kN]", value=2.00, step=0.10)

st.sidebar.markdown("### 🌲 Material y Entorno")
mat = st.sidebar.selectbox("Clase de Madera", list(MATERIALES.keys()), index=5)
clase_servicio = st.sidebar.selectbox("Clase de Servicio", ["1", "2", "3"], index=0)
k_sys_active = st.sidebar.checkbox("Activar k_sys (Forjado colaborante)", value=False, help="Aplica un factor k_sys = 1.10.")
k_sys = 1.10 if k_sys_active else 1.00

# =========================================================
# CÁLCULOS GLOBALES EN SEGUNDO PLANO
# =========================================================
props_geo = calcular_propiedades_geometricas_rectangulo(b_mm, h_mm)
props_mat = obtener_propiedades_material(mat)

gk, quk, peso_viga = convertir_a_lineal(Gk_m2, Quk_m2, s_m, b_mm, h_mm, props_mat["rho_mean"])
combos = generar_todas_las_combinaciones(gk, quk, Qpk_kN, L_m, h_mm/1000.0)

combos_elu = [c for c in combos if c["tipo"] == "ELU"]
combos_els_inst = [c for c in combos if c["tipo"] == "ELS_INST"]
combo_qp = [c for c in combos if c["tipo"] == "ELS_QP"][0]

elu_max_M = max(combos_elu, key=lambda x: x["M"])
elu_max_V = max(combos_elu, key=lambda x: x["V"])
els_inst_max_M = max(combos_els_inst, key=lambda x: x["M"])

duracion_M = "Permanente" if elu_max_M['id'] == "ELU1" else "Media"
duracion_V = "Permanente" if elu_max_V['id'] == "ELU1" else "Media"

# -----------------------------------------------------------------------------
# PÁGINA 1: COMBINACIONES
# -----------------------------------------------------------------------------
if page == "🏠 1. Combinaciones":
    st.title("Forjado: Acciones y Combinaciones (EC 1991-1-1)")
    mostrar_resumen_global()

    st.markdown("""
    <div class="blue-box">
    <b>Actualizado a Eurocódigo 1:</b> El sistema evalúa la carga puntual en dos posiciones críticas de forma automática. En el centro genera el flector máximo (CC2.1) y cerca del apoyo genera el cortante máximo (CC2.2). Además, el programa calcula y añade de forma automática el <b>peso propio de la viga</b>.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Cargas sobre la viga (Base sin mayorar)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Luz (L)", f"{L_m:.2f} m")
    c2.metric("Permanente lineal (gk)", f"{gk:.3f} kN/m")
    c3.metric("Uso lineal (qu,k)", f"{quk:.3f} kN/m")
    c4.metric("Uso puntual (Qp,k)", f"{Qpk_kN:.2f} kN")
    
    st.markdown(f"""
    <div class="small-gray">
    <b>Desglose gk:</b> (Gk · s) + Peso Viga <br>
    <i>Peso Viga = Área ({b_mm/1000}m x {h_mm/1000}m) × Densidad Media {mat} ({props_mat['rho_mean']} kg/m³) = {peso_viga:.3f} kN/m</i>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # --- TABLA ESTILO PDF ---
    st.markdown("### Tabla Resumen de Esfuerzos Máximos")
    tabla_html = "<table class='tabla-combis'><tr><th>Combinaciones de carga</th><th>M<sub>y,d</sub> [kN.m]</th><th>V<sub>z,d</sub> [kN]</th><th>Duración</th></tr>"
    for c in combos_elu:
        tabla_html += f"<tr><td class='bold-col'>{c['id']} &nbsp;&nbsp;<span style='font-weight:normal; color:#475569;'>{c['nombre']}</span></td><td class='val-col'>{c['M']:.2f}</td><td class='val-col'>{c['V']:.2f}</td><td>{c['duracion']}</td></tr>"
    tabla_html += "</table>"
    st.markdown(tabla_html, unsafe_allow_html=True)

    # --- ENVOLVENTES ---
    st.subheader("Envolventes de Cálculo (Valores Críticos)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="envelope-card"><div class="envelope-title">🔥 ELU (Resistencia / Rotura)</div><div class="val-highlight">{elu_max_M['M']:.2f} <span style="font-size:1rem;font-weight:500;">kN·m</span></div><div class="val-sub">M<sub>d</sub> máximo • <span style="color:#2563eb;">{elu_max_M['id']}</span></div><div style="margin-top:12px;"></div><div class="val-highlight">{elu_max_V['V']:.2f} <span style="font-size:1rem;font-weight:500;">kN</span></div><div class="val-sub">V<sub>d</sub> máximo • <span style="color:#2563eb;">{elu_max_V['id']}</span></div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="envelope-card" style="background: linear-gradient(135deg, #f8fafc 0%, #f0fdf4 100%); border-color: #bbf7d0;"><div class="envelope-title" style="color: #166534; border-bottom-color: #dcfce7;">📏 ELS Instantáneo (Flecha)</div><div class="val-highlight">{els_inst_max_M['M']:.2f} <span style="font-size:1rem;font-weight:500;">kN·m</span></div><div class="val-sub">M<sub>inst</sub> máximo • <span style="color:#059669;">{els_inst_max_M['id']}</span></div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="envelope-card" style="background: linear-gradient(135deg, #fdf8f6 0%, #fef3c7 100%); border-color: #fde047;"><div class="envelope-title" style="color: #854d0e; border-bottom-color: #fef08a;">⏳ ELS Cuasi-permanente (Fuego)</div><div class="val-highlight">{combo_qp['q']:.3f} <span style="font-size:1rem;font-weight:500;">kN/m</span></div><div class="val-sub">Carga lineal base (q<sub>qp</sub>)</div><div style="margin-top:12px;"></div><div class="val-highlight">{combo_qp['P']:.2f} <span style="font-size:1rem;font-weight:500;">kN</span></div><div class="val-sub">Carga puntual base (P<sub>qp</sub>)</div></div>""", unsafe_allow_html=True)

    st.divider()

    # =========================================================================
    # EXPLORADOR DE COMBINACIONES
    # =========================================================================
    st.header("🔍 Explorador de Combinaciones")
    opciones_combos = {f"[{c['id']}] {c['nombre']}": c for c in combos}
    seleccion = st.selectbox("Elige combinación:", list(opciones_combos.keys()), label_visibility="collapsed")
    c_sel = opciones_combos[seleccion]

    es_max_M = (c_sel["id"] == elu_max_M["id"])
    es_max_V = (c_sel["id"] == elu_max_V["id"])
    if es_max_M or es_max_V:
        mensaje = []
        if es_max_M: mensaje.append("Momento (ELU)")
        if es_max_V: mensaje.append("Cortante (ELU)")
        st.markdown(f"<div class='badge-winner'>🏆 Gobernante para: {' y '.join(mensaje)}</div>", unsafe_allow_html=True)

    # Diccionarios de fórmulas
    simbolos_q = {
        "ELU1": "γ<sub>G</sub> · g<sub>k</sub>",
        "ELU2": "γ<sub>G</sub> · g<sub>k</sub> + γ<sub>Q</sub> · q<sub>u,k</sub>",
        "ELU3": "γ<sub>G</sub> · g<sub>k</sub>",
        "ELU4": "γ<sub>G</sub> · g<sub>k</sub>",
        "ELS-1": "g<sub>k</sub> + q<sub>u,k</sub>",
        "ELS-2": "g<sub>k</sub>",
        "ELS-QP": "g<sub>k</sub> + ψ<sub>2</sub> · q<sub>u,k</sub>"
    }
    simbolos_P = {
        "ELU3": "γ<sub>Q</sub> · Q<sub>p,k</sub>",
        "ELU4": "γ<sub>Q</sub> · Q<sub>p,k</sub>",
        "ELS-2": "Q<sub>p,k</sub>",
        "ELS-QP": "ψ<sub>2</sub> · Q<sub>p,k</sub>"
    }
    
    sym_q = simbolos_q.get(c_sel['id'], "Fórmula q")
    sym_P = simbolos_P.get(c_sel['id'], "Fórmula P")

    colA, colB = st.columns([1.1, 1.3])
    with colA:
        st.markdown("**1. Cargas de la combinación**")
        
        html_q = f"q = {sym_q}<br>q = {c_sel['form_q']}<br>q = {c_sel['num_q']} = <span class='math-res'>{c_sel['q']:.3f} kN/m</span>"
        
        if c_sel['P'] > 0:
            pos_P_str = f"<br><span style='font-size:0.85rem; color:#94a3b8; font-weight:normal;'>Aplicada en x = {c_sel.get('pos_P', L_m/2):.2f} m</span>"
            html_P = f"<hr style='border-color:#334155; margin:10px 0;'>P = {sym_P}<br>P = {c_sel['form_P']}<br>P = {c_sel['num_P']} = <span class='math-res'>{c_sel['P']:.2f} kN</span>{pos_P_str}"
        else:
            html_P = ""
            
        st.markdown(f"<div class='math-box'>{html_q}{html_P}</div>", unsafe_allow_html=True)
        
    with colB:
        st.markdown("**2. Esfuerzos resultantes (Desglose Lineal + Puntual)**")
        
        q_val = c_sel['q']
        P_val = c_sel['P']
        pos = c_sel.get('pos_P', L_m/2)
        
        # Si la puntual está en el centro (o no hay puntual)
        if abs(pos - L_m/2) < 1e-5:
            Mq = q_val * L_m**2 / 8
            Mp = P_val * L_m / 4
            Vq = q_val * L_m / 2
            Vp = P_val / 2
            
            html_esfuerzos = f"""
            <div class='math-box' style='background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1;'>
                M<sub>max</sub> = M<sub>q</sub> + M<sub>P</sub> = (q·L²/8) + (P·L/4)<br>
                M<sub>max</sub> = ({q_val:.3f} · {L_m:.2f}² / 8) + ({P_val:.2f} · {L_m:.2f} / 4)<br>
                M<sub>max</sub> = {Mq:.2f} + {Mp:.2f} = <span style='color:#2563eb; font-weight:bold;'>{c_sel['M']:.2f} kN·m</span>
                <hr style='border-color:#e2e8f0; margin:10px 0;'>
                V<sub>max</sub> = V<sub>q</sub> + V<sub>P</sub> = (q·L/2) + (P/2)<br>
                V<sub>max</sub> = ({q_val:.3f} · {L_m:.2f} / 2) + ({P_val:.2f} / 2)<br>
                V<sub>max</sub> = {Vq:.2f} + {Vp:.2f} = <span style='color:#2563eb; font-weight:bold;'>{c_sel['V']:.2f} kN</span>
            </div>
            """
        else:
            # Si es la CC2.2 (carga al apoyo)
            Vq = q_val * L_m / 2
            Vp = P_val * pos / L_m
            
            html_esfuerzos = f"""
            <div class='math-box' style='background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1;'>
                V<sub>max</sub> = V<sub>q</sub> + V<sub>P</sub> = (q·L/2) + P·(x/L)<br>
                V<sub>max</sub> = ({q_val:.3f} · {L_m:.2f} / 2) + ({P_val:.2f} · {pos:.2f} / {L_m:.2f})<br>
                V<sub>max</sub> = {Vq:.2f} + {Vp:.2f} = <span style='color:#2563eb; font-weight:bold;'>{c_sel['V']:.2f} kN</span>
                <hr style='border-color:#e2e8f0; margin:10px 0;'>
                M<sub>max</sub> = M<sub>q</sub> + M<sub>P</sub> (Evaluado en x={pos:.2f})<br>
                M<sub>max</sub> = <span style='color:#2563eb; font-weight:bold;'>{c_sel['M']:.2f} kN·m</span>
            </div>
            """
            
        html_esfuerzos = html_esfuerzos.replace('\n', '')
        st.markdown(html_esfuerzos, unsafe_allow_html=True)

    st.markdown("**3. Justificación Normativa:**")
    st.markdown(f"<div class='expl-box'>{c_sel['explicacion']}</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top: 15px; margin-bottom: 20px;">
        <div style="background-color: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 12px 16px; border-radius: 4px; margin-bottom: 12px;">
            <span style="font-size: 1.05em; color: #0369a1; font-weight: bold;">💡 ¿Qué son esos coeficientes (ej. γ<sub>G</sub> = 1.35 o γ<sub>Q</sub> = 1.50)?</span><br>
            <div style="color: #0c4a6e; font-size: 0.95em; margin-top: 6px; line-height: 1.5;">
                Son los <b>coeficientes de seguridad (mayoración)</b>. El Eurocódigo no te deja usar los pesos "reales" sin más, te obliga a multiplicarlos para curarnos en salud por si los materiales pesan más de lo previsto o si hay errores de obra.
            </div>
        </div>
        <div style="background-color: #fdf4ff; border-left: 4px solid #d946ef; padding: 12px 16px; border-radius: 4px;">
            <span style="font-size: 1.05em; color: #86198f; font-weight: bold;">⚖️ ¿Por qué la carga puntual (P) se calcula por separado de la repartida (q)?</span><br>
            <div style="color: #701a75; font-size: 0.95em; margin-top: 6px; line-height: 1.5;">
                Porque tienen naturalezas distintas: una está repartida en toda la viga (<b>kN/m</b>) y la otra concentra su fuerza en un solo punto (<b>kN</b>). Físicamente <b>no se pueden sumar de forma directa</b>. Lo que hacemos es aplicar el <i>Principio de Superposición</i>: calculamos el esfuerzo que genera la carga repartida por su lado, el esfuerzo que genera la puntual por el suyo, y finalmente los sumamos.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.header("Tablas Resumen y Desarrollo Numérico")
    tab1, tab2 = st.tabs(["📊 Tablas de ELS", "🧮 Fórmulas y el misterio del k_mod"])
    
    with tab1:
        def mostrar_df(combos_list):
            df = pd.DataFrame(combos_list)
            df_show = df[["id", "nombre", "q", "P", "M", "V"]].copy()
            df_show.columns = ["ID", "Combinación", "q [kN/m]", "P [kN]", "Momento [kN·m]", "Cortante [kN]"]
            for col in ["q [kN/m]", "P [kN]", "Momento [kN·m]", "Cortante [kN]"]:
                df_show[col] = df_show[col].apply(lambda x: f"{x:.3f}")
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        st.subheader("ELS (Estado Límite de Servicio y Fuego)")
        mostrar_df(combos_els_inst + [combo_qp])
        
    with tab2:
        st.write("**1. Conversión de cargas superficiales a lineales**")
        st.latex(rf"g_{{k,total}} = (G_k \cdot s) + Peso_{{viga}} = ({Gk_m2:.2f} \cdot {s_m:.2f}) + {peso_viga:.3f} = {gk:.3f}\ \mathrm{{kN/m}}")
        st.latex(rf"q_{{u,k}} = Q_{{u,k}} \cdot s = {Quk_m2:.2f} \cdot {s_m:.2f} = {quk:.3f}\ \mathrm{{kN/m}}")

        st.write("**2. Esfuerzos máximos en viga biapoyada**")
        st.latex(r"M_{max} = q\frac{L^2}{8} + P\frac{L}{4} \quad \text{(Puntual en el centro)}")
        st.latex(r"V_{max} = q\frac{L}{2} + P\frac{x}{L} \quad \text{(Puntual desplazada al apoyo)}")

        st.write("**3. Coeficientes Normativos (Seguridad y Alternancia)**")
        st.latex(rf"\gamma_G = {GAMMA_G:.2f} \quad \gamma_Q = {GAMMA_Q:.2f} \quad \psi_2 = {PSI2_VIV:.2f}")

        st.write("**4. La Regla del $k_{mod}$ (Clase de Duración de la Carga)**")
        st.info("El $k_{mod}$ no se usa para calcular los kilos o los esfuerzos, sino para calcular la **resistencia** de la madera en las siguientes pestañas. La norma dice: *'Se toma el kmod de la acción de menor duración de la combinación ganadora'*.")
        
        kmod_perm = obtener_k_mod(clase_servicio, "Permanente")
        kmod_med = obtener_k_mod(clase_servicio, "Media")
        
        st.write(f"- Si gana **ELU1** (Solo peso propio): Duración = Permanente $\\rightarrow k_{{mod}} = {kmod_perm}$")
        st.write(f"- Si gana **ELU2, ELU3 o ELU4** (Entra carga uso): Duración = Media $\\rightarrow k_{{mod}} = {kmod_med}$")
        st.markdown(f"**En tu caso actual, para Momento ha ganado {elu_max_M['id']}, por lo que el programa usará automáticamente $k_{{mod}} = {obtener_k_mod(clase_servicio, duracion_M)}$ en la pestaña de Flexión.**")


# -----------------------------------------------------------------------------
# PÁGINA 2: FLEXIÓN Y AXIL
# -----------------------------------------------------------------------------
elif page == "📐 2. Flexión y Axil":
    st.title("Cálculo de secciones de madera")
    mostrar_resumen_global()

    def render_tabla_propiedades(titulo, filas, height=430, color="#2563eb"):
        filas_html = ""
        for prop, valor in filas: filas_html += f"<tr><td class='prop' style='padding:10px 14px;border-bottom:1px solid #f1f5f9;color:#4b5563;'>{prop}</td><td class='val' style='padding:10px 14px;border-bottom:1px solid #f1f5f9;text-align:right;color:#111827;font-weight:600;'>{valor}</td></tr>"
        html = f"<html><head><meta charset='utf-8'><style>body{{margin:0;font-family:Arial;background:transparent;}}.card{{background:linear-gradient(180deg,#ffffff 0%,#f8fafc 100%);border:1px solid #e5e7eb;border-radius:18px;padding:18px;box-sizing:border-box;box-shadow:0 8px 24px rgba(15,23,42,0.06);}}.title{{font-size:20px;font-weight:700;margin-bottom:14px;color:#111827;padding-bottom:10px;border-bottom:3px solid {color};}}table{{width:100%;border-collapse:separate;border-spacing:0;font-size:14px;background:white;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;}}thead tr{{background:#f3f4f6;}}th{{text-align:left;padding:12px 14px;font-weight:700;color:#374151;border-bottom:1px solid #e5e7eb;}}th:last-child{{text-align:right;}}tbody tr:nth-child(even){{background:#fafafa;}}</style></head><body><div class='card'><div class='title'>{titulo}</div><table><thead><tr><th>Propiedad</th><th>Valor</th></tr></thead><tbody>{filas_html}</tbody></table></div></body></html>"
        components.html(html, height=height, scrolling=False)

    tipo = st.radio("Selecciona el caso a comprobar:", ["Flexión", "Tracción paralela a la fibra", "Compresión paralela a la fibra"], horizontal=True)
    
    gamma_M = 1.25 if "GL" in mat else 1.30

    if tipo == "Flexión":
        k_mod = obtener_k_mod(clase_servicio, duracion_M)
        st.markdown(f"""
        <div class='link-box'>
        🔗 <b>Vinculado Automáticamente:</b><br> 
        - Usando Momento Máximo (<b>{elu_max_M['nombre']}</b>): $M_d = {elu_max_M['M']:.2f} \ kN\\cdot m$.<br>
        - Duración deducida: <b>{duracion_M}</b> $\\rightarrow k_{{mod}} = {k_mod}$.<br>
        - Material detectado: <b>{'Laminado' if 'GL' in mat else 'Macizo'}</b> $\\rightarrow \\gamma_M = {gamma_M}$.<br>
        - Efecto sistema: <b>k_sys = {k_sys:.2f}</b>.
        </div>
        """, unsafe_allow_html=True)
        M_kNm = elu_max_M['M']
        
        st.markdown("### Estabilidad al Vuelco Lateral [CTE DB SE-M 6.3.3]")
        colA, colB, colC = st.columns([1,1,1])
        with colA:
            arriostrado = st.checkbox("Viga arriostrada lateralmente (tablero clavado, sin riesgo)", value=False)
            beta_v = st.number_input("Factor de carga β_v", value=0.95, step=0.05, help="0.95 para carga distribuida, 1.00 para puntual al centro.")
            carga_superior = st.checkbox("Carga aplicada en borde comprimido (+2h a la longitud eficaz)", value=True)
        
        if arriostrado:
            k_crit = 1.00
            L_ef = 0
            lambda_rel_m = 0
        else:
            L_ef = L_m * 1000 * beta_v
            if carga_superior:
                L_ef += 2 * h_mm
            
            sigma_m_crit = (0.78 * (b_mm**2) * props_mat["E_0_05"]) / (h_mm * L_ef)
            lambda_rel_m = math.sqrt(props_mat["f_m_k"] / sigma_m_crit)
            
            if lambda_rel_m <= 0.75:
                k_crit = 1.00
            elif lambda_rel_m <= 1.4:
                k_crit = 1.56 - 0.75 * lambda_rel_m
            else:
                k_crit = 1.0 / (lambda_rel_m**2)
                
        with colB:
            st.markdown(f"<div style='padding:10px; background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;'><span style='color:#64748b;'>Longitud eficaz (L<sub>ef</sub>)</span><br><span style='font-size:1.3rem; font-weight:bold; color:#1e293b;'>{L_ef:.0f} mm</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='padding:10px; background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0; margin-top:10px;'><span style='color:#64748b;'>Esbeltez (λ<sub>rel,m</sub>)</span><br><span style='font-size:1.3rem; font-weight:bold; color:#1e293b;'>{lambda_rel_m:.2f}</span></div>", unsafe_allow_html=True)
        with colC:
            st.markdown(f"<div style='padding:22px 10px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; text-align:center; height:100%;'><span style='color:#1e3a8a; font-size:1rem; font-weight:bold;'>Coeficiente de pandeo lateral<br>k<sub>crit</sub></span><br><span style='font-size:2.5rem; font-weight:900; color:#2563eb;'>{k_crit:.2f}</span></div>", unsafe_allow_html=True)
        st.divider()

    else:
        st.markdown("<div class='link-box'>✏️ <b>Modo Manual:</b> Axil libre.</div>", unsafe_allow_html=True)
        F_kN = st.number_input("Esfuerzo axial Fd [kN]", min_value=0.0, value=114.0, step=1.0)
        duracion_manual = st.selectbox("Duración de carga", ["Permanente", "Larga", "Media", "Corta", "Instantánea"], index=2)
        k_mod = obtener_k_mod(clase_servicio, duracion_manual)
        k_crit = 1.00

    k_h = 1.0
    if tipo == "Flexión" or tipo == "Tracción paralela a la fibra":
        if "GL" in mat:
            k_h = min((600 / h_mm)**0.1, 1.1) if h_mm < 600 else 1.0
        else:
            k_h = min((150 / h_mm)**0.2, 1.3) if h_mm < 150 else 1.0

    if tipo == "Tracción paralela a la fibra": notacion = {"sigma": r"\sigma_{t,0,d}", "f_k": r"f_{t,0,k}", "f_d": r"f_{t,0,d}", "F": r"F_{t,0,d}", "titulo": "Tracción paralela a la fibra"}; f_k = props_mat["f_t_0_k"]
    elif tipo == "Compresión paralela a la fibra": notacion = {"sigma": r"\sigma_{c,0,d}", "f_k": r"f_{c,0,k}", "f_d": r"f_{c,0,d}", "F": r"F_{c,0,d}", "titulo": "Compresión paralela a la fibra"}; f_k = props_mat["f_c_0_k"]; k_h = 1.0 
    elif tipo == "Flexión": notacion = {"sigma": r"\sigma_{m,d}", "f_k": r"f_{m,k}", "f_d": r"f_{m,d}", "M": r"M_d", "W": r"W", "titulo": "Flexión"}; f_k = props_mat["f_m_k"]

    col1, col2 = st.columns(2)
    with col1:
        filas_mat = [("Material", mat), ("<i>f</i><sub>m,k</sub>", f"{props_mat['f_m_k']:.1f} N/mm²"), ("<i>k</i><sub>h</sub> (Efecto tamaño)", f"{k_h:.3f}"), ("Clase de servicio", clase_servicio), ("<i>k</i><sub>mod</sub>", f"{k_mod:.2f}"), ("<i>k</i><sub>sys</sub>", f"{k_sys:.2f}"), ("γ<sub>M</sub>", f"{gamma_M:.2f}")]
        render_tabla_propiedades("Material Automático", filas_mat, height=400, color="#2563eb")
    with col2:
        filas_sec = [("<i>b</i>", f"{b_mm:.1f} mm"), ("<i>h</i>", f"{h_mm:.1f} mm"), ("<i>W</i><sub>y</sub>", f"{props_geo['W_y']:.2f} mm³"), ("<i>A</i>", f"{props_geo['A']:.2f} mm²")]
        render_tabla_propiedades("Sección Automática", filas_sec, height=400, color="#7c3aed")

    def mostrar_tarjeta_resultado_local(ratio, sigma_d, f_d, simbolo="σ"):
        cumple = ratio <= 1.0
        if cumple: color, estado, clase = "#10b981", "✅ Cumple", "result-ok"
        else: color, estado, clase = "#ef4444", "❌ No cumple", "result-bad"
        texto = f"η = {ratio:.2f}"
        st.markdown(f"""<div class="result-box {clase}"><div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;"><div><div style="font-size:1.4rem; font-weight:800;">{estado}</div><div style="margin-top:0.35rem; font-size:1rem;">{texto}</div></div><div style="min-width:140px;text-align:center;background:white;border:2px solid {color};border-radius:16px;padding:0.8rem 1rem;box-shadow:0 4px 12px rgba(0,0,0,0.04);"><div style="font-size:0.9rem; color:#6b7280;">Aprovechamiento</div><div style="font-size:2rem; font-weight:800; color:{color};">η = {ratio:.2f}</div></div></div><div style="margin-top:0.8rem; font-size:0.95rem;"><b>{simbolo}<sub>d</sub></b> = {sigma_d:.2f} N/mm² &nbsp;&nbsp;|&nbsp;&nbsp;<b>f<sub>d</sub></b> = {f_d:.2f} N/mm²</div></div>""", unsafe_allow_html=True)

    if tipo == "Flexión":
        W_mm3 = props_geo["W_y"]
        M_Nmm = M_kNm * 1_000_000.0
        sigma_d = M_Nmm / W_mm3
        f_d = (k_mod * k_h * k_sys * k_crit * f_k) / gamma_M 
        ratio = sigma_d / f_d

        st.subheader("Desarrollo del cálculo final")
        st.latex(rf"{notacion['f_d']} = \frac{{k_{{mod}} \cdot k_{{crit}} \cdot k_h \cdot k_{{sys}} \cdot f_{{m,k}}}}{{\gamma_M}} = \frac{{{k_mod:.2f} \cdot {k_crit:.2f} \cdot {k_h:.3f} \cdot {k_sys:.2f} \cdot {f_k:.2f}}}{{{gamma_M:.2f}}} = {f_d:.2f}\ \mathrm{{N/mm}}^2")
        st.latex(rf"{notacion['sigma']} = \frac{{M_d}}{{W}} = \frac{{{M_kNm:.2f}\cdot 10^6}}{{{W_mm3:.2f}}} = {sigma_d:.2f}\ \mathrm{{N/mm}}^2")
        
        mostrar_tarjeta_resultado_local(ratio, sigma_d, f_d, simbolo="σ")

    else:
        A_mm2 = props_geo["A"]
        F_N = F_kN * 1000.0
        sigma_d = F_N / A_mm2
        f_d = (k_mod * k_h * k_sys * f_k) / gamma_M
        ratio = sigma_d / f_d
        
        st.subheader("Desarrollo del cálculo")
        st.latex(rf"{notacion['f_d']} = \frac{{k_{{mod}} \cdot k_h \cdot k_{{sys}} \cdot f_k}}{{\gamma_M}} = \frac{{{k_mod:.2f} \cdot {k_h:.3f} \cdot {k_sys:.2f} \cdot {f_k:.2f}}}{{{gamma_M:.2f}}} = {f_d:.2f}\ \mathrm{{N/mm}}^2")
        st.latex(rf"{notacion['sigma']} = \frac{{{F_kN:.2f} \cdot 1000}}{{{A_mm2:.2f}}} = {sigma_d:.2f}\ \mathrm{{N/mm}}^2")
        mostrar_tarjeta_resultado_local(ratio, sigma_d, f_d, simbolo="σ")


# -----------------------------------------------------------------------------
# PÁGINA 3: CORTANTE
# -----------------------------------------------------------------------------
elif page == "✂️ 3. Cortante ($k_{cr}$)":
    st.title("Módulo de Cortante (ELU)")
    mostrar_resumen_global()

    kmod = obtener_k_mod(clase_servicio, duracion_V)
    gamma_m = 1.25 if "GL" in mat else 1.30

    st.markdown(f"""
    <div class='link-box'>
    🔗 <b>Vinculado Automáticamente:</b><br> 
    - Cortante Máximo (<b>Vd={elu_max_V['V']:.2f} kN</b>) y Carga Lineal (<b>qd={elu_max_V['q']:.2f} kN/m</b>) de la combinación <b>{elu_max_V['nombre']}</b>.<br>
    - Duración deducida: <b>{duracion_V}</b> $\\rightarrow k_{{mod}} = {kmod}$.<br>
    - Material detectado: <b>{'Laminado' if 'GL' in mat else 'Macizo'}</b> $\\rightarrow \\gamma_M = {gamma_m}$.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📚 Guía del Maestro: Los secretos del Cortante en Madera", expanded=False):
        st.markdown("""
        El esfuerzo cortante (V) es la fuerza vertical cerca de los apoyos que intenta "cizallar" la viga. 
        En la madera, este esfuerzo no corta la viga verticalmente, sino que tiende a **rajarla horizontalmente a lo largo de las vetas**.
        
        1.  **El Truco de la Reducción ($V_{red}$):** Si pones un peso justo encima del pilar, ese peso baja por el pilar, no viaja por la viga. Por tanto, el Eurocódigo permite restar del cortante total toda la carga lineal que esté a una distancia menor o igual al canto de la viga ($h$). ¡Esto salva muchos cálculos!
        2.  **El Factor de Fisuración ($k_{cr}$):** La madera maciza y laminada puede tener pequeñas fendas (grietas) horizontales por el secado. La norma nos castiga obligándonos a considerar que la viga es un **33% más estrecha** de lo que realmente es ($k_{cr} = 0.67$).
        """)

    st.markdown("---")
    reducir_cortante = st.checkbox("Aplicar reducción de cortante a distancia 'h' del apoyo (EC5)", value=False, help="El Eurocódigo 5 permite descontar la carga cercana al apoyo. Muchos programas en España (CTE) lo omiten para ser más conservadores.")

    Vd = elu_max_V['V']
    qd = elu_max_V['q']
    fvk = props_mat["f_v_k"]

    h_m = h_mm / 1000.0
    
    if reducir_cortante:
        Vd_red = max(Vd - (qd * h_m), 0)
        texto_reduccion = f"• Reducción por cercanía al apoyo: **-{Vd - Vd_red:.2f} kN**"
    else:
        Vd_red = Vd
        texto_reduccion = "• Reducción por cercanía al apoyo: **No aplicada (Modo conservador)**"
        
    b_eff = b_mm * K_CR
    tau_d = (1.5 * Vd_red * 1000) / (b_eff * h_mm)
    fvd = (fvk * kmod * k_sys) / gamma_m
    ratio = tau_d / fvd

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='envelope-card'>", unsafe_allow_html=True)
        st.markdown("<div class='title-main'>1. Tensión Actuante (Lo que sufre la viga)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-highlight'>{tau_d:.2f}</span> <span class='val-unit'>N/mm²  (τ<sub>d</sub>)</span>", unsafe_allow_html=True)
        st.markdown("<br><b>Desglose del cálculo:</b>", unsafe_allow_html=True)
        st.write(f"• Cortante Inicial ($V_d$): **{Vd:.2f} kN**")
        st.write(texto_reduccion)
        st.write(f"• Cortante de Diseño ($V_{{d,red}}$): **{Vd_red:.2f} kN**")
        st.write(f"• Base Efectiva ($b_{{eff}} = b \cdot 0.67$): **{b_eff:.1f} mm**")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='envelope-card'>", unsafe_allow_html=True)
        st.markdown("<div class='title-main'>2. Tensión Resistente (Lo que aguanta el material)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-highlight'>{fvd:.2f}</span> <span class='val-unit'>N/mm²  (f<sub>v,d</sub>)</span>", unsafe_allow_html=True)
        st.markdown("<br><b>Desglose del cálculo:</b>", unsafe_allow_html=True)
        st.write(f"• Resistencia Característica ($f_{{v,k}}$): **{fvk:.2f} N/mm²**")
        st.write(f"• Factor de modificación ($k_{{mod}}$): **{kmod:.2f}**")
        st.write(f"• Factor de sistema ($k_{{sys}}$): **{k_sys:.2f}**")
        st.write(f"• Coeficiente de material ($\gamma_M$): **{gamma_m:.2f}**")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    colA, colB = st.columns([1, 2])
    with colA:
        aprovechamiento = ratio * 100
        if ratio <= 1.0: st.markdown(f"<div style='text-align: center; margin-top: 20px;'><span class='badge-ok' style='font-size:1.1rem; padding:8px 16px;'>✅ CUMPLE (Aprovechamiento: {aprovechamiento:.1f}%)</span></div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='text-align: center; margin-top: 20px;'><span class='badge-bad' style='font-size:1.1rem; padding:8px 16px;'>❌ NO CUMPLE (Aprovechamiento: {aprovechamiento:.1f}%)</span></div>", unsafe_allow_html=True)
    with colB:
        st.markdown(f"<div class='math-box' style='text-align: center;'>τ<sub>d</sub> ≤ f<sub>v,d</sub><br><br>{tau_d:.2f} N/mm²  ≤  {fvd:.2f} N/mm²</div>", unsafe_allow_html=True)

    st.markdown("### 🧮 Cómo se calculó paso a paso")
    with st.expander("Ver fórmulas completas"):
        st.write("**1. Reducción del Cortante en el apoyo:**")
        if reducir_cortante:
            st.latex(rf"V_{{d,red}} = V_d - q_d \cdot h = {Vd:.2f} - ({qd:.2f} \cdot {h_mm/1000:.2f}) = {Vd_red:.2f}\ \mathrm{{kN}}")
        else:
            st.latex(rf"V_{{d,red}} = V_d = {Vd:.2f}\ \mathrm{{kN}} \quad \text{{(Reducción no aplicada)}}")
            
        st.write("**2. Tensión tangencial máxima (Perfil rectangular):**")
        st.latex(rf"\tau_d = \frac{{3 \cdot V_{{d,red}}}}{{2 \cdot b_{{eff}} \cdot h}} = \frac{{3 \cdot {Vd_red:.2f} \cdot 10^3}}{{2 \cdot ({b_mm} \cdot {K_CR}) \cdot {h_mm}}} = {tau_d:.2f}\ \mathrm{{N/mm^2}}")
        st.write("**3. Resistencia de cálculo:**")
        st.latex(rf"f_{{v,d}} = \frac{{k_{{mod}} \cdot k_{{sys}} \cdot f_{{v,k}}}}{{\gamma_M}} = \frac{{{kmod:.2f} \cdot {k_sys:.2f} \cdot {fvk:.2f}}}{{{gamma_m:.2f}}} = {fvd:.2f}\ \mathrm{{N/mm^2}}")

# -----------------------------------------------------------------------------
# PÁGINA 4: FLECHA Y KDEF
# -----------------------------------------------------------------------------
elif page == "📏 4. Flecha y $k_{def}$":
    st.title("Módulo de Flecha (Deformaciones y kdef)")
    mostrar_resumen_global()

    kdef = KDEF_DICT[clase_servicio]
    E_mean = props_mat["E_0_mean"]

    st.markdown(f"<div class='link-box'>🔗 <b>Vinculado Automáticamente:</b> Usando Módulo de Elasticidad (<b>{E_mean} N/mm²</b>), Cargas de la Pestaña 1 y <b>kdef={kdef}</b> por estar en Clase de Servicio {clase_servicio}.</div>", unsafe_allow_html=True)

    st.markdown("### Selecciona tus límites normativos")
    colA, colB, colC = st.columns(3)
    limite_inst = colA.selectbox("Límite Instantánea", [300, 400, 500], format_func=lambda x: f"L/{x}")
    limite_activa = colB.selectbox("Límite Activa (Tabiques)", [400, 500], format_func=lambda x: f"L/{x}")
    limite_fin = colC.selectbox("Límite Final Neto", [250, 300, 400], format_func=lambda x: f"L/{x}")

    def flecha_uniforme(q_kNm, L_m, E_mean, I_mm4): return (5.0 / 384.0) * ((q_kNm * (L_m * 1000)**4) / (E_mean * I_mm4))
    def flecha_puntual(P_kN, L_m, E_mean, I_mm4): return (1.0 / 48.0) * (((P_kN * 1000) * (L_m * 1000)**3) / (E_mean * I_mm4))

    I_y = props_geo["I_y"]

    w_inst_G = flecha_uniforme(gk, L_m, E_mean, I_y)
    
    w_inst_Q_uni = flecha_uniforme(quk, L_m, E_mean, I_y)
    w_inst_Q_pun = flecha_puntual(Qpk_kN, L_m, E_mean, I_y)
    w_inst_Q = max(w_inst_Q_uni, w_inst_Q_pun) 
    w_inst_total = w_inst_G + w_inst_Q

    w_creep_G = w_inst_G * kdef
    w_creep_Q = w_inst_Q * (PSI2_VIV * kdef)
    w_creep_total = w_creep_G + w_creep_Q

    w_fin_G = w_inst_G + w_creep_G
    w_fin_Q = w_inst_Q + w_creep_Q
    w_fin_total = w_inst_total + w_creep_total

    w_activa = w_fin_total - w_inst_G

    w_lim_inst = (L_m * 1000) / limite_inst
    w_lim_activa = (L_m * 1000) / limite_activa
    w_lim_fin = (L_m * 1000) / limite_fin

    st.info("💡 **Nota:** Para la flecha instantánea se toma el caso más desfavorable entre la sobrecarga uniforme y la carga puntual local, consideradas acciones alternativas según el EC1.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='envelope-card'>", unsafe_allow_html=True)
        st.markdown("<div class='title-day1'>📅 Día 1: Instantánea (w_inst)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{w_inst_total:.1f}</span> <span class='val-unit'>mm</span>", unsafe_allow_html=True)
        st.markdown("<br>**Desglose:**", unsafe_allow_html=True)
        st.write(f"• Por peso (G): **{w_inst_G:.1f} mm**")
        st.write(f"• Por uso (max Q): **{w_inst_Q:.1f} mm**")
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        if (w_inst_total / w_lim_inst) <= 1.0: st.markdown(f"<span class='badge-ok'>✅ Cumple: ≤ {w_lim_inst:.1f} mm</span>", unsafe_allow_html=True)
        else: st.markdown(f"<span class='badge-bad'>❌ No cumple: > {w_lim_inst:.1f} mm</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='envelope-card' style='background: linear-gradient(135deg, #fefce8 0%, #fffbeb 100%); border-color: #fde047;'>", unsafe_allow_html=True)
        st.markdown("<div class='title-activa'>🧱 Flecha Activa (w_activa)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{w_activa:.1f}</span> <span class='val-unit'>mm</span>", unsafe_allow_html=True)
        st.markdown("<br>**Fórmula:**", unsafe_allow_html=True)
        st.write(f"• Flecha Final: **{w_fin_total:.1f} mm**")
        st.write(f"• Restamos Inst,G: **-{w_inst_G:.1f} mm**")
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        if (w_activa / w_lim_activa) <= 1.0: st.markdown(f"<span class='badge-ok' style='color:#854d0e; border-color:#fde047; background:#fef08a;'>✅ Cumple: ≤ {w_lim_activa:.1f} mm</span>", unsafe_allow_html=True)
        else: st.markdown(f"<span class='badge-bad'>❌ No cumple: > {w_lim_activa:.1f} mm</span>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.8rem; color:#9ca3af; margin-top:5px;'>*Estimación simplificada asumiendo tabiques ejecutados tras deformación por peso propio.</p></div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='envelope-card' style='background: linear-gradient(135deg, #fef2f2 0%, #fff1f2 100%); border-color: #fecaca;'>", unsafe_allow_html=True)
        st.markdown("<div class='title-day10k'>⏳ 30 Años: Flecha Final (w_fin)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{w_fin_total:.1f}</span> <span class='val-unit'>mm</span>", unsafe_allow_html=True)
        st.markdown("<br>**Desglose:**", unsafe_allow_html=True)
        st.write(f"• Día 1: **{w_inst_total:.1f} mm**")
        st.write(f"• Fluencia (Creep): **+{w_creep_total:.1f} mm**")
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        if (w_fin_total / w_lim_fin) <= 1.0: st.markdown(f"<span class='badge-ok' style='color:#991b1b; border-color:#fca5a5; background:#fecaca;'>✅ Cumple: ≤ {w_lim_fin:.1f} mm</span>", unsafe_allow_html=True)
        else: st.markdown(f"<span class='badge-bad'>❌ No cumple: > {w_lim_fin:.1f} mm</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.header("🔍 ¿Cómo ha afectado exactamente el $k_{def}$?")
    st.markdown(f"""
    <div class='expl-box'>
    Has elegido <b>Clase {clase_servicio}</b>, por lo que el coeficiente de deformación en el tiempo es <b>kdef = {kdef:.2f}</b>.<br>
    Fíjate en las pizarras de abajo para entender a qué le afecta este {kdef:.2f} y a qué no.
    </div>
    """, unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("### 1. El Peso Propio (G)")
        st.write("El peso de la structure está **siempre al 100%**. La madera fluye bajo todo su peso.")
        st.markdown(f"""<div class='math-box'>w_fin,G = w_inst,G · (1 + kdef)<br>w_fin,G = {w_inst_G:.2f} · (1 + {kdef:.2f})<br>w_fin,G = {w_fin_G:.2f} mm</div>""", unsafe_allow_html=True)
        st.caption(f"El peso propio ha generado {w_creep_G:.1f} mm de flecha 'extra' con los años.")
    with colB:
        st.markdown("### 2. La Sobrecarga de Uso (Q)")
        st.write("Solo consideramos la parte que vive ahí de forma permanente, es decir el $\psi_2$ (30%).")
        st.markdown(f"""<div class='math-box'>w_fin,Q = w_inst,Q · (1 + ψ2 · kdef)<br>w_fin,Q = {w_inst_Q:.2f} · (1 + {PSI2_VIV:.2f} · {kdef:.2f})<br>w_fin,Q = {w_fin_Q:.2f} mm</div>""", unsafe_allow_html=True)
        st.caption(f"La sobrecarga ha generado solo {w_creep_Q:.1f} mm de flecha 'extra' con los años.")

    st.divider()
    
    st.header("🧠 Traducción al mundo real (Para no olvidar los conceptos)")
    st.markdown("""
    <div style="display: flex; gap: 15px; flex-wrap: wrap;">
        <div class="story-box" style="flex: 1; background: #f0fdf4; border: 1px solid #bbf7d0;">
            <p class="story-title" style="color: #166534;">📅 1. Instantánea (La Fiesta)</p>
            Imagina que terminas de construir el forjado. Ese mismo día metes todos los muebles e invitas a 20 personas a una fiesta de inauguración. El suelo cede unos milímetros de golpe bajo el peso de la gente y la madera. Eso es la <b>Flecha Instantánea</b>. Al día siguiente, cuando la gente se va, el suelo recupera parte de esa curva.
        </div>
        <div class="story-box" style="flex: 1; background: #fffbeb; border: 1px solid #fde047;">
            <p class="story-title" style="color: #854d0e;">🧱 2. Activa (El Tabique de Cristal)</p>
            Haces el forjado (baja un poco). <b>Después</b>, construyes encima un tabique rígido o una cristalera. Al cristal le da igual lo que bajó el suelo ayer; solo le importa lo que baje <b>a partir de hoy</b>. Si mañana metes la bañera, los muebles y pasan 10 años, el suelo bajará más. Esa flecha "extra" que sufre el tabique es la <b>Flecha Activa</b>. Si es mucha, el cristal estalla.
        </div>
        <div class="story-box" style="flex: 1; background: #fef2f2; border: 1px solid #fecaca;">
            <p class="story-title" style="color: #991b1b;">⏳ 3. Final (La Jubilación a 30 años)</p>
            Pasan 30 años. La estructura de madera ha estado soportando su propio peso y el de armarios pesados día tras día. La madera es viscoelástica: "se cansa" y fluye. Sin añadir ni un solo kilo nuevo, la viga se ha ido doblando lentamente (esto lo mide el <b>kdef</b>). Lo que ha bajado en total tras décadas de servicio es la <b>Flecha Final</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PÁGINA 5: VIBRACIONES
# -----------------------------------------------------------------------------
elif page == "📳 5. Vibraciones":
    st.title("📳 5. Servicio: Confort y Vibraciones (EC5)")
    mostrar_resumen_global()

    st.info("⚠️ **Nota normativa:** Este módulo evalúa el confort mediante el método simplificado de frecuencia propia ($f_1 > 8Hz$) y rigidez bajo carga estática ($w_{1kN}$), habitual en diseño residencial. El EC5 completo incluye un tercer criterio de respuesta a impulso ($v$) para un análisis dinámico exhaustivo.")

    with st.expander("📚 Guía del Maestro: ¿Por qué vibra la madera?", expanded=False):
        st.markdown("""
        Un forjado de madera puede ser súper resistente y no romperse jamás, pero tener un gran problema: **El Efecto Trampolín**. 
        Como la madera es muy ligera (poca masa) en relación a su resistencia, es fácil que vibre como la cuerda de una guitarra cuando alguien camina sobre ella.
        
        *   **La Masa que Vibra ($m$):** Para ver cómo vibra el forjado, no usamos los coeficientes de seguridad. Usamos la masa real. Cogemos todo el peso muerto (Estructura + Pavimento) y le sumamos solo un **10% o 20%** de la sobrecarga de uso (los muebles, que por su peso "ayudan" a amortiguar la vibración).
        *   **Frecuencia Fundamental ($f_1$):** Es la "velocidad" a la que rebota el suelo. Si es **menor a 8 Hz** (8 rebotes por segundo), coincide con la frecuencia del paso humano y el sistema nervioso lo percibe como inestable. ¡Hay que estar por encima de 8 Hz!
        *   **Criterio de Rigidez ($w_{1kN}$):** Simulamos una persona pesada (100 kg = 1 kN) dando un paso fuerte en el centro del forjado. El suelo no debería hundirse más de 1.0 - 2.0 mm (dependiendo del país).
        """)

    st.sidebar.header("Parámetros de Vibración")
    psi_masa = st.sidebar.slider("Participación del uso en masa (ψ)", 0.0, 0.30, 0.10, 0.05, help="Porcentaje de la sobrecarga de uso que se considera masa fija (muebles). Suele ser 10% o 20%.")
    k_rep = st.sidebar.slider("Coef. reparto transversal", 0.20, 1.00, 0.50, 0.05, help="0.50 significa que la viga pisada se lleva el 50% de la carga puntual, el resto lo absorben las vecinas gracias al tablero.")

    st.sidebar.header("Límites de Confort")
    limite_f1 = st.sidebar.number_input("Frecuencia mínima f1 [Hz]", value=8.0, step=0.5)
    limite_w1kN = st.sidebar.number_input("Hundimiento máximo w_1kN [mm]", value=1.5, step=0.1)

    E_mean = props_mat["E_0_mean"]
    I_y = props_geo["I_y"]
    
    E_N_m2 = E_mean * 1e6
    I_m4 = I_y * 1e-12
    EI_L = (E_N_m2 * I_m4) / s_m

    Gk_viga_m2 = peso_viga / s_m 
    masa_G = (Gk_m2 + Gk_viga_m2) * (1000 / 9.81)
    masa_Q = (Quk_m2 * psi_masa) * (1000 / 9.81)
    m_total = masa_G + masa_Q

    f1 = (math.pi / (2 * L_m**2)) * math.sqrt(EI_L / m_total)

    F_N = 1000.0 * k_rep
    L_mm = L_m * 1000.0
    w_1kN = (F_N * L_mm**3) / (48.0 * E_mean * I_y)

    st.subheader("Resultados de Confort (Estado Límite de Servicio)")
    col1, col2 = st.columns(2)

    with col1:
        color_card = "#f0fdf4" if f1 >= limite_f1 else "#fef2f2"
        border_card = "#bbf7d0" if f1 >= limite_f1 else "#fecaca"
        st.markdown(f"<div class='envelope-card' style='background: {color_card}; border-color: {border_card};'>", unsafe_allow_html=True)
        st.markdown("<div class='envelope-title' style='color:#1e293b'>🎵 Frecuencia Propia ($f_1$)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{f1:.1f}</span> <span class='val-unit'>Hz (rebotes / seg)</span>", unsafe_allow_html=True)
        st.markdown("<br>**Análisis:**", unsafe_allow_html=True)
        st.write(f"• Masa actuante: **{m_total:.0f} kg/m²**")
        st.write(f"• Rigidez del forjado: **{EI_L/1e6:.2f} MN·m²/m**")
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        if f1 >= limite_f1: st.markdown(f"<span class='badge-ok'>✅ FORJADO RÁPIDO (≥ {limite_f1} Hz)</span>", unsafe_allow_html=True)
        else: st.markdown(f"<span class='badge-bad'>❌ FORJADO LENTO (< {limite_f1} Hz). ¡Peligro!</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        color_card2 = "#f0fdf4" if w_1kN <= limite_w1kN else "#fef2f2"
        border_card2 = "#bbf7d0" if w_1kN <= limite_w1kN else "#fecaca"
        st.markdown(f"<div class='envelope-card' style='background: {color_card2}; border-color: {border_card2};'>", unsafe_allow_html=True)
        st.markdown("<div class='envelope-title' style='color:#1e293b'>🦶 Rigidez al paso ($w_{1kN}$)</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-big'>{w_1kN:.2f}</span> <span class='val-unit'>mm de hundimiento</span>", unsafe_allow_html=True)
        st.markdown("<br>**Análisis:**", unsafe_allow_html=True)
        st.write(f"• Carga aplicada a la viga: **1.0 kN $\\times$ {k_rep:.2f} (Reparto)**")
        st.write(f"• Luz de la viga: **{L_m:.2f} m**")
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        if w_1kN <= limite_w1kN: st.markdown(f"<span class='badge-ok'>✅ SUELO RÍGIDO (≤ {limite_w1kN} mm)</span>", unsafe_allow_html=True)
        else: st.markdown(f"<span class='badge-bad'>❌ SUELO BLANDO (> {limite_w1kN} mm). Efecto trampolín.</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.header("🧮 Disección Matemática")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("### 1. Cálculo de Masa ($m$)")
        st.markdown(f"""
        <div class='math-box'>
        m_G = (G_k + Peso_{{viga}}) · (1000 / 9.81) <br>
        m_G = ({Gk_m2:.2f} + {Gk_viga_m2:.2f}) · 101.9 = {masa_G:.1f} kg/m²
        <hr style="border-color:#334155; margin:10px 0;">
        m_Q = (Q_k · ψ_{{masa}}) · (1000 / 9.81) <br>
        m_Q = ({Quk_m2:.2f} · {psi_masa:.2f}) · 101.9 = {masa_Q:.1f} kg/m²
        <hr style="border-color:#334155; margin:10px 0;">
        m_{{total}} = <span class='math-res'>{m_total:.1f} kg/m²</span>
        </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown("### 2. Frecuencia Propia ($f_1$)")
        st.markdown(f"""
        <div class='math-box'>
        (EI)_L = E_{{mean}} · I_y / s <br>
        (EI)_L = {EI_L/1e6:.2f} · 10⁶ N·m²/m
        <hr style="border-color:#334155; margin:10px 0;">
        f_1 = (π / 2·L²) · √((EI)_L / m) <br>
        f_1 = (3.1416 / {2 * L_m**2:.2f}) · √({EI_L:.0f} / {m_total:.1f}) <br>
        f_1 = <span class='math-res'>{f1:.2f} Hz</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 3. Criterio de Rigidez ($w_{1kN}$)")
    st.latex(rf"w_{{1kN}} = \frac{{(1000\ N \cdot k_{{rep}}) \cdot L^3}}{{48 \cdot E_{{mean}} \cdot I_y}} = \frac{{(1000 \cdot {k_rep:.2f}) \cdot {L_mm:.0f}^3}}{{48 \cdot {E_mean} \cdot {I_y:.0f}}} = {w_1kN:.2f}\ \mathrm{{mm}}")

    st.divider()
    st.header("🧠 Traducción al mundo real")
    st.markdown("""
    <div style="display: flex; gap: 15px; flex-wrap: wrap;">
        <div class="story-box" style="flex: 1; background: #faf5ff; border: 1px solid #e9d5ff;">
            <p class="story-title" style="color: #7e22ce;">🎵 ¿Por qué 8 Hz?</p>
            Al caminar generas "armónicos" de hasta 6 o 7 Hz. Si el forjado vibra a 7 Hz, tus pasos entran en <b>Resonancia</b> con el suelo, y la vibración se amplifica salvajemente. Exigimos que el forjado sea "más rápido" que tus pasos (> 8 Hz).
        </div>
        <div class="story-box" style="flex: 1; background: #fffbeb; border: 1px solid #fde047;">
            <p class="story-title" style="color: #854d0e;">🐘 El Pisotón (1 kN)</p>
            Simulamos que una persona de 100 kg da un paso seco. Si la viga baja más de 1.5 mm de golpe, la sensación es de muchísima inseguridad, aunque sepa que la viga aguanta toneladas.
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PÁGINA 6: FUEGO (Sección Eficaz Reducida)
# -----------------------------------------------------------------------------
elif page == "🔥 6. Fuego (EC5)":
    st.title("🔥 6. Fuego (Sección Eficaz Reducida)")
    mostrar_resumen_global()

    with st.expander("📚 Guía del Maestro: La madera y el fuego", expanded=False):
        st.markdown("""
        A diferencia del acero (que colapsa por temperatura), la madera se quema lentamente creando una capa exterior de carbón que aísla el núcleo. 
        El **Método de la Sección Eficaz Reducida** consiste en:
        1. Calcular cuánto se ha quemado la viga en $X$ minutos (Velocidad de carbonización $\\beta_n$).
        2. Añadir $7\ mm$ extras ($d_0$) porque la madera justo debajo del carbón está muy caliente y pierde fuerza.
        3. Quitarle esa capa a la viga original y comprobar si el "palillo" que queda en el medio es capaz de aguantar el forjado.
        """)

    st.sidebar.header("Parámetros de Incendio")
    t_fuego = st.sidebar.selectbox("Tiempo de resistencia t (minutos)", [15, 30, 45, 60, 90, 120], index=1)
    
    beta_n = 0.70 if "GL" in mat else 0.80
    k_fi = 1.15 if "GL" in mat else 1.25
    k_mod_fi = 1.00
    gamma_m_fi = 1.00
    
    d_char_n = beta_n * t_fuego
    k_0 = min(t_fuego / 20.0, 1.0)
    d_0 = 7.0
    d_ef = d_char_n + k_0 * d_0

    num_caras = st.sidebar.selectbox("Caras expuestas al fuego", [1, 2, 3, 4], index=2)
    b_fi, h_fi = b_mm, h_mm
    detalle_caras = ""

    if num_caras == 1:
        tipo_1cara = st.sidebar.radio("¿Qué cara se quema?", ["Un Lateral (reduce base)", "Inferior (reduce canto)"])
        if "Lateral" in tipo_1cara:
            b_fi = b_mm - d_ef
            detalle_caras = "1 Lateral"
        else:
            h_fi = h_mm - d_ef
            detalle_caras = "1 Inferior"
            
    elif num_caras == 2:
        tipo_2caras = st.sidebar.radio("¿Qué caras se queman?", ["Dos Laterales (reduce 2x base)", "1 Lateral y 1 Inferior"])
        if "Dos Laterales" in tipo_2caras:
            b_fi = b_mm - 2 * d_ef
            detalle_caras = "2 Laterales"
        else:
            b_fi = b_mm - d_ef
            h_fi = h_mm - d_ef
            detalle_caras = "1 Lat + 1 Inf"
            
    elif num_caras == 3:
        st.sidebar.caption("🔥 Expuestas: 2 Laterales + 1 Inferior")
        b_fi = b_mm - 2 * d_ef
        h_fi = h_mm - d_ef
        detalle_caras = "2 Lat + 1 Inf"
        
    elif num_caras == 4:
        st.sidebar.caption("🔥 Expuestas: Todas las caras")
        b_fi = b_mm - 2 * d_ef
        h_fi = h_mm - 2 * d_ef
        detalle_caras = "Todas"

    if b_fi <= 0 or h_fi <= 0:
        st.error("🔥 **LA VIGA SE HA CONSUMIDO POR COMPLETO.** La sección restante es nula o negativa. Aumenta la sección inicial o disminuye el tiempo de fuego.")
    else:
        Area_fi = b_fi * h_fi
        Iy_fi = (b_fi * h_fi**3) / 12.0
        Wy_fi = Iy_fi / (h_fi / 2.0)
        Iz_fi = (h_fi * b_fi**3) / 12.0
        Wz_fi = Iz_fi / (b_fi / 2.0)

        if "GL" in mat:
            k_hy = min((600 / h_fi)**0.1, 1.1) if h_fi < 600 else 1.0
            k_hz = min((600 / b_fi)**0.1, 1.1) if b_fi < 600 else 1.0
        else:
            k_hy = min((150 / h_fi)**0.2, 1.3) if h_fi < 150 else 1.0
            k_hz = min((150 / b_fi)**0.2, 1.3) if b_fi < 150 else 1.0

        M_fi = combo_qp['M']
        
        sigma_m_fi_d = (M_fi * 1e6) / Wy_fi
        f_m_fi_d = (k_mod_fi * k_fi * k_hy * props_mat["f_m_k"]) / gamma_m_fi
        ratio_fuego = sigma_m_fi_d / f_m_fi_d

        st.markdown("<h3 style='color: #b91c1c; margin-bottom: 0;'>CARACTERÍSTICAS DE LA SECCIÓN A FUEGO</h3>", unsafe_allow_html=True)
        
        html_sec = f"""<table style="width:100%; text-align:center; border-collapse: collapse; margin-bottom: 20px; font-size: 0.95rem;">
<tr style="background-color: #f8fafc; border-bottom: 2px solid #cbd5e1;">
<th style="padding: 10px;">b_ef (mm)</th><th style="padding: 10px;">h_ef (mm)</th>
<th style="padding: 10px;">Área (mm²)</th><th style="padding: 10px;">Iy (mm⁴)</th>
<th style="padding: 10px;">Wy (mm³)</th><th style="padding: 10px;">Iz (mm⁴)</th>
<th style="padding: 10px;">Wz (mm³)</th>
</tr>
<tr>
<td style="padding: 10px; color: #b91c1c; font-weight: bold; background-color: #fef2f2;">{b_fi:.0f}</td>
<td style="padding: 10px; color: #b91c1c; font-weight: bold; background-color: #fef2f2;">{h_fi:.0f}</td>
<td style="padding: 10px;">{Area_fi:,.2f}</td><td style="padding: 10px;">{Iy_fi:,.0f}</td>
<td style="padding: 10px;">{Wy_fi:,.2f}</td><td style="padding: 10px;">{Iz_fi:,.0f}</td>
<td style="padding: 10px;">{Wz_fi:,.2f}</td>
</tr>
</table>"""
        st.markdown(html_sec, unsafe_allow_html=True)

        html_params = f"""<div style="display:flex; gap: 20px; flex-wrap: wrap;">
<table style="flex: 2; min-width: 400px; text-align:center; border-collapse: collapse; font-size: 0.9rem;">
<caption style="text-align:left; font-style:italic; margin-bottom:5px;">CTE - Método de la sección reducida</caption>
<tr style="background-color: #f8fafc; border-bottom: 2px solid #cbd5e1;">
<th style="padding: 8px;">Resist. t (min)</th><th style="padding: 8px;">Caras</th>
<th style="padding: 8px;">d_ef (mm)</th><th style="padding: 8px;">d_char,n (mm)</th>
<th style="padding: 8px;">βn (mm/min)</th><th style="padding: 8px;">K0</th>
<th style="padding: 8px;">d0 (mm)</th>
</tr>
<tr>
<td style="padding: 8px; font-weight:bold; background-color:#fffbeb;">{t_fuego}</td>
<td style="padding: 8px; font-weight:bold; background-color:#fffbeb;">{num_caras} ({detalle_caras})</td>
<td style="padding: 8px;">{d_ef:.1f}</td><td style="padding: 8px;">{d_char_n:.1f}</td>
<td style="padding: 8px;">{beta_n:.2f}</td><td style="padding: 8px;">{k_0:.2f}</td>
<td style="padding: 8px;">{d_0:.1f}</td>
</tr>
</table>
<table style="flex: 1; min-width: 250px; text-align:center; border-collapse: collapse; font-size: 0.9rem;">
<caption style="text-align:left; font-style:italic; margin-bottom:5px; color:#b91c1c; font-weight:bold;">COEFICIENTES DE CÁLCULO</caption>
<tr style="background-color: #f8fafc; border-bottom: 2px solid #cbd5e1;">
<th style="padding: 8px;">K_hy</th><th style="padding: 8px;">K_fi</th>
<th style="padding: 8px;">K_mod,i</th><th style="padding: 8px;">γ_M</th>
</tr>
<tr>
<td style="padding: 8px;">{k_hy:.2f}</td><td style="padding: 8px;">{k_fi:.2f}</td>
<td style="padding: 8px;">{k_mod_fi:.2f}</td><td style="padding: 8px;">{gamma_m_fi:.2f}</td>
</tr>
</table>
</div>"""
        st.markdown(html_params, unsafe_allow_html=True)
        st.divider()

        col1, col2 = st.columns(2)
        
        with col1:
            color_card = "#f0fdf4" if ratio_fuego <= 1.0 else "#fef2f2"
            border_card = "#bbf7d0" if ratio_fuego <= 1.0 else "#fecaca"
            st.markdown(f"<div class='envelope-card' style='background: {color_card}; border-color: {border_card};'>", unsafe_allow_html=True)
            st.markdown("<div class='title-main'>⚖️ Comprobación a Flexión Fuego</div>", unsafe_allow_html=True)
            st.markdown(f"<span class='val-big'>{sigma_m_fi_d:.1f}</span> <span class='val-unit'>N/mm² (Tensión Actuante)</span>", unsafe_allow_html=True)
            st.markdown("<br>**Análisis de Resistencia:**", unsafe_allow_html=True)
            st.write(f"• Momento Accidental ($M_{{fi}}$): **{M_fi:.2f} kN·m**")
            st.write(f"• Resistencia fuego ($K_{{hy}} \cdot K_{{fi}} \cdot f_k$): **{f_m_fi_d:.2f} N/mm²**")
            st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
            if ratio_fuego <= 1.0:
                st.markdown(f"<span class='badge-ok'>✅ CUMPLE (Aprovechamiento: {ratio_fuego*100:.1f}%)</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='badge-bad'>❌ COLAPSO (Aprovechamiento: {ratio_fuego*100:.1f}%)</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("### 🧮 Disección Matemática")
            st.markdown(f"""
            <div class='math-box'>
            <b>1. Resistencia minorada en incendio:</b><br>
            f_{{m,fi,d}} = k_{{mod,i}} · k_{{fi}} · k_{{hy}} · f_{{m,k}} / γ_M<br>
            f_{{m,fi,d}} = {k_mod_fi:.2f} · {k_fi:.2f} · {k_hy:.2f} · {props_mat['f_m_k']:.2f} / {gamma_m_fi:.2f} = <span style='color:#10b981;'>{f_m_fi_d:.2f} N/mm²</span>
            <hr style="border-color:#334155; margin:10px 0;">
            <b>2. Tensión actuante (Base Cuasi-permanente):</b><br>
            σ_{{m,fi,d}} = M_{{fi}} / W_{{y,fi}}<br>
            σ_{{m,fi,d}} = ({M_fi:.2f} · 10⁶) / {Wy_fi:,.0f} = <span style='color:#ef4444;'>{sigma_m_fi_d:.2f} N/mm²</span>
            </div>
            """, unsafe_allow_html=True)
            st.caption("Nota: El programa deduce automáticamente cómo se resta la capa carbonizada ($d_{ef}$) a la base y al canto en función de las caras elegidas.")


# -----------------------------------------------------------------------------
# PÁGINA 7: DIAGRAMAS DE ESFUERZOS
# -----------------------------------------------------------------------------
elif page == "📊 7. Diagramas de Esfuerzos":
    st.title("📊 7. Diagramas de Esfuerzos (V y M)")
    mostrar_resumen_global()
    
    st.markdown("""
    <div class="blue-box">
    Visualización interactiva de esfuerzos a lo largo de la viga. Puedes pasar el ratón por encima de la gráfica para ver los valores exactos en cada milímetro.
    </div>
    """, unsafe_allow_html=True)

    opciones_combos = {f"[{c['id']}] {c['nombre']}": c for c in combos}
    seleccion = st.selectbox("Elige la combinación que deseas dibujar:", list(opciones_combos.keys()))
    c_sel = opciones_combos[seleccion]

    q_kNm = c_sel['q']
    P_kN = c_sel['P']
    M_max = c_sel['M']
    V_max = c_sel['V']
    pos_P = c_sel['pos_P']

    x_vals_plot = []
    v_vals_plot = []
    m_vals_plot = []
    
    pasos = 200
    Ra = q_kNm * L_m / 2.0 + P_kN * (L_m - pos_P) / L_m
    
    for i in range(pasos + 1):
        x = i * L_m / pasos
        
        if abs(x - pos_P) < 1e-5 and P_kN > 0:
            x_vals_plot.append(x)
            v_vals_plot.append(Ra - q_kNm * x)
            m_vals_plot.append(Ra * x - q_kNm * x**2 / 2)
            
            x_vals_plot.append(x)
            v_vals_plot.append(Ra - q_kNm * x - P_kN)
            m_vals_plot.append(Ra * x - q_kNm * x**2 / 2)
        else:
            x_vals_plot.append(x)
            if x <= pos_P:
                v = Ra - q_kNm * x
                m = Ra * x - q_kNm * x**2 / 2
            else:
                v = Ra - q_kNm * x - P_kN
                m = Ra * x - q_kNm * x**2 / 2 - P_kN * (x - pos_P)
            v_vals_plot.append(v)
            m_vals_plot.append(m)

    convencion_europea = st.checkbox("Convención Europea (Dibujar momentos positivos hacia abajo)", value=True)
    if convencion_europea:
        m_vals_plot = [-m for m in m_vals_plot]
        M_max_plot = -M_max
    else:
        M_max_plot = M_max

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='envelope-card'><div class='envelope-title' style='color:#dc2626'>Vd máximo en envolvente</div><div class='val-highlight'>{V_max:.2f} kN</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='envelope-card'><div class='envelope-title' style='color:#10b981'>Md máximo en envolvente</div><div class='val-highlight'>{M_max:.2f} kN·m</div></div>", unsafe_allow_html=True)

    st.divider()

    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=x_vals_plot, y=v_vals_plot, fill='tozeroy', fillcolor='rgba(220, 38, 38, 0.15)', mode='lines', line=dict(color='#dc2626', width=3), name='Cortante [kN]'))
    fig_v.add_hline(y=0, line_width=2, line_color="#334155")
    
    fig_v.add_annotation(x=0, y=v_vals_plot[0], text=f" {v_vals_plot[0]:.2f} kN ", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#dc2626", ax=30, ay=-30 if v_vals_plot[0]>0 else 30, font=dict(color="white", size=12), bgcolor="#dc2626", borderpad=3)
    fig_v.add_annotation(x=L_m, y=v_vals_plot[-1], text=f" {v_vals_plot[-1]:.2f} kN ", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#dc2626", ax=-30, ay=-30 if v_vals_plot[-1]>0 else 30, font=dict(color="white", size=12), bgcolor="#dc2626", borderpad=3)
    
    fig_v.update_layout(title="<b>Diagrama de Esfuerzo Cortante (V)</b>", xaxis_title="Posición en la viga (m)", yaxis_title="Cortante (kN)", plot_bgcolor="white", paper_bgcolor="white", xaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False), yaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False), margin=dict(t=50, b=40, l=40, r=40), height=350)
    st.plotly_chart(fig_v, use_container_width=True)

    fig_m = go.Figure()
    fig_m.add_trace(go.Scatter(x=x_vals_plot, y=m_vals_plot, fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.15)', mode='lines', line=dict(color='#10b981', width=3), name='Momento [kN·m]'))
    fig_m.add_hline(y=0, line_width=2, line_color="#334155")
    
    dir_y = 30 if convencion_europea else -30
    fig_m.add_annotation(x=pos_P, y=M_max_plot, text=f" {M_max:.2f} kN·m ", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#10b981", ax=0, ay=dir_y, font=dict(color="white", size=13), bgcolor="#10b981", borderpad=4)

    fig_m.update_layout(title="<b>Diagrama de Momento Flector (M)</b>", xaxis_title="Posición en la viga (m)", yaxis_title="Momento (kN·m)", plot_bgcolor="white", paper_bgcolor="white", xaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False), yaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False), margin=dict(t=50, b=40, l=40, r=40), height=350)
    st.plotly_chart(fig_m, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 8: RESULTADOS (RESUMEN EJECUTIVO)
# -----------------------------------------------------------------------------
elif page == "📑 8. Resultados":
    st.title("📑 Resumen de Resultados")
    mostrar_resumen_global()
    
    st.markdown("<div class='blue-box'><b>Parámetros del Resumen:</b> Configura las opciones finales para generar el informe.</div>", unsafe_allow_html=True)
    
    c_op1, c_op2, c_op3 = st.columns(3)
    arriostrado_res = c_op1.checkbox("Viga arriostrada (Sin riesgo de vuelco)", value=True)
    reducir_cortante_res = c_op2.checkbox("Aplicar reducción de cortante en apoyo", value=False)
    t_fuego_res = c_op3.selectbox("Tiempo a Fuego (min)", [15, 30, 45, 60, 90, 120], index=1)

    gamma_M = 1.25 if "GL" in mat else 1.30
    
    # ELU Flexión
    k_mod_M = obtener_k_mod(clase_servicio, duracion_M)
    if "GL" in mat:
        k_h = min((600 / h_mm)**0.1, 1.1) if h_mm < 600 else 1.0
    else:
        k_h = min((150 / h_mm)**0.2, 1.3) if h_mm < 150 else 1.0
        
    if arriostrado_res:
        k_crit = 1.00
    else:
        L_ef = L_m * 1000 * 0.95 + (2 * h_mm) 
        sigma_m_crit = (0.78 * (b_mm**2) * props_mat.get("E_0_05", props_mat["E_0_mean"]*0.67)) / (h_mm * L_ef)
        lambda_rel_m = math.sqrt(props_mat["f_m_k"] / sigma_m_crit)
        if lambda_rel_m <= 0.75: k_crit = 1.00
        elif lambda_rel_m <= 1.4: k_crit = 1.56 - 0.75 * lambda_rel_m
        else: k_crit = 1.0 / (lambda_rel_m**2)
        
    f_m_d = (k_mod_M * k_h * k_sys * k_crit * props_mat["f_m_k"]) / gamma_M
    sigma_d = (elu_max_M['M'] * 1e6) / props_geo["W_y"]
    ratio_flex = sigma_d / f_m_d

    # ELU Cortante
    k_mod_V = obtener_k_mod(clase_servicio, duracion_V)
    Vd_base = elu_max_V['V']
    if reducir_cortante_res: Vd_base = max(Vd_base - (elu_max_V['q'] * (h_mm/1000.0)), 0)
    tau_d = (1.5 * Vd_base * 1000) / ((b_mm * K_CR) * h_mm)
    f_v_d = (props_mat["f_v_k"] * k_mod_V * k_sys) / gamma_M
    ratio_cort = tau_d / f_v_d

    # ELS (Flechas EC5 puros)
    E_mean = props_mat["E_0_mean"]
    I_y = props_geo["I_y"]
    def f_uni(q): return (5.0 / 384.0) * ((q * (L_m * 1000)**4) / (E_mean * I_y))
    def f_pun(P): return (1.0 / 48.0) * (((P * 1000) * (L_m * 1000)**3) / (E_mean * I_y))
    
    kdef = KDEF_DICT[clase_servicio]
    w_inst_G = f_uni(gk)
    w_inst_Q = max(f_uni(quk), f_pun(Qpk_kN))
    w_inst_total = w_inst_G + w_inst_Q
    
    w_fin_G = w_inst_G * (1 + kdef)
    w_fin_Q = w_inst_Q * (1 + PSI2_VIV * kdef)
    w_fin_total = w_fin_G + w_fin_Q
    w_activa = w_fin_total - w_inst_G
    
    ratio_inst = w_inst_total / ((L_m * 1000) / 300) 
    ratio_act = w_activa / ((L_m * 1000) / 400) 
    ratio_fin = w_fin_total / ((L_m * 1000) / 250)    

    # Fuego (3 caras expuestas por defecto para el resumen)
    beta_n = 0.70 if "GL" in mat else 0.80
    d_ef = (beta_n * t_fuego_res) + min(t_fuego_res / 20.0, 1.0) * 7.0
    b_fi = b_mm - 2 * d_ef
    h_fi = h_mm - d_ef
    if b_fi > 0 and h_fi > 0:
        Wy_fi = (b_fi * h_fi**2) / 6.0
        sigma_fi = (combo_qp['M'] * 1e6) / Wy_fi
        f_m_fi = (1.15 if "GL" in mat else 1.25) * props_mat["f_m_k"]
        ratio_fuego_flex = sigma_fi / f_m_fi
        
        tau_fi = (1.5 * combo_qp['V'] * 1000) / (b_fi * h_fi)
        f_v_fi = (1.15 if "GL" in mat else 1.25) * props_mat["f_v_k"]
        ratio_fuego_cort = tau_fi / f_v_fi
    else:
        ratio_fuego_flex = 9.99
        ratio_fuego_cort = 9.99

    max_ratio = max(ratio_flex, ratio_cort, ratio_inst, ratio_act, ratio_fin, ratio_fuego_flex, ratio_fuego_cort)

    html_resumen = f"""
    <style>
        .res-container {{ font-family: 'Segoe UI', Arial, sans-serif; color: #44546a; margin-top: 10px; }}
        .res-main-bar {{ background-color: #e6ebed; border-left: 6px solid #587e91; display: flex; align-items: center; padding: 10px 15px; margin-bottom: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .res-main-title {{ font-weight: 700; color: #47768c; flex-grow: 1; font-size: 1.15rem; text-transform: uppercase; letter-spacing: 0.5px; }}
        .res-main-val {{ font-weight: 700; color: #47768c; font-size: 1.25rem; background: #fff; padding: 2px 10px; border-radius: 4px; }}
        .res-desc {{ font-size: 0.95rem; color: #5c707c; margin-bottom: 25px; line-height: 1.5; padding-left: 5px; }}
        .res-sec-bar {{ background-color: #f1f4f5; border-left: 6px solid #8e9599; padding: 6px 12px; margin-top: 20px; display: flex; font-size: 1rem; font-weight: 700; color: #587e91; }}
        .res-table {{ width: 100%; border-collapse: collapse; font-size: 0.95rem; margin-bottom: 10px; }}
        .res-table th {{ text-align: left; padding: 8px 12px; color: #47768c; font-weight: 700; border-bottom: 2px solid #dde3e6; }}
        .res-table td {{ padding: 10px 12px; border-bottom: 1px solid #edf1f2; }}
        .res-table tr:hover {{ background-color: #f8fafc; }}
        .td-name {{ color: #587e91; width: 45%; }}
        .td-index {{ font-weight: 800; width: 15%; text-align: center; }}
        .td-comb {{ color: #7f95a3; font-size: 0.9rem; }}
    </style>
    <div class="res-container">
        <div class="res-main-bar">
            <div class="res-main-title">Índice de aprovechamiento global</div>
            <div class="res-main-val" style="color: {'#dc2626' if max_ratio>1 else '#47768c'};">{max_ratio*100:.0f}%</div>
        </div>
        <div class="res-desc">
            El índice de aprovechamiento es la relación entre el efecto actuante y el límite establecido para dicho efecto (tensiones y/o deformaciones). Por lo tanto, un índice superior al 100% implica que no cumple los requisitos establecidos.
        </div>
        <div class="res-sec-bar">
            <div style="flex-grow: 1;">Estado Límite Último [ELU]</div>
            <div style="width: 15%; text-align: center; font-size: 0.9rem;">Índice</div>
            <div style="width: 40%; font-size: 0.9rem;">Combinación límite</div>
        </div>
        <table class="res-table">
            <tr>
                <td class="td-name">Resistencia a flexión</td>
                <td class="td-index" style="color: {'#dc2626' if ratio_flex>1 else '#47768c'};">{ratio_flex*100:.0f} %</td>
                <td class="td-comb">{elu_max_M['nombre']}</td>
            </tr>
            <tr>
                <td class="td-name">Resistencia a cortante</td>
                <td class="td-index" style="color: {'#dc2626' if ratio_cort>1 else '#47768c'};">{ratio_cort*100:.0f} %</td>
                <td class="td-comb">{elu_max_V['nombre']}</td>
            </tr>
        </table>
        <div class="res-sec-bar">Estado Límite de Servicio [ELS]</div>
        <table class="res-table">
            <tr>
                <td class="td-name">Integridad elementos constructivos</td>
                <td class="td-index" style="color: {'#dc2626' if ratio_act>1 else '#47768c'};">{ratio_act*100:.0f} %</td>
                <td class="td-comb">Deformación Activa EC5 (L/400)</td>
            </tr>
            <tr>
                <td class="td-name">Confort de los usuarios</td>
                <td class="td-index" style="color: {'#dc2626' if ratio_inst>1 else '#47768c'};">{ratio_inst*100:.0f} %</td>
                <td class="td-comb">Deformación Instantánea EC5 (L/300)</td>
            </tr>
            <tr>
                <td class="td-name">Apariencia de la obra</td>
                <td class="td-index" style="color: {'#dc2626' if ratio_fin>1 else '#47768c'};">{ratio_fin*100:.0f} %</td>
                <td class="td-comb">Deformación Final EC5 (L/250)</td>
            </tr>
        </table>
        <div class="res-sec-bar">Situación accidental de incendio [ACC]</div>
        <table class="res-table">
            <tr>
                <td class="td-name">Resistencia a flexión</td>
                <td class="td-index" style="color: {'#dc2626' if ratio_fuego_flex>1 else '#47768c'};">{"FALLA" if ratio_fuego_flex > 10 else f"{ratio_fuego_flex*100:.0f} %"}</td>
                <td class="td-comb">Cuasi-permanente ({t_fuego_res} min - 3 caras)</td>
            </tr>
            <tr>
                <td class="td-name">Resistencia a cortante</td>
                <td class="td-index" style="color: {'#dc2626' if ratio_fuego_cort>1 else '#47768c'};">{"FALLA" if ratio_fuego_cort > 10 else f"{ratio_fuego_cort*100:.0f} %"}</td>
                <td class="td-comb">Cuasi-permanente ({t_fuego_res} min - 3 caras)</td>
            </tr>
        </table>
        <div class="res-sec-bar">Reacción en apoyo (Para diseño de uniones)</div>
        <table class="res-table">
            <tr>
                <td class="td-name">Vertical en ELU &nbsp;&nbsp;<span style="font-size:0.8rem; color:#8e9599;">R<sub>d,exterior,V</sub></span></td>
                <td class="td-index" style="color:#111827; font-size:1.05rem;">{elu_max_V['V']:.2f} kN</td>
                <td class="td-comb">{elu_max_V['nombre']}</td>
            </tr>
        </table>
    </div>
    """
    
    # Aplanamos el HTML quitando los saltos de línea para que Streamlit no lo rompa
    html_resumen = html_resumen.replace('\n', '')
    
    st.markdown(html_resumen, unsafe_allow_html=True)
