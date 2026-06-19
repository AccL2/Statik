import streamlit as st
import math
import streamlit.components.v1 as components
import plotly.graph_objects as go

# =========================================================
# CONFIGURACIÓN Y ESTILO GLOBAL
# =========================================================
st.set_page_config(page_title="Holzbau Pro – Pilares EC5", layout="wide", page_icon="🏛️")

st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.envelope-card { background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
border: 1px solid #bfdbfe; border-radius: 12px; padding: 20px; margin-bottom: 1rem;
box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
.envelope-title { font-size: 1.1rem; font-weight: 700; color: #1e3a8a;
margin-bottom: 8px; border-bottom: 2px solid #dbeafe; padding-bottom: 4px; }
.val-highlight { font-size: 1.8rem; font-weight: 800; color: #111827; }
.val-sub { font-size: 0.95rem; color: #4b5563; font-weight: 500; margin-top: 4px; }
.math-box { background: #1e293b; color: #f8fafc; font-family: monospace;
padding: 12px 16px; border-radius: 8px; margin: 10px 0; font-size: 1.05rem; }
.math-res { color: #10b981; font-weight: bold; }
.expl-box { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 12px 16px;
border-radius: 4px; color: #166534; font-size: 0.95rem; margin-top: 10px; }
.blue-box { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a;
padding: 12px 14px; border-radius: 8px; margin-bottom: 1rem; font-size: 0.95rem; }
.link-box { background: #faf5ff; border: 1px dashed #fde047; color: #854d0e;
padding: 10px 14px; border-radius: 8px; margin-bottom: 1rem; font-size: 0.95rem;
font-weight: 500;}
.result-box { padding: 1rem 1.2rem; border-radius: 14px; margin-bottom: 1rem;
border: 1px solid #e5e7eb; background: #f9fafb; }
.result-ok { background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
border: 1px solid #10b981; color: #065f46; }
.result-bad { background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
border: 1px solid #ef4444; color: #991b1b; }
.badge-ok { background: #dcfce7; color: #166534; padding: 4px 12px;
border-radius: 99px; font-weight: bold; border: 1px solid #bbf7d0;}
.badge-bad { background: #fee2e2; color: #991b1b; padding: 4px 12px;
border-radius: 99px; font-weight: bold; border: 1px solid #fecaca;}
.global-summary { background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px 12px;
border-radius: 6px; font-size: 0.9rem; color: #475569; margin-bottom: 15px;
display: flex; gap: 20px; flex-wrap: wrap; }
.title-main { color: #1e293b; font-size: 1.3rem; font-weight: 700;
border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 15px;}
.nivel-card { border-radius: 12px; padding: 20px; margin-bottom: 20px; }
.nivel-title { font-size: 1.2rem; font-weight: 800; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# BASES DE DATOS GLOBALES
# =========================================================
MATERIALES = {
    "C14":   {"f_m_k": 14.0, "f_t_0_k":  8.0, "f_c_0_k": 16.0, "f_v_k": 3.0, "E_0_mean":  7000, "E_0_05":  4700, "rho_k": 290, "rho_mean": 350},
    "C16":   {"f_m_k": 16.0, "f_t_0_k": 10.0, "f_c_0_k": 17.0, "f_v_k": 3.2, "E_0_mean":  8000, "E_0_05":  5400, "rho_k": 310, "rho_mean": 370},
    "C18":   {"f_m_k": 18.0, "f_t_0_k": 11.0, "f_c_0_k": 18.0, "f_v_k": 3.4, "E_0_mean":  9000, "E_0_05":  6000, "rho_k": 320, "rho_mean": 380},
    "C24":   {"f_m_k": 24.0, "f_t_0_k": 14.5, "f_c_0_k": 21.0, "f_v_k": 4.0, "E_0_mean": 11000, "E_0_05":  7400, "rho_k": 350, "rho_mean": 420},
    "C30":   {"f_m_k": 30.0, "f_t_0_k": 18.0, "f_c_0_k": 26.0, "f_v_k": 4.0, "E_0_mean": 12000, "E_0_05":  8000, "rho_k": 380, "rho_mean": 460},
    "GL24h": {"f_m_k": 24.0, "f_t_0_k": 16.5, "f_c_0_k": 24.0, "f_v_k": 3.5, "E_0_mean": 11600, "E_0_05":  9600, "rho_k": 385, "rho_mean": 430},
    "GL28h": {"f_m_k": 28.0, "f_t_0_k": 19.5, "f_c_0_k": 26.5, "f_v_k": 3.5, "E_0_mean": 12600, "E_0_05": 10500, "rho_k": 425, "rho_mean": 460},
    "GL32h": {"f_m_k": 32.0, "f_t_0_k": 22.5, "f_c_0_k": 29.0, "f_v_k": 3.8, "E_0_mean": 13700, "E_0_05": 11400, "rho_k": 440, "rho_mean": 490},
}

KMOD_TABLA = {
    "1": {"Permanente": 0.60, "Larga": 0.70, "Media": 0.80, "Corta": 0.90, "Instantánea": 1.10},
    "2": {"Permanente": 0.60, "Larga": 0.70, "Media": 0.80, "Corta": 0.90, "Instantánea": 1.10},
    "3": {"Permanente": 0.50, "Larga": 0.55, "Media": 0.65, "Corta": 0.70, "Instantánea": 0.90},
}

CONDICIONES_APOYO = {
    "Bi-articulado (β = 1.0)": 1.0,
    "Empotrado-Articulado (β = 0.7)": 0.7,
    "Bi-empotrado (β = 0.5)": 0.5,
    "Empotrado-Libre / Voladizo (β = 2.0)": 2.0,
}


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def calc_kc(lam_rel, bc):
    if lam_rel <= 0.3:
        return 1.0, 0.5 * (1 + bc * (lam_rel - 0.3) + lam_rel**2)
    k = 0.5 * (1 + bc * (lam_rel - 0.3) + lam_rel**2)
    disc = max(k**2 - lam_rel**2, 1e-12)
    kc = 1.0 / (k + math.sqrt(disc))
    return kc, k


def render_tabla_propiedades(titulo, filas, height=430, color="#2563eb"):
    filas_html = ""
    for prop, valor in filas:
        filas_html += (
            f"<tr><td style='padding:10px 14px;border-bottom:1px solid #f1f5f9;"
            f"color:#4b5563;'>{prop}</td><td style='padding:10px 14px;border-bottom:"
            f"1px solid #f1f5f9;text-align:right;color:#111827;font-weight:600;'>"
            f"{valor}</td></tr>"
        )
    html = (
        f"<html><head><meta charset='utf-8'><style>"
        f"body{{margin:0;font-family:Arial;background:transparent;}}"
        f".card{{background:linear-gradient(180deg,#fff 0%,#f8fafc 100%);"
        f"border:1px solid #e5e7eb;border-radius:18px;padding:18px;"
        f"box-sizing:border-box;box-shadow:0 8px 24px rgba(15,23,42,0.06);}}"
        f".title{{font-size:20px;font-weight:700;margin-bottom:14px;color:#111827;"
        f"padding-bottom:10px;border-bottom:3px solid {color};}}"
        f"table{{width:100%;border-collapse:separate;border-spacing:0;font-size:14px;"
        f"background:white;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;}}"
        f"thead tr{{background:#f3f4f6;}}th{{text-align:left;padding:12px 14px;"
        f"font-weight:700;color:#374151;border-bottom:1px solid #e5e7eb;}}"
        f"th:last-child{{text-align:right;}}"
        f"tbody tr:nth-child(even){{background:#fafafa;}}"
        f"</style></head><body><div class='card'><div class='title'>{titulo}</div>"
        f"<table><thead><tr><th>Propiedad</th><th>Valor</th></tr></thead>"
        f"<tbody>{filas_html}</tbody></table></div></body></html>"
    )
    components.html(html, height=height, scrolling=False)


def mostrar_tarjeta_resultado(ratio, titulo="", detalle=""):
    cumple = ratio <= 1.0
    if cumple:
        color, estado, clase = "#10b981", "✅ Cumple", "result-ok"
    else:
        color, estado, clase = "#ef4444", "❌ No cumple", "result-bad"
    aprov = ratio * 100
    det_html = f'<div style="margin-top:0.25rem;font-size:0.9rem;color:#6b7280;">{detalle}</div>' if detalle else ''
    st.markdown(
        f'<div class="result-box {clase}"><div style="display:flex;'
        f'justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">'
        f'<div><div style="font-size:1.4rem;font-weight:800;">{estado}</div>'
        f'<div style="margin-top:0.35rem;font-size:1rem;">{titulo}</div>{det_html}</div>'
        f'<div style="min-width:140px;text-align:center;background:white;border:2px solid '
        f'{color};border-radius:16px;padding:0.8rem 1rem;box-shadow:0 4px 12px rgba(0,0,0,0.04);">'
        f'<div style="font-size:0.9rem;color:#6b7280;">Aprovechamiento</div>'
        f'<div style="font-size:2rem;font-weight:800;color:{color};">η = {ratio:.2f}</div>'
        f'<div style="font-size:0.85rem;color:#6b7280;">{aprov:.1f}%</div>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )


def ejemplo_pilar(b, h, L, N, My, Mz, beta_y_ex, beta_z_ex, mat_key, cs, dur):
    """Calcula un pilar completo y devuelve un dict con todo."""
    pm = MATERIALES[mat_key]
    km = KMOD_TABLA[cs][dur]
    es_gl = "GL" in mat_key
    gM = 1.25 if es_gl else 1.30
    bc = 0.1 if es_gl else 0.2
    A = b * h
    iy = h / math.sqrt(12)
    iz = b / math.sqrt(12)
    Wy = b * h**2 / 6.0
    Wz = h * b**2 / 6.0
    Lef_y = beta_y_ex * L * 1000
    Lef_z = beta_z_ex * L * 1000
    lam_y = Lef_y / iy
    lam_z = Lef_z / iz
    fc0k = pm["f_c_0_k"]
    E005 = pm["E_0_05"]
    fmk = pm["f_m_k"]
    lr_y = (lam_y / math.pi) * math.sqrt(fc0k / E005)
    lr_z = (lam_z / math.pi) * math.sqrt(fc0k / E005)
    kcy, ky = calc_kc(lr_y, bc)
    kcz, kz = calc_kc(lr_z, bc)
    fc0d = km * fc0k / gM
    sc = (N * 1000) / A if N > 0 else 0
    smy = (My * 1e6) / Wy if My > 0 else 0
    smz = (Mz * 1e6) / Wz if Mz > 0 else 0
    if es_gl:
        khy = min((600/h)**0.1, 1.1) if h < 600 else 1.0
    else:
        khy = min((150/h)**0.2, 1.3) if h < 150 else 1.0
    fmyd = km * khy * fmk / gM
    fmzd = fmyd  # asumimos cuadrado para simplificar
    no_pandeo = (lr_y <= 0.3) and (lr_z <= 0.3)
    if no_pandeo:
        tc = (sc / fc0d)**2 if fc0d > 0 else 0
    else:
        kc_min = min(kcy, kcz)
        tc = sc / (kc_min * fc0d) if (kc_min * fc0d) > 0 else 999
    tmy = smy / fmyd if fmyd > 0 else 0
    tmz = smz / fmzd if fmzd > 0 else 0
    r1 = tc + tmy + 0.7 * tmz
    r2 = tc + 0.7 * tmy + tmz
    ratio = max(r1, r2)
    return {
        "A": A, "iy": iy, "iz": iz, "Wy": Wy, "lam_y": lam_y, "lam_z": lam_z,
        "lr_y": lr_y, "lr_z": lr_z, "kcy": kcy, "kcz": kcz,
        "fc0d": fc0d, "sc": sc, "smy": smy, "fmyd": fmyd,
        "tc": tc, "tmy": tmy, "tmz": tmz,
        "ratio": ratio, "no_pandeo": no_pandeo,
        "kc_min": min(kcy, kcz),
    }


# =========================================================
# MENÚ LATERAL
# =========================================================
st.sidebar.markdown("## 🧭 Navegación")
page = st.sidebar.radio(
    "Ir a…",
    [
        "🏛️ 1. Datos del Pilar",
        "📐 2. Pandeo (EC5 §6.3.2)",
        "⚖️ 3. Interacción N + M",
        "🔥 4. Fuego",
        "📑 5. Resultados",
        "📖 6. Ejemplos Didácticos",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.markdown("### 📐 Geometría del Pilar")
L_m = st.sidebar.number_input("Altura L [m]", value=3.00, step=0.10, min_value=0.50)
b_mm = st.sidebar.number_input("Base b [mm] (eje débil)", value=160, step=10, min_value=40)
h_mm = st.sidebar.number_input("Canto h [mm] (eje fuerte)", value=160, step=10, min_value=40)

st.sidebar.markdown("### 🔗 Condiciones de Contorno")
beta_y_custom = st.sidebar.checkbox("β_y personalizado", value=False)
if beta_y_custom:
    beta_y = st.sidebar.number_input("β_y", value=1.0, step=0.1, min_value=0.1, max_value=3.0)
else:
    tipo_y = st.sidebar.selectbox("Apoyo eje Y", list(CONDICIONES_APOYO.keys()), index=0)
    beta_y = CONDICIONES_APOYO[tipo_y]
beta_z_custom = st.sidebar.checkbox("β_z personalizado", value=False)
if beta_z_custom:
    beta_z = st.sidebar.number_input("β_z", value=1.0, step=0.1, min_value=0.1, max_value=3.0)
else:
    tipo_z = st.sidebar.selectbox("Apoyo eje Z", list(CONDICIONES_APOYO.keys()), index=0)
    beta_z = CONDICIONES_APOYO[tipo_z]

st.sidebar.markdown("### ⚖️ Esfuerzos de Cálculo")
N_d_kN = st.sidebar.number_input("N_d [kN]", value=80.0, step=5.0, min_value=0.0)
modo_M = st.sidebar.radio("Momento:", ["Sin momento", "Momento directo", "Excentricidad"], horizontal=True)
if modo_M == "Momento directo":
    M_yd_kNm = st.sidebar.number_input("M_y,d [kN·m]", value=2.0, step=0.5, min_value=0.0)
    M_zd_kNm = st.sidebar.number_input("M_z,d [kN·m]", value=0.0, step=0.5, min_value=0.0)
    e_y_mm = 0.0; e_z_mm = 0.0
elif modo_M == "Excentricidad":
    e_y_mm = st.sidebar.number_input("e_y [mm]", value=20.0, step=5.0, min_value=0.0)
    e_z_mm = st.sidebar.number_input("e_z [mm]", value=0.0, step=5.0, min_value=0.0)
    M_yd_kNm = N_d_kN * e_y_mm / 1000.0
    M_zd_kNm = N_d_kN * e_z_mm / 1000.0
else:
    M_yd_kNm = 0.0; M_zd_kNm = 0.0; e_y_mm = 0.0; e_z_mm = 0.0

st.sidebar.markdown("### 🌲 Material y Entorno")
mat = st.sidebar.selectbox("Madera", list(MATERIALES.keys()), index=5)
clase_servicio = st.sidebar.selectbox("Clase Servicio", ["1", "2", "3"], index=0)
duracion = st.sidebar.selectbox("Duración carga", ["Permanente", "Larga", "Media", "Corta", "Instantánea"], index=2)

# =========================================================
# CÁLCULOS GLOBALES
# =========================================================
props_mat = MATERIALES[mat]
k_mod = KMOD_TABLA[clase_servicio][duracion]
es_laminada = "GL" in mat
gamma_M = 1.25 if es_laminada else 1.30
beta_c = 0.1 if es_laminada else 0.2

A_mm2 = b_mm * h_mm
I_y = b_mm * h_mm**3 / 12.0
I_z = h_mm * b_mm**3 / 12.0
W_y = b_mm * h_mm**2 / 6.0
W_z = h_mm * b_mm**2 / 6.0
i_y = h_mm / math.sqrt(12)
i_z = b_mm / math.sqrt(12)

L_ef_y_mm = beta_y * L_m * 1000
L_ef_z_mm = beta_z * L_m * 1000
lambda_y = L_ef_y_mm / i_y
lambda_z = L_ef_z_mm / i_z

f_c_0_k = props_mat["f_c_0_k"]
E_0_05 = props_mat["E_0_05"]
f_m_k = props_mat["f_m_k"]

lambda_rel_y = (lambda_y / math.pi) * math.sqrt(f_c_0_k / E_0_05)
lambda_rel_z = (lambda_z / math.pi) * math.sqrt(f_c_0_k / E_0_05)
k_c_y, k_factor_y = calc_kc(lambda_rel_y, beta_c)
k_c_z, k_factor_z = calc_kc(lambda_rel_z, beta_c)
N_cr_y = (math.pi**2 * E_0_05 * I_y) / (L_ef_y_mm**2) / 1000.0
N_cr_z = (math.pi**2 * E_0_05 * I_z) / (L_ef_z_mm**2) / 1000.0
N_cr_min = min(N_cr_y, N_cr_z)

sigma_c_0_d = (N_d_kN * 1000) / A_mm2 if N_d_kN > 0 else 0.0
sigma_m_y_d = (M_yd_kNm * 1e6) / W_y if M_yd_kNm > 0 else 0.0
sigma_m_z_d = (M_zd_kNm * 1e6) / W_z if M_zd_kNm > 0 else 0.0

f_c_0_d = k_mod * f_c_0_k / gamma_M
if es_laminada:
    k_h_y = min((600/h_mm)**0.1, 1.1) if h_mm < 600 else 1.0
    k_h_z = min((600/b_mm)**0.1, 1.1) if b_mm < 600 else 1.0
else:
    k_h_y = min((150/h_mm)**0.2, 1.3) if h_mm < 150 else 1.0
    k_h_z = min((150/b_mm)**0.2, 1.3) if b_mm < 150 else 1.0
f_m_y_d = k_mod * k_h_y * f_m_k / gamma_M
f_m_z_d = k_mod * k_h_z * f_m_k / gamma_M
k_m = 0.7

sin_riesgo_pandeo = (lambda_rel_y <= 0.3) and (lambda_rel_z <= 0.3)
hay_momentos = (M_yd_kNm > 0) or (M_zd_kNm > 0)

if f_c_0_d > 0:
    if sin_riesgo_pandeo:
        tc_y = (sigma_c_0_d / f_c_0_d)**2; tc_z = tc_y
        eq_label = "EC5 Ec. 6.19/6.20 (sin pandeo)"
    else:
        tc_y = sigma_c_0_d / (k_c_y * f_c_0_d) if k_c_y > 0 else 999
        tc_z = sigma_c_0_d / (k_c_z * f_c_0_d) if k_c_z > 0 else 999
        eq_label = "EC5 Ec. 6.23/6.24 (con pandeo)"
else:
    tc_y = 0; tc_z = 0; eq_label = ""

tm_y = sigma_m_y_d / f_m_y_d if f_m_y_d > 0 else 0
tm_z = sigma_m_z_d / f_m_z_d if f_m_z_d > 0 else 0
ratio_int_y = tc_y + tm_y + k_m * tm_z
ratio_int_z = tc_z + k_m * tm_y + tm_z
ratio_global = max(ratio_int_y, ratio_int_z)
eje_critico = "Y" if ratio_int_y >= ratio_int_z else "Z"

ratio_comp_simple = sigma_c_0_d / f_c_0_d if f_c_0_d > 0 else 0
ratio_buck_y = sigma_c_0_d / (k_c_y * f_c_0_d) if (k_c_y * f_c_0_d) > 0 else 0
ratio_buck_z = sigma_c_0_d / (k_c_z * f_c_0_d) if (k_c_z * f_c_0_d) > 0 else 0
ratio_pandeo_puro = max(ratio_buck_y, ratio_buck_z)


def mostrar_resumen_global():
    ecc = f"<div><b>Exc.:</b> e_y={e_y_mm:.0f}, e_z={e_z_mm:.0f} mm</div>" if modo_M == "Excentricidad" else ""
    st.markdown(f"""<div class="global-summary">
    <div><b>Sección:</b> {b_mm}×{h_mm}</div><div><b>Altura:</b> {L_m:.2f} m</div>
    <div><b>Material:</b> {mat} (CS{clase_servicio})</div><div><b>N<sub>d</sub>:</b> {N_d_kN:.1f} kN</div>
    <div><b>β<sub>y</sub>={beta_y:.1f} / β<sub>z</sub>={beta_z:.1f}</b></div>{ecc}
    </div>""", unsafe_allow_html=True)


# =============================================================================
# PÁGINA 1: DATOS DEL PILAR
# =============================================================================
if page == "🏛️ 1. Datos del Pilar":
    st.title("🏛️ Pilar de Madera: Datos y Propiedades")
    mostrar_resumen_global()

    st.markdown("""
    <div class="blue-box">
    <b>Herramienta de Pilares EC5:</b> Comprueba la <b>inestabilidad por pandeo</b>
    (§6.3.2) y la <b>interacción compresión + flexión</b> (§6.2.4 / §6.3.2) de
    pilares de madera maciza o laminada encolada con sección rectangular.
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        filas_sec = [
            ("<i>b</i> (base, eje débil)", f"{b_mm} mm"),
            ("<i>h</i> (canto, eje fuerte)", f"{h_mm} mm"),
            ("<i>A</i>", f"{A_mm2:,} mm²"),
            ("<i>I<sub>y</sub></i>", f"{I_y:,.0f} mm⁴"),
            ("<i>I<sub>z</sub></i>", f"{I_z:,.0f} mm⁴"),
            ("<i>W<sub>y</sub></i>", f"{W_y:,.0f} mm³"),
            ("<i>W<sub>z</sub></i>", f"{W_z:,.0f} mm³"),
            ("<i>i<sub>y</sub></i>", f"{i_y:.1f} mm"),
            ("<i>i<sub>z</sub></i>", f"{i_z:.1f} mm"),
        ]
        render_tabla_propiedades("📏 Sección Transversal", filas_sec, height=480, color="#7c3aed")

    with col2:
        filas_mat = [
            ("Material", mat),
            ("<i>f<sub>c,0,k</sub></i>", f"{f_c_0_k:.1f} N/mm²"),
            ("<i>f<sub>m,k</sub></i>", f"{f_m_k:.1f} N/mm²"),
            ("<i>E<sub>0,mean</sub></i>", f"{props_mat['E_0_mean']:,} N/mm²"),
            ("<i>E<sub>0,05</sub></i>", f"{E_0_05:,} N/mm²"),
            ("<i>ρ<sub>k</sub></i>", f"{props_mat['rho_k']} kg/m³"),
            ("Clase de servicio", clase_servicio),
            ("<i>k<sub>mod</sub></i>", f"{k_mod:.2f}"),
            ("γ<sub>M</sub>", f"{gamma_M:.2f}"),
            ("β<sub>c</sub> (imperfección)", f"{beta_c:.1f}"),
        ]
        render_tabla_propiedades("🌲 Material y Coeficientes", filas_mat, height=480, color="#2563eb")

    st.divider()
    st.subheader("⚖️ Esfuerzos y Tensiones de Cálculo")

    c1, c2, c3 = st.columns(3)
    c1.metric("N_d (Compresión)", f"{N_d_kN:.1f} kN")
    c2.metric("M_y,d", f"{M_yd_kNm:.2f} kN·m")
    c3.metric("M_z,d", f"{M_zd_kNm:.2f} kN·m")

    c1, c2, c3 = st.columns(3)
    c1.metric("σ_c,0,d", f"{sigma_c_0_d:.2f} N/mm²")
    c2.metric("σ_m,y,d", f"{sigma_m_y_d:.2f} N/mm²")
    c3.metric("σ_m,z,d", f"{sigma_m_z_d:.2f} N/mm²")

    c1, c2, c3 = st.columns(3)
    c1.metric("f_c,0,d", f"{f_c_0_d:.2f} N/mm²")
    c2.metric("f_m,y,d", f"{f_m_y_d:.2f} N/mm²")
    c3.metric("f_m,z,d", f"{f_m_z_d:.2f} N/mm²")

    if modo_M == "Excentricidad":
        st.markdown(f"""
        <div class='expl-box'>
        <b>Momentos por excentricidad:</b><br>
        M<sub>y,d</sub> = N<sub>d</sub> · e<sub>y</sub> = {N_d_kN:.1f} × {e_y_mm:.0f}/1000
        = <b>{M_yd_kNm:.2f} kN·m</b><br>
        M<sub>z,d</sub> = N<sub>d</sub> · e<sub>z</sub> = {N_d_kN:.1f} × {e_z_mm:.0f}/1000
        = <b>{M_zd_kNm:.2f} kN·m</b>
        </div>""", unsafe_allow_html=True)


# =============================================================================
# PÁGINA 2: PANDEO
# =============================================================================
elif page == "📐 2. Pandeo (EC5 §6.3.2)":
    st.title("📐 Pandeo por Compresión (Inestabilidad)")
    mostrar_resumen_global()

    with st.expander("📚 Guía del Maestro: ¿Qué es el pandeo?", expanded=False):
        st.markdown("""
        Un pilar corto se rompe por **aplastamiento**. Pero un pilar esbelto se
        **dobla lateralmente** antes de alcanzar la resistencia del material.
        El EC5 reduce la resistencia útil con un factor $k_c$:

        * $\\lambda_{rel} \\leq 0.3$: Pilar robusto → $k_c = 1.0$
        * $\\lambda_{rel}$ creciente → $k_c$ disminuye → menos capacidad

        $\\beta_c$ distingue maciza ($0.2$, más imperfecciones) de laminada ($0.1$).
        """)

    # --- PASO 1 ---
    st.markdown("### 1️⃣ Longitudes Eficaces de Pandeo")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='math-box'>
        <b>Eje Y (fuerte):</b><br>
        L<sub>ef,y</sub> = β<sub>y</sub> · L = {beta_y:.2f} × {L_m*1000:.0f}
        = <span class='math-res'>{L_ef_y_mm:.0f} mm</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='math-box'>
        <b>Eje Z (débil):</b><br>
        L<sub>ef,z</sub> = β<sub>z</sub> · L = {beta_z:.2f} × {L_m*1000:.0f}
        = <span class='math-res'>{L_ef_z_mm:.0f} mm</span>
        </div>""", unsafe_allow_html=True)

    # --- PASO 2 ---
    st.markdown("### 2️⃣ Esbelteces Mecánicas (λ)")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='math-box'>
        λ<sub>y</sub> = L<sub>ef,y</sub> / i<sub>y</sub>
        = {L_ef_y_mm:.0f} / {i_y:.1f}
        = <span class='math-res'>{lambda_y:.1f}</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='math-box'>
        λ<sub>z</sub> = L<sub>ef,z</sub> / i<sub>z</sub>
        = {L_ef_z_mm:.0f} / {i_z:.1f}
        = <span class='math-res'>{lambda_z:.1f}</span>
        </div>""", unsafe_allow_html=True)

    # --- PASO 3 ---
    st.markdown("### 3️⃣ Esbelteces Relativas (λ_rel)")
    c1, c2 = st.columns(2)
    for col, eje, lr, lam in [(c1, "Y", lambda_rel_y, lambda_y), (c2, "Z", lambda_rel_z, lambda_z)]:
        clr = "#10b981" if lr <= 0.3 else ("#f59e0b" if lr <= 1.0 else "#ef4444")
        with col:
            st.markdown(f"""<div class='math-box'>
            λ<sub>rel,{eje.lower()}</sub> = (λ<sub>{eje.lower()}</sub> / π) · √(f<sub>c,0,k</sub> / E<sub>0,05</sub>)<br>
            = ({lam:.1f} / π) · √({f_c_0_k:.1f} / {E_0_05})<br>
            = <span style='color:{clr};font-weight:bold;'>{lr:.3f}</span>
            </div>""", unsafe_allow_html=True)
            if lr <= 0.3:
                st.markdown(f"<span class='badge-ok'>λ_rel,{eje.lower()} ≤ 0.3 → Sin pandeo</span>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='badge-bad'>λ_rel,{eje.lower()} > 0.3 → Riesgo de pandeo</span>",
                            unsafe_allow_html=True)

    st.divider()

    # --- PASO 4 ---
    st.markdown("### 4️⃣ Factores de Pandeo (k_c)")
    c1, c2 = st.columns(2)
    for col, eje, lr, kf, kc in [(c1,"Y",lambda_rel_y,k_factor_y,k_c_y),
                                  (c2,"Z",lambda_rel_z,k_factor_z,k_c_z)]:
        with col:
            st.markdown(f"""<div class='math-box'>
            <b>Eje {eje}:</b><br>
            k<sub>{eje.lower()}</sub> = 0.5·(1 + {beta_c}·({lr:.3f} − 0.3) + {lr:.3f}²)
            = {kf:.4f}<br><br>
            k<sub>c,{eje.lower()}</sub> = 1 / (k + √(k² − λ²))
            = <span class='math-res'>{kc:.4f}</span>
            </div>""", unsafe_allow_html=True)

    # --- PASO 5: Euler ---
    st.markdown("### 5️⃣ Carga Crítica de Euler")
    c1, c2, c3 = st.columns(3)
    c1.metric("N_cr,y", f"{N_cr_y:.1f} kN")
    c2.metric("N_cr,z", f"{N_cr_z:.1f} kN")
    ratio_euler = N_d_kN / N_cr_min if N_cr_min > 0 else 999
    c3.metric("N_d / N_cr,min", f"{ratio_euler:.3f}")

    if N_cr_min > 0 and N_d_kN > 0:
        seg = N_cr_min / N_d_kN
        if seg > 3:
            st.markdown(f"<div class='expl-box'>Carga {seg:.1f}× menor que la crítica de Euler.</div>",
                        unsafe_allow_html=True)
        elif seg > 1:
            st.markdown(f"<div class='expl-box' style='border-color:#f59e0b;background:#fffbeb;"
                        f"color:#854d0e;'>Margen moderado: {seg:.1f}× la carga crítica.</div>",
                        unsafe_allow_html=True)
        else:
            st.error("⚠️ ¡La carga supera la carga crítica de Euler!")

    st.divider()

    # --- PASO 6: Comprobación ---
    st.markdown("### 6️⃣ Comprobación a Pandeo (Compresión Pura)")
    kc_min = min(k_c_y, k_c_z)
    f_c_buck = kc_min * f_c_0_d
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='envelope-card'>", unsafe_allow_html=True)
        st.markdown("<div class='title-main'>Tensión Actuante</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='val-highlight'>{sigma_c_0_d:.2f}</span> "
                    f"<span class='val-sub'>N/mm²</span>", unsafe_allow_html=True)
        st.latex(rf"\sigma_{{c,0,d}} = \frac{{N_d}}{{A}} = \frac{{{N_d_kN:.1f} \times 10^3}}"
                 rf"{{{A_mm2}}} = {sigma_c_0_d:.2f}\ \mathrm{{N/mm^2}}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='envelope-card'>", unsafe_allow_html=True)
        st.markdown("<div class='title-main'>Resistencia Reducida por Pandeo</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<span class='val-highlight'>{f_c_buck:.2f}</span> "
                    f"<span class='val-sub'>N/mm²</span>", unsafe_allow_html=True)
        st.latex(rf"k_c \cdot f_{{c,0,d}} = {kc_min:.4f} \times {f_c_0_d:.2f} = {f_c_buck:.2f}"
                 rf"\ \mathrm{{N/mm^2}}")
        st.markdown("</div>", unsafe_allow_html=True)

    mostrar_tarjeta_resultado(
        ratio_pandeo_puro,
        titulo=f"σ_c,0,d / (k_c · f_c,0,d) = {sigma_c_0_d:.2f} / {f_c_buck:.2f} = {ratio_pandeo_puro:.3f}",
        detalle=f"Eje crítico: {'Z (débil)' if ratio_buck_z >= ratio_buck_y else 'Y (fuerte)'}"
    )

    st.divider()

    # --- CURVA DE PANDEO ---
    st.markdown("### 📊 Curva de Pandeo EC5")
    lam_range = [i * 0.02 for i in range(151)]
    kc_mac = [calc_kc(lr, 0.2)[0] for lr in lam_range]
    kc_lam = [calc_kc(lr, 0.1)[0] for lr in lam_range]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=lam_range, y=kc_mac, mode='lines',
                             line=dict(color='#f59e0b', width=2.5, dash='dash'),
                             name='Maciza (βc=0.2)'))
    fig.add_trace(go.Scatter(x=lam_range, y=kc_lam, mode='lines',
                             line=dict(color='#2563eb', width=2.5),
                             name='Laminada (βc=0.1)'))
    fig.add_trace(go.Scatter(x=[lambda_rel_y], y=[k_c_y], mode='markers+text',
                             marker=dict(size=14, color='#dc2626', symbol='circle',
                                         line=dict(width=2, color='white')),
                             text=[f"  Y ({lambda_rel_y:.2f})"], textposition="middle right",
                             textfont=dict(size=12, color='#dc2626'), name='Eje Y'))
    fig.add_trace(go.Scatter(x=[lambda_rel_z], y=[k_c_z], mode='markers+text',
                             marker=dict(size=14, color='#7c3aed', symbol='diamond',
                                         line=dict(width=2, color='white')),
                             text=[f"  Z ({lambda_rel_z:.2f})"], textposition="middle right",
                             textfont=dict(size=12, color='#7c3aed'), name='Eje Z'))
    fig.add_vline(x=0.3, line_dash="dot", line_color="#10b981", line_width=1.5,
                  annotation_text="λ_rel=0.3", annotation_position="top left",
                  annotation_font_color="#10b981")
    fig.update_layout(xaxis_title="λ_rel", yaxis_title="k_c",
                      plot_bgcolor="white", paper_bgcolor="white",
                      xaxis=dict(showgrid=True, gridcolor="#e2e8f0", range=[0, 3]),
                      yaxis=dict(showgrid=True, gridcolor="#e2e8f0", range=[0, 1.05]),
                      margin=dict(t=30, b=40, l=50, r=30), height=400,
                      legend=dict(x=0.55, y=0.95, bgcolor="rgba(255,255,255,0.8)"))
    st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PÁGINA 3: INTERACCIÓN N + M
# =============================================================================
elif page == "⚖️ 3. Interacción N + M":
    st.title("⚖️ Interacción Compresión + Flexión")
    mostrar_resumen_global()

    with st.expander("📚 Guía: ¿Cuándo comprobar la interacción?", expanded=False):
        st.markdown("""
        Cuando un pilar recibe **momentos** además de compresión hay que verificar
        la **interacción**:

        * **Sin pandeo** ($\\lambda_{rel} \\leq 0.3$ en ambos ejes): Ec. 6.19/6.20 —
          axil **al cuadrado**, sin $k_c$.
        * **Con pandeo**: Ec. 6.23/6.24 — axil **lineal** dividido por $k_c$.

        $k_m = 0.7$ para secciones rectangulares.
        """)

    if not hay_momentos:
        st.info("💡 Sin momentos → la interacción se reduce a pandeo puro (pestaña anterior).")

    st.markdown(f"### Ecuaciones: **{eq_label}**")

    if sin_riesgo_pandeo:
        st.latex(r"\left(\frac{\sigma_{c,0,d}}{f_{c,0,d}}\right)^2 + "
                 r"\frac{\sigma_{m,y,d}}{f_{m,y,d}} + k_m \frac{\sigma_{m,z,d}}{f_{m,z,d}} \leq 1")
        st.latex(r"\left(\frac{\sigma_{c,0,d}}{f_{c,0,d}}\right)^2 + k_m "
                 r"\frac{\sigma_{m,y,d}}{f_{m,y,d}} + \frac{\sigma_{m,z,d}}{f_{m,z,d}} \leq 1")
    else:
        st.latex(r"\frac{\sigma_{c,0,d}}{k_{c,y}\,f_{c,0,d}} + "
                 r"\frac{\sigma_{m,y,d}}{f_{m,y,d}} + k_m \frac{\sigma_{m,z,d}}{f_{m,z,d}} \leq 1")
        st.latex(r"\frac{\sigma_{c,0,d}}{k_{c,z}\,f_{c,0,d}} + k_m "
                 r"\frac{\sigma_{m,y,d}}{f_{m,y,d}} + \frac{\sigma_{m,z,d}}{f_{m,z,d}} \leq 1")

    st.divider()
    st.markdown("### 🧮 Desarrollo Numérico")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Ecuación 1 (Eje Y):**")
        if sin_riesgo_pandeo:
            st.markdown(f"""<div class='math-box'>
            ({sigma_c_0_d:.2f}/{f_c_0_d:.2f})² + {sigma_m_y_d:.2f}/{f_m_y_d:.2f}
            + 0.7·{sigma_m_z_d:.2f}/{f_m_z_d:.2f}<br>
            = {tc_y:.4f} + {tm_y:.4f} + {k_m*tm_z:.4f}
            = <span class='math-res'>{ratio_int_y:.4f}</span>
            {'  ≤ 1 ✅' if ratio_int_y<=1 else '  > 1 ❌'}
            </div>""", unsafe_allow_html=True)
        else:
            dy = k_c_y * f_c_0_d
            st.markdown(f"""<div class='math-box'>
            {sigma_c_0_d:.2f}/({k_c_y:.4f}·{f_c_0_d:.2f})
            + {sigma_m_y_d:.2f}/{f_m_y_d:.2f}
            + 0.7·{sigma_m_z_d:.2f}/{f_m_z_d:.2f}<br>
            = {tc_y:.4f} + {tm_y:.4f} + {k_m*tm_z:.4f}
            = <span class='math-res'>{ratio_int_y:.4f}</span>
            {'  ≤ 1 ✅' if ratio_int_y<=1 else '  > 1 ❌'}
            </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("**Ecuación 2 (Eje Z):**")
        if sin_riesgo_pandeo:
            st.markdown(f"""<div class='math-box'>
            ({sigma_c_0_d:.2f}/{f_c_0_d:.2f})² + 0.7·{sigma_m_y_d:.2f}/{f_m_y_d:.2f}
            + {sigma_m_z_d:.2f}/{f_m_z_d:.2f}<br>
            = {tc_z:.4f} + {k_m*tm_y:.4f} + {tm_z:.4f}
            = <span class='math-res'>{ratio_int_z:.4f}</span>
            {'  ≤ 1 ✅' if ratio_int_z<=1 else '  > 1 ❌'}
            </div>""", unsafe_allow_html=True)
        else:
            dz = k_c_z * f_c_0_d
            st.markdown(f"""<div class='math-box'>
            {sigma_c_0_d:.2f}/({k_c_z:.4f}·{f_c_0_d:.2f})
            + 0.7·{sigma_m_y_d:.2f}/{f_m_y_d:.2f}
            + {sigma_m_z_d:.2f}/{f_m_z_d:.2f}<br>
            = {tc_z:.4f} + {k_m*tm_y:.4f} + {tm_z:.4f}
            = <span class='math-res'>{ratio_int_z:.4f}</span>
            {'  ≤ 1 ✅' if ratio_int_z<=1 else '  > 1 ❌'}
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### Resultado de la Interacción")
    mostrar_tarjeta_resultado(
        ratio_global,
        titulo=f"Gobernante: {'Ec.1 (Y)' if ratio_int_y>=ratio_int_z else 'Ec.2 (Z)'}",
        detalle=f"η₁ = {ratio_int_y:.3f}  |  η₂ = {ratio_int_z:.3f}  →  η_max = {ratio_global:.3f}"
    )

    # --- Barra de contribución ---
    if ratio_global > 0:
        st.markdown("### 📊 Contribución de cada esfuerzo")
        r_max = max(ratio_int_y, ratio_int_z)
        if ratio_int_y >= ratio_int_z:
            parts = [("Compresión (N)", tc_y), ("Flexión Y", tm_y), ("Flexión Z (k_m)", k_m*tm_z)]
        else:
            parts = [("Compresión (N)", tc_z), ("Flexión Y (k_m)", k_m*tm_y), ("Flexión Z", tm_z)]
        colors_bar = ["#3b82f6", "#f59e0b", "#8b5cf6"]
        fig_b = go.Figure()
        for (lb, vl), cb in zip(parts, colors_bar):
            pct = (vl / r_max * 100) if r_max > 0 else 0
            fig_b.add_trace(go.Bar(y=["η"], x=[vl], name=f"{lb}: {vl:.3f} ({pct:.0f}%)",
                                   orientation='h', marker_color=cb,
                                   text=f"{pct:.0f}%", textposition='inside',
                                   textfont=dict(color='white', size=13)))
        fig_b.add_vline(x=1.0, line_dash="dash", line_color="#dc2626", line_width=2,
                        annotation_text="Límite", annotation_position="top right")
        fig_b.update_layout(barmode='stack', height=120,
                            margin=dict(t=30, b=20, l=10, r=10),
                            xaxis=dict(range=[0, max(r_max*1.15, 1.1)],
                                       showgrid=True, gridcolor="#e2e8f0"),
                            yaxis=dict(showticklabels=False),
                            plot_bgcolor="white", paper_bgcolor="white",
                            legend=dict(orientation="h", y=-0.5, x=0))
        st.plotly_chart(fig_b, use_container_width=True)


# =============================================================================
# PÁGINA 4: FUEGO
# =============================================================================
elif page == "🔥 4. Fuego":
    st.title("🔥 Fuego: Sección Eficaz Reducida (Pilar)")
    mostrar_resumen_global()

    with st.expander("📚 Guía: El pilar en un incendio", expanded=False):
        st.markdown("""
        En un pilar, el fuego tiene **doble efecto**:
        1. Se reduce el **área** → la tensión sube.
        2. Se reduce el **radio de giro** → la esbeltez sube y $k_c$ baja.

        Método de la Sección Eficaz Reducida: $d_{ef} = d_{char,n} + k_0 \\cdot d_0$
        """)

    st.sidebar.header("🔥 Parámetros de Incendio")
    t_fuego = st.sidebar.selectbox("Tiempo t [min]", [15, 30, 45, 60, 90, 120], index=1,
                                   key="t_fire")
    num_caras = st.sidebar.selectbox("Caras expuestas", [1, 2, 3, 4], index=3, key="caras_fire")

    beta_n = 0.70 if es_laminada else 0.80
    k_fi = 1.15 if es_laminada else 1.25
    d_char_n = beta_n * t_fuego
    k_0 = min(t_fuego / 20.0, 1.0)
    d_ef = d_char_n + k_0 * 7.0

    b_fi, h_fi = float(b_mm), float(h_mm)
    if num_caras == 1:
        b_fi -= d_ef; detalle_c = "1 lateral"
    elif num_caras == 2:
        b_fi -= 2 * d_ef; detalle_c = "2 laterales"
    elif num_caras == 3:
        b_fi -= 2 * d_ef; h_fi -= d_ef; detalle_c = "2 lat + 1 inf"
    else:
        b_fi -= 2 * d_ef; h_fi -= 2 * d_ef; detalle_c = "4 caras"

    if b_fi <= 0 or h_fi <= 0:
        st.error("🔥 **SECCIÓN CONSUMIDA.** Aumenta la sección o reduce el tiempo.")
    else:
        A_fi = b_fi * h_fi
        i_y_fi = h_fi / math.sqrt(12)
        i_z_fi = b_fi / math.sqrt(12)
        lr_y_fi = ((beta_y * L_m * 1000 / i_y_fi) / math.pi) * math.sqrt(f_c_0_k / E_0_05)
        lr_z_fi = ((beta_z * L_m * 1000 / i_z_fi) / math.pi) * math.sqrt(f_c_0_k / E_0_05)
        kc_y_fi, _ = calc_kc(lr_y_fi, beta_c)
        kc_z_fi, _ = calc_kc(lr_z_fi, beta_c)
        kc_min_fi = min(kc_y_fi, kc_z_fi)

        N_fi_kN = st.sidebar.number_input("N_fi [kN] (cuasi-perm.)",
                                          value=round(N_d_kN * 0.6, 1), step=5.0,
                                          min_value=0.0, key="n_fi")
        sigma_c_fi = (N_fi_kN * 1000) / A_fi
        f_c_fi_d = k_fi * f_c_0_k  # k_mod,fi = 1.0, γ_M,fi = 1.0
        f_c_buck_fi = kc_min_fi * f_c_fi_d
        ratio_fuego = sigma_c_fi / f_c_buck_fi if f_c_buck_fi > 0 else 999

        st.markdown("### Profundidad de Carbonización")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("β_n", f"{beta_n:.2f} mm/min")
        c2.metric("d_char,n", f"{d_char_n:.1f} mm")
        c3.metric("d_ef", f"{d_ef:.1f} mm")
        c4.metric("Caras", f"{num_caras} ({detalle_c})")

        st.markdown("### Sección Reducida")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("b_fi", f"{b_fi:.0f} mm", delta=f"{b_fi-b_mm:.0f}")
        c2.metric("h_fi", f"{h_fi:.0f} mm", delta=f"{h_fi-h_mm:.0f}")
        c3.metric("A_fi", f"{A_fi:,.0f} mm²", delta=f"{(A_fi/A_mm2-1)*100:.0f}%")
        c4.metric("i_min,fi", f"{min(i_y_fi,i_z_fi):.1f} mm")

        st.markdown("### Re-cálculo de Pandeo en Incendio")
        c1, c2, c3 = st.columns(3)
        c1.metric("λ_rel,y (fuego)", f"{lr_y_fi:.3f}", delta=f"+{lr_y_fi-lambda_rel_y:.3f}")
        c2.metric("λ_rel,z (fuego)", f"{lr_z_fi:.3f}", delta=f"+{lr_z_fi-lambda_rel_z:.3f}")
        c3.metric("k_c,min (fuego)", f"{kc_min_fi:.4f}",
                   delta=f"{kc_min_fi-min(k_c_y,k_c_z):.4f}")

        st.divider()
        st.markdown("### Comprobación")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class='math-box'>
            <b>Tensión:</b> σ = N_fi / A_fi = {N_fi_kN:.1f}·10³ / {A_fi:.0f}
            = <span class='math-res'>{sigma_c_fi:.2f} N/mm²</span>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='math-box'>
            <b>Resistencia:</b> k_c · k_fi · f_c,0,k = {kc_min_fi:.4f} · {k_fi} · {f_c_0_k}
            = <span class='math-res'>{f_c_buck_fi:.2f} N/mm²</span>
            </div>""", unsafe_allow_html=True)

        mostrar_tarjeta_resultado(
            ratio_fuego,
            titulo=f"η = {sigma_c_fi:.2f} / {f_c_buck_fi:.2f} = {ratio_fuego:.3f}",
            detalle=f"R{t_fuego} – {num_caras} caras expuestas"
        )

        st.markdown(f"""
        <div class='expl-box' style='border-color:#f59e0b;background:#fffbeb;color:#854d0e;'>
        <b>Efecto doble del fuego:</b> La esbeltez ha subido de
        {max(lambda_rel_y,lambda_rel_z):.3f} a {max(lr_y_fi,lr_z_fi):.3f} y
        k<sub>c</sub> ha bajado de {min(k_c_y,k_c_z):.4f} a {kc_min_fi:.4f}.
        </div>""", unsafe_allow_html=True)


# =============================================================================
# PÁGINA 5: RESULTADOS
# =============================================================================
elif page == "📑 5. Resultados":
    st.title("📑 Resumen de Resultados")
    mostrar_resumen_global()

    # --- Fuego para resumen (4 caras, 30 min) ---
    t_res = 30
    bn_r = 0.70 if es_laminada else 0.80
    kfi_r = 1.15 if es_laminada else 1.25
    d_ef_r = (bn_r * t_res) + min(t_res / 20.0, 1.0) * 7.0
    b_fi_r = b_mm - 2 * d_ef_r
    h_fi_r = h_mm - 2 * d_ef_r
    if b_fi_r > 0 and h_fi_r > 0:
        A_fi_r = b_fi_r * h_fi_r
        i_y_r = h_fi_r / math.sqrt(12)
        i_z_r = b_fi_r / math.sqrt(12)
        lr_y_r = ((beta_y * L_m * 1000 / i_y_r) / math.pi) * math.sqrt(f_c_0_k / E_0_05)
        lr_z_r = ((beta_z * L_m * 1000 / i_z_r) / math.pi) * math.sqrt(f_c_0_k / E_0_05)
        kcy_r, _ = calc_kc(lr_y_r, beta_c)
        kcz_r, _ = calc_kc(lr_z_r, beta_c)
        kcm_r = min(kcy_r, kcz_r)
        N_fi_est = N_d_kN * 0.6
        s_fi_r = (N_fi_est * 1000) / A_fi_r
        f_fi_r = kcm_r * kfi_r * f_c_0_k
        ratio_fuego_res = s_fi_r / f_fi_r if f_fi_r > 0 else 9.99
    else:
        ratio_fuego_res = 9.99

    max_ratio = max(ratio_pandeo_puro, ratio_global, ratio_fuego_res)

    def idx_color(r):
        return '#dc2626' if r > 1 else '#47768c'

    html_res = f"""
    <style>
    .rc{{font-family:'Segoe UI',Arial,sans-serif;color:#44546a;margin-top:10px;}}
    .rmb{{background:#e6ebed;border-left:6px solid #587e91;display:flex;
    align-items:center;padding:10px 15px;margin-bottom:5px;}}
    .rmt{{font-weight:700;color:#47768c;flex-grow:1;font-size:1.15rem;
    text-transform:uppercase;letter-spacing:0.5px;}}
    .rmv{{font-weight:700;font-size:1.25rem;background:#fff;padding:2px 10px;border-radius:4px;}}
    .rd{{font-size:0.95rem;color:#5c707c;margin-bottom:25px;line-height:1.5;padding-left:5px;}}
    .rsb{{background:#f1f4f5;border-left:6px solid #8e9599;padding:6px 12px;
    margin-top:20px;display:flex;font-size:1rem;font-weight:700;color:#587e91;}}
    .rt{{width:100%;border-collapse:collapse;font-size:0.95rem;margin-bottom:10px;}}
    .rt td{{padding:10px 12px;border-bottom:1px solid #edf1f2;}}
    .rt tr:hover{{background:#f8fafc;}}
    .tn{{color:#587e91;width:50%;}}.ti{{font-weight:800;width:15%;text-align:center;}}
    .tc{{color:#7f95a3;font-size:0.9rem;}}
    </style>
    <div class="rc">
    <div class="rmb">
    <div class="rmt">Índice de aprovechamiento global</div>
    <div class="rmv" style="color:{idx_color(max_ratio)};">{max_ratio*100:.0f}%</div>
    </div>
    <div class="rd">Un índice superior al 100% implica incumplimiento.</div>

    <div class="rsb"><div style="flex-grow:1;">Comprobación</div>
    <div style="width:15%;text-align:center;font-size:0.9rem;">Índice</div>
    <div style="width:35%;font-size:0.9rem;">Detalles</div></div>
    <table class="rt">
    <tr><td class="tn">Compresión simple (sin pandeo)</td>
    <td class="ti" style="color:{idx_color(ratio_comp_simple)};">{ratio_comp_simple*100:.0f}%</td>
    <td class="tc">σ_c / f_c,0,d</td></tr>

    <tr><td class="tn">Pandeo por compresión (§6.3.2)</td>
    <td class="ti" style="color:{idx_color(ratio_pandeo_puro)};">{ratio_pandeo_puro*100:.0f}%</td>
    <td class="tc">σ_c / (k_c · f_c,0,d) — Eje {'Z' if ratio_buck_z>=ratio_buck_y else 'Y'}</td></tr>

    <tr><td class="tn">Interacción N + M</td>
    <td class="ti" style="color:{idx_color(ratio_global)};">{ratio_global*100:.0f}%</td>
    <td class="tc">{eq_label} — {eje_critico}</td></tr>

    <tr><td class="tn">Fuego R{t_res} (4 caras, N_fi≈0.6·N_d)</td>
    <td class="ti" style="color:{idx_color(ratio_fuego_res)};">{"FALLA" if ratio_fuego_res>10 else f"{ratio_fuego_res*100:.0f}%"}</td>
    <td class="tc">Pandeo con sección reducida</td></tr>
    </table>

    <div class="rsb">Datos del pilar</div>
    <table class="rt">
    <tr><td class="tn">Sección</td><td class="ti">{b_mm}×{h_mm} mm</td>
    <td class="tc">A = {A_mm2:,} mm²</td></tr>
    <tr><td class="tn">Altura / L_ef</td><td class="ti">{L_m:.2f} m</td>
    <td class="tc">β_y={beta_y:.2f}, β_z={beta_z:.2f}</td></tr>
    <tr><td class="tn">Material</td><td class="ti">{mat}</td>
    <td class="tc">CS {clase_servicio} — k_mod={k_mod} — γ_M={gamma_M}</td></tr>
    <tr><td class="tn">Axil N_d</td><td class="ti">{N_d_kN:.1f} kN</td>
    <td class="tc">σ_c,0,d = {sigma_c_0_d:.2f} N/mm²</td></tr>
    <tr><td class="tn">Momentos</td><td class="ti">M_y={M_yd_kNm:.2f} / M_z={M_zd_kNm:.2f}</td>
    <td class="tc">kN·m</td></tr>
    <tr><td class="tn">Esbelteces relativas</td><td class="ti">λ_y={lambda_rel_y:.3f} / λ_z={lambda_rel_z:.3f}</td>
    <td class="tc">k_c,y={k_c_y:.4f} / k_c,z={k_c_z:.4f}</td></tr>
    <tr><td class="tn">Carga Euler mínima</td><td class="ti">{N_cr_min:.1f} kN</td>
    <td class="tc">N_d/N_cr = {N_d_kN/N_cr_min:.3f}</td></tr>
    </table>
    </div>
    """

    st.markdown(html_res.replace('\n', ''), unsafe_allow_html=True)

    # =============================================================================
# PÁGINA 6: EJEMPLOS DIDÁCTICOS (LA NUEVA)
# =============================================================================
elif page == "📖 6. Ejemplos Didácticos":
    st.title("📖 Ejemplos Didácticos: De Menos a Más")

    st.markdown("""
    <div class="blue-box">
    Esta página contiene <b>4 niveles progresivos</b> de complejidad para entender
    qué comprueba esta herramienta y por qué. Cada nivel usa el mismo pilar base
    (GL24h, 160×160 mm) y va añadiendo dificultad.
    </div>
    """, unsafe_allow_html=True)

    MAT_EJ = "GL24h"
    B_EJ, H_EJ, CS_EJ, DUR_EJ = 160, 160, "1", "Media"
    pm_ej = MATERIALES[MAT_EJ]
    fc0k_ej = pm_ej["f_c_0_k"]
    E005_ej = pm_ej["E_0_05"]
    km_ej = KMOD_TABLA[CS_EJ][DUR_EJ]
    gM_ej = 1.25
    A_ej = B_EJ * H_EJ
    fc0d_ej = km_ej * fc0k_ej / gM_ej

    # ==========================
    # NIVEL 1: PILAR CORTITO
    # ==========================
    st.markdown("""---""")
    st.markdown("""
    <div class="nivel-card" style="background: linear-gradient(135deg, #f0fdf4, #dcfce7); border: 2px solid #86efac;">
    <div class="nivel-title" style="color: #166534;">🟢 NIVEL 1 — Pilar cortito y gordo (sin pandeo)</div>
    <p style="color:#166534;">160×160 mm · L = 0.5 m · N = 80 kN · Sin momento</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Pregunta:** *¿Se aplasta la madera?*")

    N1 = 80; L1 = 0.5
    r1 = ejemplo_pilar(B_EJ, H_EJ, L1, N1, 0, 0, 1.0, 1.0, MAT_EJ, CS_EJ, DUR_EJ)

    c1, c2, c3 = st.columns(3)
    c1.metric("σ_c (tensión)", f"{r1['sc']:.2f} N/mm²")
    c2.metric("f_c,0,d (resistencia)", f"{r1['fc0d']:.2f} N/mm²")
    c3.metric("η (aprovechamiento)", f"{r1['ratio']:.2f}")

    st.markdown(f"""
    <div class='math-box'>
    σ = N / A = {N1}·10³ / {A_ej:,} = <span class='math-res'>{r1['sc']:.2f} N/mm²</span><br><br>
    f_c,0,d = k_mod · f_c,0,k / γ_M = {km_ej} × {fc0k_ej} / {gM_ej} = <span class='math-res'>{fc0d_ej:.2f} N/mm²</span><br><br>
    λ_rel = {r1['lr_y']:.3f} ≤ 0.3 → <span class='math-res'>SIN PANDEO</span> → k_c = 1.0<br><br>
    η = ({r1['sc']:.2f} / {fc0d_ej:.2f})² = <span class='math-res'>{r1['ratio']:.3f} ✅</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='expl-box'>
    <b>Conclusión:</b> El pilar es tan corto y gordo que no tiene ningún riesgo de pandeo.
    Solo comprobamos que la madera no se aplaste. Con η = 0.04 (4%), sobra el 96% de la capacidad.
    </div>
    """, unsafe_allow_html=True)

    # ==========================
    # NIVEL 2: PILAR ESBELTO
    # ==========================
    st.markdown("""---""")
    st.markdown("""
    <div class="nivel-card" style="background: linear-gradient(135deg, #fefce8, #fef08a); border: 2px solid #facc15;">
    <div class="nivel-title" style="color: #854d0e;">🟡 NIVEL 2 — El mismo pilar, pero alto (pandeo)</div>
    <p style="color:#854d0e;">160×160 mm · N = 80 kN · Sin momento · Altura variable</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Pregunta:** *¿Se dobla antes de aplastarse?*")

    alturas = [0.5, 1.5, 3.0, 5.0, 6.5, 8.0]
    filas_tabla = []
    for Lx in alturas:
        rx = ejemplo_pilar(B_EJ, H_EJ, Lx, N1, 0, 0, 1.0, 1.0, MAT_EJ, CS_EJ, DUR_EJ)
        filas_tabla.append({
            "Altura": f"{Lx} m",
            "λ_rel": f"{rx['lr_y']:.3f}",
            "k_c": f"{rx['kc_min']:.3f}",
            "Resist. útil": f"{rx['kc_min']*fc0d_ej:.2f} N/mm²",
            "η": f"{rx['ratio']:.3f}",
            "Estado": "✅" if rx['ratio'] <= 1.0 else "❌ ¡PANDEA!",
        })

    import pandas as pd
    df_alturas = pd.DataFrame(filas_tabla)
    st.dataframe(df_alturas, use_container_width=True, hide_index=True)

    st.markdown(f"""
    <div class='expl-box'>
    <b>Observa:</b> La tensión σ = {r1['sc']:.2f} N/mm² <b>no cambia</b> al subir la altura.
    Lo que cambia es cuánto de la resistencia puedes usar: k<sub>c</sub> baja y la resistencia
    útil cae. A 8 m, el pilar pandea con solo 80 kN.
    </div>
    """, unsafe_allow_html=True)

    # Gráfica
    etas = []
    Ls = [i*0.1 for i in range(5, 101)]
    for Lx in Ls:
        rx = ejemplo_pilar(B_EJ, H_EJ, Lx, N1, 0, 0, 1.0, 1.0, MAT_EJ, CS_EJ, DUR_EJ)
        etas.append(rx['ratio'])

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=Ls, y=etas, mode='lines', line=dict(color='#2563eb', width=3),
                              name='η (aprovechamiento)'))
    fig2.add_hline(y=1.0, line_dash="dash", line_color="#dc2626", line_width=2,
                   annotation_text="LÍMITE η = 1.0")
    fig2.update_layout(xaxis_title="Altura del pilar (m)", yaxis_title="η (aprovechamiento)",
                       plot_bgcolor="white", height=350, margin=dict(t=30,b=40),
                       xaxis=dict(showgrid=True, gridcolor="#e2e8f0"),
                       yaxis=dict(showgrid=True, gridcolor="#e2e8f0"))
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("La altura a la que η = 1.0 es la altura máxima que aguanta este pilar con 80 kN.")

    # ==========================
    # NIVEL 3: CON MOMENTO
    # ==========================
    st.markdown("""---""")
    st.markdown("""
    <div class="nivel-card" style="background: linear-gradient(135deg, #fff7ed, #fed7aa); border: 2px solid #f97316;">
    <div class="nivel-title" style="color: #9a3412;">🟠 NIVEL 3 — Pilar con momento (viento o excentricidad)</div>
    <p style="color:#9a3412;">160×160 mm · L = 3.0 m · N = 80 kN · M_y variable</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Pregunta:** *¿Aguanta el peso Y el empujón lateral a la vez?*")

    momentos = [0, 1, 2, 4, 6, 8]
    filas_M = []
    for Mx in momentos:
        rx = ejemplo_pilar(B_EJ, H_EJ, 3.0, N1, Mx, 0, 1.0, 1.0, MAT_EJ, CS_EJ, DUR_EJ)
        filas_M.append({
            "M_y": f"{Mx} kN·m",
            "η_compresión": f"{rx['tc']:.3f}",
            "η_flexión": f"{rx['tmy']:.3f}",
            "η_TOTAL": f"{rx['ratio']:.3f}",
            "Compresión": f"{rx['tc']/rx['ratio']*100:.0f}%" if rx['ratio'] > 0 else "—",
            "Flexión": f"{rx['tmy']/rx['ratio']*100:.0f}%" if rx['ratio'] > 0 else "—",
            "Estado": "✅" if rx['ratio'] <= 1.0 else "❌",
        })

    df_M = pd.DataFrame(filas_M)
    st.dataframe(df_M, use_container_width=True, hide_index=True)

    r3 = ejemplo_pilar(B_EJ, H_EJ, 3.0, N1, 2, 0, 1.0, 1.0, MAT_EJ, CS_EJ, DUR_EJ)
    st.markdown(f"""
    <div class='math-box'>
    <b>Ejemplo con M_y = 2 kN·m:</b><br><br>
    Parte de compresión: σ_c / (k_c · f_c,0,d) = {r3['sc']:.2f} / ({r3['kc_min']:.3f} × {fc0d_ej:.2f}) = <span class='math-res'>{r3['tc']:.3f}</span><br><br>
    Parte de flexión: σ_m / f_m,d = {r3['smy']:.2f} / {r3['fmyd']:.2f} = <span class='math-res'>{r3['tmy']:.3f}</span><br><br>
    TOTAL: {r3['tc']:.3f} + {r3['tmy']:.3f} = <span class='math-res'>{r3['ratio']:.3f} ✅</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='expl-box'>
    <b>Conclusión:</b> Sin momento, el pilar está al 28%. Con 2 kN·m de momento sube al 46%.
    Con 8 kN·m ya no cumple. <b>La compresión y la flexión se suman</b>: cada una "gasta"
    parte de la capacidad del pilar.
    </div>
    """, unsafe_allow_html=True)

    # ==========================
    # NIVEL 4: FUEGO
    # ==========================
    st.markdown("""---""")
    st.markdown("""
    <div class="nivel-card" style="background: linear-gradient(135deg, #fef2f2, #fecaca); border: 2px solid #ef4444;">
    <div class="nivel-title" style="color: #991b1b;">🔴 NIVEL 4 — Fuego (lo más duro)</div>
    <p style="color:#991b1b;">160×160 mm · L = 3.0 m · 4 caras · GL24h · β_n = 0.70</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Pregunta:** *¿El palillo que queda tras quemarse sigue en pie?*")

    tiempos = [0, 15, 30, 45, 60]
    filas_F = []
    for t in tiempos:
        if t == 0:
            filas_F.append({"Tiempo": "0 (original)", "d_ef": "0 mm",
                           "b_fi×h_fi": f"{B_EJ}×{H_EJ}", "A_fi": f"{A_ej:,}",
                           "λ_rel": f"{r1['lr_y']:.3f}" if L1==0.5 else "—",
                           "k_c": "1.000", "η": "—", "Estado": "—"})
            continue
        d_ef_t = (0.70 * t) + min(t/20,1)*7
        bf = B_EJ - 2*d_ef_t
        hf = H_EJ - 2*d_ef_t
        if bf <= 0 or hf <= 0:
            filas_F.append({"Tiempo": f"{t} min", "d_ef": f"{d_ef_t:.0f} mm",
                           "b_fi×h_fi": "CONSUMIDO", "A_fi": "0",
                           "λ_rel": "—", "k_c": "—", "η": "—", "Estado": "🔥 COLAPSO"})
            continue
        Af = bf * hf
        iy_f = hf / math.sqrt(12)
        lr_f = ((1.0*3000/iy_f)/math.pi)*math.sqrt(fc0k_ej/E005_ej)
        kcf, _ = calc_kc(lr_f, 0.1)
        Nfi = 80 * 0.6
        sf = (Nfi*1000)/Af
        ff = kcf * 1.15 * fc0k_ej
        rf = sf / ff if ff > 0 else 999
        filas_F.append({
            "Tiempo": f"{t} min", "d_ef": f"{d_ef_t:.0f} mm",
            "b_fi×h_fi": f"{bf:.0f}×{hf:.0f}", "A_fi": f"{Af:,.0f}",
            "λ_rel": f"{lr_f:.3f}", "k_c": f"{kcf:.3f}",
            "η": f"{rf:.3f}", "Estado": "✅" if rf <= 1 else "❌"
        })

    df_F = pd.DataFrame(filas_F)
    st.dataframe(df_F, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class='math-box'>
    <b>Ejemplo a 30 minutos (4 caras):</b><br><br>
    d_ef = 0.70 × 30 + 7 = 28 mm (carbón + madera caliente)<br><br>
    Sección: 160 − 2×28 = 104 mm → 104×104 = 10,816 mm² <span style="color:#f59e0b;">(−58% del área)</span><br><br>
    N_fi = 0.6 × 80 = 48 kN (carga reducida en incendio)<br>
    σ = 48,000 / 10,816 = 4.44 N/mm²<br><br>
    λ_rel sube de 1.034 a 1.591 → k_c baja de 0.741 a 0.354 <span style="color:#ef4444;">(¡doble golpe!)</span><br><br>
    f_buck = 0.354 × 1.15 × 24 = 9.77 N/mm²<br>
    η = 4.44 / 9.77 = <span class='math-res'>0.454 ✅</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='expl-box' style='border-color:#ef4444; background:#fef2f2; color:#991b1b;'>
    <b>El doble golpe del fuego en un pilar:</b><br>
    1. Se reduce el <b>área</b> → la tensión sube.<br>
    2. Se reduce el <b>radio de giro</b> → el pilar es más esbelto → k_c baja → la resistencia
    útil cae aún más.<br><br>
    Un pilar es <b>mucho más sensible</b> al fuego que una viga, porque la viga solo pierde
    resistencia a flexión, pero el pilar pierde resistencia Y estabilidad al mismo tiempo.
    </div>
    """, unsafe_allow_html=True)

    # ==========================
    # RESUMEN ESQUEMÁTICO
    # ==========================
    st.markdown("""---""")
    st.markdown("### 🗺️ Mapa Mental: ¿Qué comprueba cada cosa?")
    st.markdown("""
    | Nivel | Comprobación | Pregunta | Fórmula clave |
    |-------|-------------|----------|---------------|
    | 🟢 1 | Compresión simple | ¿Se aplasta? | σ ≤ f_c,0,d |
    | 🟡 2 | Pandeo | ¿Se dobla? | σ ≤ **k_c** · f_c,0,d |
    | 🟠 3 | Interacción N+M | ¿Aguanta peso + empujón? | σ_c/(k_c·f) + σ_m/f_m ≤ 1 |
    | 🔴 4 | Fuego | ¿El palillo que queda aguanta? | Todo recalculado con sección reducida |
    """)

    st.markdown("""
    ### 🔑 Glosario rápido

    | Símbolo | Qué es | Traducción |
    |---------|--------|------------|
    | σ_c | Tensión de compresión | "Cuánto sufre la madera" |
    | f_c,0,d | Resistencia de cálculo | "Cuánto aguanta" |
    | k_c | Factor de pandeo | "Cuánto pierdo por ser esbelto" (1.0 = nada, 0.3 = mucho) |
    | λ_rel | Esbeltez relativa | "¿Soy un tocón (< 0.3) o un espagueti (> 1.0)?" |
    | β | Coef. longitud eficaz | "¿Cómo me sujetan arriba y abajo?" |
    | k_mod | Factor de duración | "La madera aguanta menos si la cargo mucho tiempo" |
    | γ_M | Coef. de seguridad | "No me fío al 100% del material" |
    | β_c | Imperfección | "¿Tiene nudos (0.2) o es laminada (0.1)?" |
    | η | Aprovechamiento | "¿Cuánto de la capacidad he gastado?" (> 1.0 = fallo) |
    """)