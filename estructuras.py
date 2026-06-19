"""
=============================================================
  MÓDULO: estructuras.py
  Biblioteca de cálculos - Estructuras y Resistencia de Materiales
  Autor: [Tu nombre]
  Versión: 1.0
=============================================================

CÓMO USAR ESTE MÓDULO:
  En tu script Python, escribí al principio:
    from estructuras import seccion_rectangular, tension_normal, ...

  O importá todo:
    import estructuras
    estructuras.tension_normal(F=1000, A=50)
"""

import math


# =============================================================
# 1. PROPIEDADES GEOMÉTRICAS DE SECCIONES TRANSVERSALES
# =============================================================

def seccion_rectangular(b, h):
    """
    Calcula las propiedades de una sección rectangular.

    Parámetros:
        b (float): Ancho de la sección [mm, cm, m — la unidad que uses]
        h (float): Alto de la sección [misma unidad que b]

    Retorna:
        dict con: Area, Momento de Inercia Ix e Iy, Módulo resistente Wx e Wy

    Ejemplo:
        seccion_rectangular(b=200, h=400)  → sección de 200x400 mm
    """
    A   = b * h
    Ix  = (b * h**3) / 12      # Inercia respecto al eje X (horizontal)
    Iy  = (h * b**3) / 12      # Inercia respecto al eje Y (vertical)
    Wx  = Ix / (h / 2)         # Módulo resistente respecto a X
    Wy  = Iy / (b / 2)         # Módulo resistente respecto a Y

    return {
        "Sección": "Rectangular",
        "b": b,
        "h": h,
        "A":  round(A,  4),
        "Ix": round(Ix, 4),
        "Iy": round(Iy, 4),
        "Wx": round(Wx, 4),
        "Wy": round(Wy, 4),
    }


def seccion_circular(d):
    """
    Calcula las propiedades de una sección circular sólida.

    Parámetros:
        d (float): Diámetro [mm, cm, m]

    Ejemplo:
        seccion_circular(d=150)  → sección circular de Ø150 mm
    """
    r  = d / 2
    A  = math.pi * r**2
    I  = (math.pi * d**4) / 64   # Inercia (igual en X e Y por simetría)
    W  = I / r                   # Módulo resistente

    return {
        "Sección": "Circular",
        "d": d,
        "A": round(A, 4),
        "I": round(I, 4),
        "W": round(W, 4),
    }


def seccion_tubular(D, e):
    """
    Calcula las propiedades de una sección circular hueca (tubo).

    Parámetros:
        D (float): Diámetro exterior [mm]
        e (float): Espesor de pared  [mm]

    Ejemplo:
        seccion_tubular(D=168.3, e=8)  → tubo 168.3 x 8 mm
    """
    d  = D - 2 * e              # Diámetro interior
    A  = (math.pi / 4) * (D**2 - d**2)
    I  = (math.pi / 64) * (D**4 - d**4)
    W  = I / (D / 2)

    return {
        "Sección": "Tubular",
        "D_ext": D,
        "D_int": round(d, 4),
        "e": e,
        "A": round(A, 4),
        "I": round(I, 4),
        "W": round(W, 4),
    }


# =============================================================
# 2. TENSIONES INTERNAS
# =============================================================

def tension_normal(N, A):
    """
    Tensión normal por carga axial (tracción o compresión).

    Fórmula:  σ = N / A

    Parámetros:
        N (float): Fuerza axial  [N, kN — la unidad que uses]
        A (float): Área de la sección [mm², cm², m²]

    Ejemplo:
        tension_normal(N=50000, A=2500)  → σ en N/mm² (MPa)
    """
    sigma = N / A
    return {
        "N": N,
        "A": A,
        "sigma (σ)": round(sigma, 4),
    }


def tension_flexion(M, W):
    """
    Tensión normal por flexión (fibra extrema).

    Fórmula:  σ = M / W

    Parámetros:
        M (float): Momento flector [N·mm, kN·m — la unidad que uses]
        W (float): Módulo resistente de la sección [mm³, cm³]

    Ejemplo:
        tension_flexion(M=12e6, W=10666.67)
    """
    sigma = M / W
    return {
        "M": M,
        "W": W,
        "sigma (σ)": round(sigma, 4),
    }


def tension_combinada(N, A, M, W):
    """
    Tensión combinada = axial + flexión.

    Fórmula:  σ_max = N/A + M/W
              σ_min = N/A - M/W

    Parámetros:
        N (float): Fuerza axial
        A (float): Área de la sección
        M (float): Momento flector
        W (float): Módulo resistente

    Ejemplo:
        tension_combinada(N=10000, A=2000, M=5e6, W=8000)
    """
    sigma_axial   = N / A
    sigma_flexion = M / W
    sigma_max     = sigma_axial + sigma_flexion
    sigma_min     = sigma_axial - sigma_flexion

    return {
        "σ_axial":   round(sigma_axial,   4),
        "σ_flexión": round(sigma_flexion, 4),
        "σ_max":     round(sigma_max,     4),
        "σ_min":     round(sigma_min,     4),
    }


def tension_corte(V, Q, I, b):
    """
    Tensión de corte en una sección (fórmula de Jourawski).

    Fórmula:  τ = (V · Q) / (I · b)

    Parámetros:
        V (float): Fuerza cortante
        Q (float): Momento estático del área parcial respecto al centroide
        I (float): Momento de inercia de la sección completa
        b (float): Ancho de la sección en el punto de cálculo

    Ejemplo:
        tension_corte(V=30000, Q=120000, I=5.33e8, b=200)
    """
    tau = (V * Q) / (I * b)
    return {
        "V": V,
        "Q": Q,
        "I": I,
        "b": b,
        "tau (τ)": round(tau, 6),
    }


# =============================================================
# 3. DEFORMACIONES - VIGAS SIMPLES
# =============================================================

def flecha_viga_centro(P, L, E, I):
    """
    Flecha máxima en el centro de una viga simplemente apoyada
    con carga puntual centrada.

    Fórmula:  δ_max = P·L³ / (48·E·I)

    Parámetros:
        P (float): Carga puntual [N, kN]
        L (float): Luz de la viga [mm, m]
        E (float): Módulo de elasticidad [MPa, GPa]
        I (float): Momento de inercia [mm⁴, m⁴]

    Ejemplo (unidades SI con mm y N):
        flecha_viga_centro(P=10000, L=4000, E=210000, I=5413.3e4)
    """
    delta = (P * L**3) / (48 * E * I)
    return {
        "P": P,
        "L": L,
        "E": E,
        "I": I,
        "δ_max": round(delta, 6),
    }


def flecha_viga_carga_uniforme(q, L, E, I):
    """
    Flecha máxima en el centro de una viga simplemente apoyada
    con carga uniformemente distribuida.

    Fórmula:  δ_max = 5·q·L⁴ / (384·E·I)

    Parámetros:
        q (float): Carga distribuida [N/mm, kN/m]
        L (float): Luz de la viga
        E (float): Módulo de elasticidad
        I (float): Momento de inercia

    Ejemplo:
        flecha_viga_carga_uniforme(q=5, L=4000, E=210000, I=5413.3e4)
    """
    delta = (5 * q * L**4) / (384 * E * I)
    return {
        "q": q,
        "L": L,
        "E": E,
        "I": I,
        "δ_max": round(delta, 6),
    }


# =============================================================
# 4. MATERIALES COMUNES (módulos de elasticidad en MPa)
# =============================================================

MATERIALES = {
    "Acero estructural":   {"E": 210_000, "nu": 0.30, "fy": 250},   # S275
    "Acero S355":          {"E": 210_000, "nu": 0.30, "fy": 355},
    "Hormigón C25/30":     {"E":  31_000, "nu": 0.20, "fck": 25},
    "Hormigón C30/37":     {"E":  33_000, "nu": 0.20, "fck": 30},
    "Madera GL24h":        {"E":  11_600, "nu": 0.20, "fm": 24},
    "Aluminio":            {"E":  70_000, "nu": 0.33, "fy": 270},
}

def info_material(nombre):
    """
    Devuelve las propiedades del material seleccionado.

    Materiales disponibles:
        'Acero estructural', 'Acero S355', 'Hormigón C25/30',
        'Hormigón C30/37', 'Madera GL24h', 'Aluminio'

    Ejemplo:
        info_material('Acero S355')
    """
    if nombre in MATERIALES:
        datos = MATERIALES[nombre].copy()
        datos["Material"] = nombre
        return datos
    else:
        disponibles = list(MATERIALES.keys())
        return {"Error": f"Material no encontrado. Disponibles: {disponibles}"}


# =============================================================
# 5. UTILIDAD - IMPRIMIR RESULTADOS ORDENADOS
# =============================================================

def mostrar(titulo, resultado):
    """
    Imprime un diccionario de resultados de forma clara.

    Ejemplo:
        mostrar("Sección rectangular", seccion_rectangular(200, 400))
    """
    print(f"\n{'='*50}")
    print(f"  {titulo}")
    print(f"{'='*50}")
    for clave, valor in resultado.items():
        print(f"  {clave:<20} {valor}")
    print(f"{'='*50}\n")


# =============================================================
# ZONA DE PRUEBA — Solo se ejecuta si corrés este archivo
#                  directamente (no al importarlo)
# =============================================================

if __name__ == "__main__":

    # --- Ejemplo 1: Propiedades de sección rectangular ---
    sec = seccion_rectangular(b=200, h=400)
    mostrar("Sección Rectangular 200x400 mm", sec)

    # --- Ejemplo 2: Tensión normal axial ---
    tn = tension_normal(N=80_000, A=sec["A"])
    mostrar("Tensión Normal (N=80 kN)", tn)

    # --- Ejemplo 3: Tensión por flexión ---
    tf = tension_flexion(M=25e6, W=sec["Wx"])
    mostrar("Tensión por Flexión (M=25 kN·m)", tf)

    # --- Ejemplo 4: Flecha en viga simplemente apoyada ---
    mat = info_material("Acero estructural")
    fl = flecha_viga_centro(P=10_000, L=4_000, E=mat["E"], I=sec["Ix"])
    mostrar("Flecha máxima (viga 4m, P=10 kN centro)", fl)

    # --- Ejemplo 5: Material ---
    mostrar("Propiedades del material", mat)
