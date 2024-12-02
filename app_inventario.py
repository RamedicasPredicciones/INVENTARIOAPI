import streamlit as st
from app_inventario import cargar_inventario_y_completar
from app_faltantes import procesar_faltantes
import pandas as pd

st.title("Generador de Alternativas para Faltantes")

# Cargar el inventario desde la API
st.subheader("Cargando Inventario")
inventario = cargar_inventario_y_completar()

if inventario is not None:
    st.success("Inventario cargado correctamente.")
else:
    st.error("No se pudo cargar el inventario. Revisa la conexión.")
    st.stop()

# Subir archivo de faltantes
st.subheader("Subir archivo de faltantes")
faltantes_file = st.file_uploader("Carga tu archivo de faltantes (formato .xlsx)", type=["xlsx"])

if faltantes_file is not None:
    faltantes_df = pd.read_excel(faltantes_file)
    alternativas = procesar_faltantes(faltantes_df, inventario, columnas_adicionales=['nombre', 'laboratorio'], bodega_seleccionada=None)
    st.success("¡Procesamiento completado!")
    st.dataframe(alternativas)

    # Botón para descargar
    @st.cache_data
    def convertir_a_excel(df):
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    excel_data = convertir_a_excel(alternativas)
    st.download_button(
        label="Descargar Alternativas",
        data=excel_data,
        file_name="alternativas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
