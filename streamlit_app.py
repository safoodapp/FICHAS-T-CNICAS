import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="SAFOOD - Gestión de FT", layout="wide")

# URL LIMPIA
url = "https://docs.google.com/spreadsheets/d/1O93UAtI-Xq7PofX5S7u-m_E-XG58uHqK8YlMvL1x-7M/edit?usp=sharing"

# Usamos la conexión con caché para evitar bloqueos de Google
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Leer datos
    df_ing = conn.read(spreadsheet=url, worksheet="INGREDIENTES", ttl="0")
    df_rec = conn.read(spreadsheet=url, worksheet="RECETAS", ttl="0")
    df_cli = conn.read(spreadsheet=url, worksheet="CLIENTES", ttl="0")

    st.title("👨‍🍳 SAFOOD - Fichas Técnicas")

    if not df_cli.empty:
        cliente_sel = st.sidebar.selectbox("Selecciona Cliente", df_cli['Nombre_Cliente'].unique())
        id_cliente = df_cli[df_cli['Nombre_Cliente'] == cliente_sel]['ID_Cliente'].values[0]

        # Filtrar datos por cliente
        rec_cliente = df_rec[df_rec['ID_Cliente'] == id_cliente]
        ing_cliente = df_ing[df_ing['ID_Cliente'] == id_cliente]

        if not rec_cliente.empty:
            producto_sel = st.selectbox("Selecciona Producto", rec_cliente['Nombre_Producto'].unique())

            if producto_sel:
                # Filtrar receta específica
                datos_receta = rec_cliente[rec_cliente['Nombre_Producto'] == producto_sel]
                
                # Unir con ingredientes
                df_final = pd.merge(datos_receta, ing_cliente, left_on='Ingrediente', right_on='Nombre_Ingrediente')
                
                if not df_final.empty:
                    total_gramos = df_final['Gramos'].sum()
                    df_final = df_final.sort_values(by='Gramos', ascending=False)

                    # --- ETIQUETADO ---
                    st.subheader("📝 Etiquetado Legal (RD 1169)")
                    listado = []
                    for _, row in df_final.iterrows():
                        pct = (row['Gramos'] / total_gramos) * 100
                        nombre = str(row['Nombre_Ingrediente'])
                        txt = f"**{nombre} ({pct:.1f}%)**" if nombre.lower() in producto_sel.lower() else nombre
                        if pd.notna(row['Desglose_Legal']):
                            txt += f" ({row['Desglose_Legal']})"
                        listado.append(txt)
                    st.write(", ".join(listado))

                    # --- NUTRICIONALES ---
                    st.subheader("📊 Info Nutricional (por 100g)")
                    nutri_cols = ['Kcal', 'Grasas', 'Sat', 'Hidratos', 'Azucar', 'Prot', 'Sal']
                    # Limpieza de datos por si hay celdas vacías
                    for col in nutri_cols:
                        df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
                    
                    totales = {col: round((df_final[col] * df_final['Gramos']).sum() / total_gramos, 2) for col in nutri_cols}
                    st.table(pd.DataFrame([totales]))
                else:
                    st.error("Error: Los nombres de ingredientes en RECETAS no coinciden con INGREDIENTES.")
        else:
            st.info("Este cliente no tiene recetas guardadas.")
    else:
        st.warning("No se encontraron clientes en el Excel.")

except Exception as e:
    st.error("Error de conexión con el Excel.")
    st.info("Asegúrate de que el Google Sheets esté compartido como 'Cualquier persona con el enlace' en modo Lector.")
    st.write(f"Detalle técnico: {e}")
