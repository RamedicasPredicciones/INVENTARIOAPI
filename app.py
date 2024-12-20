import streamlit as st
from app_inventario import cargar_inventario_y_completar
from app_faltantes import procesar_faltantes
import pandas as pd

# URL de la plantilla para faltantes
PLANTILLA_URL = "https://docs.google.com/spreadsheets/d/1CPMBfCiuXq2_l8KY68HgexD-kyNVJ2Ml/export?format=xlsx"

# Configuración inicial de Streamlit
st.set_page_config(page_title="RAMEDICAS - Generador de Alternativas", layout="wide")

# URL del fondo
FONDO_URL = "https://drive.google.com/uc?id=12bErHbEtceFn_JvSxwvnxKPUUH7YZykC"

# CSS para el fondo
st.markdown(
    f"""
    <style>
        body {{
            background-image: url("{FONDO_URL}");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
        }}
    </style>
    """, unsafe_allow_html=True
)

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
    </div>
    """,
    unsafe_allow_html=True
)

# Botón para recargar inventario
if st.button("Recargar Inventario"):
    st.spinner("Recargando inventario...")
    inventario = cargar_inventario_y_completar()
    if inventario is not None:
        st.success("Inventario recargado correctamente.")
    else:
        st.error("Error al recargar el inventario.")

# Subir archivo de faltantes
st.header("Carga de Archivos")
faltantes_file = st.file_uploader("Sube el archivo de faltantes (.xlsx)", type=["xlsx"])

# Cargar inventario desde la API
st.subheader("Cargando inventario...")
inventario = cargar_inventario_y_completar()

if inventario is not None:
    st.success("Inventario cargado correctamente.")
else:
    st.error("Error al cargar el inventario. Intente nuevamente.")
    st.stop()

# Filtrar bodegas disponibles
bodegas_disponibles = inventario['bodega'].unique().tolist()

# Filtro para seleccionar bodegas
bodega_seleccionada = st.multiselect("Selecciona la bodega", options=bodegas_disponibles, default=[])

# Filtrar opciones disponibles
inventario['opcion'] = pd.to_numeric(inventario['opcion'], errors='coerce').fillna(0).astype(int)
opciones_disponibles = sorted(inventario[inventario['opcion'] >= 1]['opcion'].unique())
opcion_seleccionada = st.selectbox("Selecciona una opción", options=opciones_disponibles)

# Inicializar almacenamiento de resultados
if "resultados" not in st.session_state:
    st.session_state.resultados = pd.DataFrame()

if faltantes_file and opcion_seleccionada:
    with st.spinner(f"Procesando faltantes para opción {opcion_seleccionada}..."):
        # Leer archivo de faltantes
        faltantes_df = pd.read_excel(faltantes_file)

        # Procesar faltantes
        nuevas_alternativas = procesar_faltantes(
            faltantes_df, 
            inventario[inventario['opcion'] == opcion_seleccionada], 
            columnas_adicionales=['nombre', 'laboratorio', 'presentacion'], 
            bodega_seleccionada=bodega_seleccionada
        )

        # Combinar nuevas alternativas con resultados previos
        if not nuevas_alternativas.empty:
            st.session_state.resultados = pd.concat([st.session_state.resultados, nuevas_alternativas]).drop_duplicates()

        # Mostrar resultados acumulados
        st.write("Resultados acumulados:")
        st.dataframe(st.session_state.resultados)

        # Botón para seguir buscando
        if st.button("Seguir buscando opciones"):
            st.experimental_rerun()

# Botón para descargar archivo final
if not st.session_state.resultados.empty:
    st.header("Descargar todas las alternativas")
    
    @st.cache_data
    def convertir_a_excel(df):
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Alternativas")
        processed_data = output.getvalue()
        return processed_data

    alternativas_excel = convertir_a_excel(st.session_state.resultados)
    st.download_button(
        label="Descargar archivo de alternativas",
        data=alternativas_excel,
        file_name="todas_las_alternativas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
