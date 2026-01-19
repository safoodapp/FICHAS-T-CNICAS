import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="SAFOOD - Sistema Integral", layout="wide")

# URL de tu Google Sheets (Asegúrate de que sea la correcta)
url = "https://docs.google.com/spreadsheets/d/1O93UAtI-Xq7PofX5S7u-m_E-XG58uHqK8YlMvL1x-7M/edit?usp=sharing"

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN PARA CARGAR DATOS ---
def load_data():
    ing = conn.read(spreadsheet=url, worksheet="INGREDIENTES", ttl="0")
    rec = conn.read(spreadsheet=url, worksheet="RECETAS", ttl="0")
    cli = conn.read(spreadsheet=url, worksheet="CLIENTES", ttl="0")
    return ing, rec, cli

try:
    df_ing, df_rec, df_cli = load_data()

    st.title("🚀 SAFOOD - Centro de Control")

    menu = st.sidebar.radio("Menú", ["Gestionar Clientes e Ingredientes", "Calculadora de Recetas (FT)"])

    # --- SECCIÓN 1: GESTIÓN DE DATOS ---
    if menu == "Gestionar Clientes e Ingredientes":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Clientes")
            st.dataframe(df_cli, use_container_width=True)
            with st.expander("Añadir Cliente"):
                new_cli_id = st.text_input("ID Cliente (ej: LINA)")
                new_cli_nom = st.text_input("Nombre del Cliente")
                if st.button("Guardar Cliente"):
                    new_row = pd.DataFrame([{"ID_Cliente": new_cli_id, "Nombre_Cliente": new_cli_nom}])
                    df_updated = pd.concat([df_cli, new_row], ignore_index=True)
                    conn.update(spreadsheet=url, worksheet="CLIENTES", data=df_updated)
                    st.success("Cliente guardado. ¡Refresca la página!")

        with col2:
            st.subheader("🍎 Ingredientes")
            cli_sel = st.selectbox("Cliente para el ingrediente", df_cli['Nombre_Cliente'].unique())
            id_cli_ing = df_cli[df_cli['Nombre_Cliente'] == cli_sel]['ID_Cliente'].values[0]
            
            with st.form("form_ing"):
                nom_ing = st.text_input("Nombre Ingrediente")
                desglose = st.text_area("Desglose Legal")
                c1, c2, c3 = st.columns(3)
                kcal = c1.number_input("Kcal", 0.0)
                prot = c2.number_input("Prot", 0.0)
                grasa = c3.number_input("Grasa", 0.0)
                if st.form_submit_button("Añadir Ingrediente al Excel"):
                    new_ing = pd.DataFrame([{
                        "ID_Cliente": id_cli_ing, "Nombre_Ingrediente": nom_ing, 
                        "Desglose_Legal": desglose, "Kcal": kcal, "Prot": prot, "Grasas": grasa
                    }])
                    df_up_ing = pd.concat([df_ing, new_ing], ignore_index=True)
                    conn.update(spreadsheet=url, worksheet="INGREDIENTES", data=df_up_ing)
                    st.success("Ingrediente añadido")

    # --- SECCIÓN 2: CALCULADORA Y FT ---
    else:
        st.subheader("🧪 Calculadora de Fichas Técnicas")
        cliente_sel = st.selectbox("Selecciona Cliente", df_cli['Nombre_Cliente'].unique())
        id_cli = df_cli[df_cli['Nombre_Cliente'] == cliente_sel]['ID_Cliente'].values[0]
        
        # Filtrar recetas de este cliente
        recetas_cli = df_rec[df_rec['ID_Cliente'] == id_cli]
        
        if not recetas_cli.empty:
            prod_sel = st.selectbox("Selecciona Receta", recetas_cli['Nombre_Producto'].unique())
            
            # Cálculo de Porcentajes y Nutrición
            datos = recetas_cli[recetas_cli['Nombre_Producto'] == prod_sel]
            ing_info = df_ing[df_ing['ID_Cliente'] == id_cli]
            
            df_ft = pd.merge(datos, ing_info, left_on="Ingrediente", right_on="Nombre_Ingrediente")
            total = df_ft['Gramos'].sum()
            df_ft = df_ft.sort_values(by="Gramos", ascending=False)
            
            # Listado 1169
            st.markdown("### 📝 Listado de Ingredientes (Ordenado)")
            lista_txt = []
            for _, r in df_ft.iterrows():
                pct = (r['Gramos'] / total) * 100
                # Si el ingrediente está en el nombre, ponemos el %
                base_nom = r['Nombre_Ingrediente']
                if base_nom.lower() in prod_sel.lower():
                    base_nom = f"**{base_nom} ({pct:.1f}%)**"
                
                if pd.notna(r['Desglose_Legal']):
                    base_nom += f" ({r['Desglose_Legal']})"
                lista_txt.append(base_nom)
            st.write(", ".join(lista_txt))
            
            # Tabla Nutricional
            st.markdown("### 📊 Nutricionales por 100g")
            nutri = {"Kcal": (df_ft['Kcal']*df_ft['Gramos']).sum()/total}
            st.table(pd.DataFrame([nutri]))
        else:
            st.warning("Este cliente no tiene recetas registradas.")

except Exception as e:
    st.error(f"Error crítico de conexión: {e}")
    st.info("Revisa que las pestañas se llamen: CLIENTES, INGREDIENTES y RECETAS.")
