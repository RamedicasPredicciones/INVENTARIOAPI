import streamlit as st
import pandas as pd

# URL de la plantilla para faltantes
PLANTILLA_URL = "https://docs.google.com/spreadsheets/d/1CPMBfCiuXq2_l8KY68HgexD-kyNVJ2Ml/export?format=xlsx"

# Función para procesar faltantes y buscar alternativas
def procesar_faltantes(faltantes_file, inventario_file):
    # Cargar los datos
    faltantes = pd.read_excel(faltantes_file)
    inventario = pd.read_excel(inventario_file)
    
    # Calcular columna 'faltante'
    faltantes["faltante"] = faltantes["cant_pedido"] - faltantes["cant_despacho"]
    
    # Buscar alternativas basadas en 'cum'
    alternativas = pd.merge(
        faltantes, 
        inventario, 
        on="cum", 
        how="left", 
        suffixes=("_faltante", "_inventario")
    )
    
    # Seleccionar columnas relevantes
    columnas_relevantes = [
        "codart", "cum", "faltante", "nombre", "laboratorio", "presentacion", "embalaje"
    ]
    alternativas = alternativas[columnas_relevantes]
    
    return alternativas

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

# Botones de inicio
st.markdown(
    f"""
    <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 10px; margin-top: 20px;">
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

# Subir archivos de faltantes e inventario
st.header("Carga de Archivos")
faltantes_file = st.file_uploader("Sube el archivo de faltantes (.xlsx)", type=["xlsx"])
inventario_file = st.file_uploader("Sube el archivo de inventario (.xlsx)", type=["xlsx"])

# Procesar y mostrar resultados
if faltantes_file and inventario_file:
    with st.spinner("Procesando archivos..."):
        alternativas = procesar_faltantes(faltantes_file, inventario_file)
    
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

