import streamlit as st
from app_inventario import cargar_inventario
from app_faltantes import procesar_faltantes
import pandas as pd

# URL de la plantilla para faltantes
PLANTILLA_URL = "https://docs.google.com/spreadsheets/d/1CPMBfCiuXq2_l8KY68HgexD-kyNVJ2Ml/export?format=xlsx"

# Configuración inicial de Streamlit
st.set_page_config(page_title="RAMEDICAS - Generador de Alternativas", layout="wide")

# Título e introducción
st.markdown(
    """
    <h1 style="text-align: center; color: #FF5800; font-family: Arial, sans-serif;">
        RAMEDICAS S.A.S.
    </h1>
    <h3 style="text-align: center; font-family: Arial, sans-serif; color: #3A86FF;">
        Generador de Alternativas para Faltantes
    </h3>
    <p style="text-align: center; font-family: Arial, sans-serif; color: #6B6B6B;">
        Esta herramienta te permite buscar el código alternativa para cada faltante de los pedidos en Ramédicas con su respectivo inventario actual.
    </p>
    """, unsafe_allow_html=True
)

# Botones principales
st.markdown(
    f"""
    <div style="display: flex; flex-direction: row; align-items: center; gap: 10px; margin-top: 20px;">
        <a href="{PLANTILLA_URL}" download>
            <button style="background-color: #FF5800; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer;">
                Descargar plantilla de faltantes
            </button>
        </a>
        <button onclick="window.location.reload()" style="background-color: #3A86FF; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer;">
            Actualizar inventario
        </button>
    </div>
    """,
    unsafe_allow_html=True
)

# Subir archivo de faltantes
st.header("Carga de Archivos")
faltantes_file = st.file_uploader("Sube el archivo de faltantes (.xlsx)", type=["xlsx"])

# Cargar el inventario desde la API
st.header("Cargando Inventario...")
with st.spinner("Obteniendo datos de inventario desde la API..."):
    inventario = cargar_inventario()

if faltantes_file:
    with st.spinner("Procesando archivos..."):
        # Leer el archivo de faltantes cargado
        faltantes_df = pd.read_excel(faltantes_file)
        
        # Mostrar las columnas cargadas para depuración
        st.write("Columnas del archivo de faltantes cargado:", list(faltantes_df.columns))
        
        # Normalizar columnas
        faltantes_df.columns = faltantes_df.columns.str.lower().str.strip()
        
        # Verificar que las columnas necesarias estén presentes
        columnas_necesarias = {'cur', 'codart', 'faltante', 'embalaje'}
        if not columnas_necesarias.issubset(faltantes_df.columns):
            st.error(
                f"El archivo de faltantes debe contener las columnas: {', '.join(columnas_necesarias)}. "
                f"Las columnas detectadas fueron: {', '.join(faltantes_df.columns)}."
            )
        else:
            # Si las columnas están presentes, proceder con el procesamiento
            if inventario is not None:
                alternativas = procesar_faltantes(
                    faltantes_df,
                    inventario,
                    columnas_adicionales=['nombre', 'laboratorio', 'presentacion'],
                    bodega_seleccionada=None,
                )
                
                st.success("¡Alternativas generadas exitosamente!")
                st.write("Aquí tienes las alternativas generadas:")
                st.dataframe(alternativas)
                
                # Botón para descargar el archivo de alternativas
                st.header("Descargar Alternativas")
                
                @st.cache_data
                def convertir_a_excel(df):
                    import io
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Alternativas")
                    processed_data = output.getvalue()
                    return processed_data

                alternativas_excel = convertir_a_excel(alternativas)
                st.download_button(
                    label="Descargar archivo de alternativas",
                    data=alternativas_excel,
                    file_name="alternativas_generadas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                st.error("No se pudo cargar el inventario. Por favor, intente de nuevo.")
