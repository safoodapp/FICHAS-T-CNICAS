import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="SAFOOD - Gestión de FT", layout="wide")

# URL de tu Google Sheets (la que me pasaste)
url = "https://docs.google.com/spreadsheets/d/1O93UAtI-Xq7PofX5S7u-m_E-XG58uHqK8YlMvL1x-7M/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Carga de datos
df_ing = conn.read(worksheet="INGREDIENTES")
df_rec = conn.read(worksheet="RECETAS")
df_cli = conn.read(worksheet="CLIENTES")

st.title("👨‍🍳 SAFOOD - Fichas Técnicas Inteligentes")

# 1. Filtro de Cliente
cliente_sel = st.sidebar.selectbox("Selecciona el Cliente", df_cli['Nombre_Cliente'].unique())
id_cliente = df_cli[df_cli['Nombre_Cliente'] == cliente_sel]['ID_Cliente'].values[0]

# Filtrar recetas por cliente
rec_cliente = df_rec[df_rec['ID_Cliente'] == id_cliente]

producto_sel = st.selectbox("Selecciona Producto", rec_cliente['Nombre_Producto'].unique())

if producto_sel:
    # Cruce de datos receta + ingredientes
    ing_cliente = df_ing[df_ing['ID_Cliente'] == id_cliente]
    datos_receta = rec_cliente[rec_cliente['Nombre_Producto'] == producto_sel]
    df_final = pd.merge(datos_receta, ing_cliente, left_on='Ingrediente', right_on='Nombre_Ingrediente')
    
    total_gramos = df_final['Gramos'].sum()
    df_final = df_final.sort_values(by='Gramos', ascending=False)

    # --- CÁLCULO LISTADO LEGAL ---
    st.subheader("📝 Etiquetado Legal (RD 1169)")
    listado = []
    for _, row in df_final.iterrows():
        pct = (row['Gramos'] / total_gramos) * 100
        nombre = row['Nombre_Ingrediente']
        # Si el ingrediente está en el nombre del producto, ponemos %
        if nombre.lower() in producto_sel.lower():
            txt = f"**{nombre} ({pct:.1f}%)**"
        else:
            txt = nombre
        if pd.notna(row['Desglose_Legal']):
            txt += f" ({row['Desglose_Legal']})"
        listado.append(txt)
    st.write(", ".join(listado))

    # --- CÁLCULO NUTRICIONAL REAL ---
    st.subheader("📊 Información Nutricional (por 100g)")
    nutri_cols = ['Kcal', 'Grasas', 'Sat', 'Hidratos', 'Azucar', 'Prot', 'Sal']
    totales = {}
    for col in nutri_cols:
        # Fórmula: Suma de (valor_ingrediente * gramos_ingrediente) / total_receta
        totales[col] = (df_final[col] * df_final['Gramos']).sum() / total_gramos

    st.table(pd.DataFrame([totales]))