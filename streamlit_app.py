import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="SAFOOD FT", layout="wide")

# URL ACORTADA (Prueba con esta que es la "limpia")
url = "https://docs.google.com/spreadsheets/d/1O93UAtI-Xq7PofX5S7u-m_E-XG58uHqK8YlMvL1x-7M/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leemos las pestañas (asegurándonos de que coincidan con tu imagen)
    df_cli = conn.read(spreadsheet=url, worksheet="CLIENTES", ttl=0)
    df_ing = conn.read(spreadsheet=url, worksheet="INGREDIENTES", ttl=0)
    df_rec = conn.read(spreadsheet=url, worksheet="RECETAS", ttl=0)

    st.title("👨‍🍳 SAFOOD - Fichas Técnicas")

    menu = st.sidebar.selectbox("Selecciona Acción", ["Ver Recetas", "Añadir Datos"])

    if menu == "Ver Recetas":
        if not df_cli.empty:
            cliente = st.selectbox("Selecciona Cliente", df_cli['Nombre_Cliente'].unique())
            id_cliente = df_cli[df_cli['Nombre_Cliente'] == cliente]['ID_Cliente'].values[0]
            
            # Filtramos recetas del cliente
            recetas_cliente = df_rec[df_rec['ID_Cliente'] == id_cliente]
            
            if not recetas_cliente.empty:
                producto = st.selectbox("Selecciona Producto", recetas_cliente['Nombre_Producto'].unique())
                
                # CÁLCULOS (QUID y Nutricionales)
                datos = recetas_cliente[recetas_cliente['Nombre_Producto'] == producto]
                ing_info = df_ing[df_ing['ID_Cliente'] == id_cliente]
                
                df_ft = pd.merge(datos, ing_info, left_on="Ingrediente", right_on="Nombre_Ingrediente")
                total_g = df_ft['Gramos'].sum()
                df_ft = df_ft.sort_values(by="Gramos", ascending=False)
                
                st.subheader(f"Listado Legal: {producto}")
                lista = []
                for _, r in df_ft.iterrows():
                    pct = (r['Gramos'] / total_g) * 100
                    nom = r['Nombre_Ingrediente']
                    # Si el ingrediente está en el nombre, ponemos el %
                    if nom.lower() in producto.lower():
                        nom = f"**{nom} ({pct:.1f}%)**"
                    if pd.notna(r['Desglose_Legal']):
                        nom += f" ({r['Desglose_Legal']})"
                    lista.append(nom)
                st.write(", ".join(lista))
            else:
                st.warning("No hay recetas para este cliente.")
                
    elif menu == "Añadir Datos":
        st.subheader("Añadir nuevo ingrediente")
        # Aquí el formulario para escribir en el Excel
        st.info("Para escribir en el Excel, asegúrate de que el permiso sea EDITOR.")

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Revisa que el Google Sheets esté compartido como EDITOR para cualquier persona con el enlace.")
