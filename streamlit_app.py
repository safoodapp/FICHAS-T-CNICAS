import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="SAFOOD - Edición Pro", layout="wide")

url = "https://docs.google.com/spreadsheets/d/1O93UAtI-Xq7PofX5S7u-m_E-XG58uHqK8YlMvL1x-7M/edit?usp=sharing"

# CONEXIÓN PARA EDICIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

# Formulario para añadir ingredientes directamente
with st.expander("➕ Añadir Nuevo Ingrediente"):
    with st.form("nuevo_ing"):
        nombre = st.text_input("Nombre del Ingrediente")
        kcal = st.number_input("Kcal", min_value=0.0)
        desglose = st.text_area("Desglose Legal")
        
        if st.form_submit_button("Guardar en Excel"):
            # Aquí la app intentará escribir en el Excel
            st.success(f"Guardando {nombre}...")
            # Lógica de actualización:
            # conn.update(spreadsheet=url, data=...) 

# Lectura de datos
df_ing = conn.read(spreadsheet=url, worksheet="INGREDIENTES")
st.write("Datos actuales:", df_ing)
