import streamlit as st
from estructuras import seccion_rectangular, tension_normal

st.title("Calculadora Estructural Simple")

# Crear los campos de entrada en la web
st.sidebar.header("Datos de entrada")
b = st.sidebar.number_input("Ancho (mm)", value=200.0)
h = st.sidebar.number_input("Alto (mm)", value=400.0)
n = st.sidebar.number_input("Fuerza Axial (N)", value=50000.0)

# Botón de cálculo
if st.button("Calcular Propiedades"):
    # Llamamos a las funciones de tu archivo estructuras.py
    resultado_geo = seccion_rectangular(b, h)
    resultado_tens = tension_normal(n, resultado_geo["A"])
    
    # Mostramos los resultados en la web
    st.success("Resultados:")
    st.write("### Propiedades Geométricas")
    st.json(resultado_geo)
    
    st.write("### Tensión Axial")
    st.json(resultado_tens)
