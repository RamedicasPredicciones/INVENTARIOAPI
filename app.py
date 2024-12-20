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

# Variables globales
resultado_acumulado = pd.DataFrame()

# Botón para recargar inventario
if st.button("Recargar Inventario"):
    st.spinner("Recargando inventario...")
    inventario = cargar_inventario_y_completar()
    if inventario is not None:
        st.success("Inventario recargado correctamente.")
    else:
        st.error("Error al recargar el inventario.")

# Subir archivos de faltantes
st.header("Carga de Archivos")
faltantes_file = st.file_uploader("Sube el archivo de faltantes (.xlsx)", type=["xlsx"])

# Cargar el inventario desde la API
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

# Filtro para seleccionar opciones mayores o iguales a 1
inventario = inventario[inventario['opcion'] >= 1]
opciones_disponibles = inventario['opcion'].unique().tolist()
opcion_seleccionada = st.multiselect("Selecciona la opción", options=opciones_disponibles, default=[])

# Procesar faltantes si el usuario sube un archivo
if faltantes_file:
    with st.spinner("Procesando faltantes..."):
        # Leer el archivo de faltantes cargado
        faltantes_df = pd.read_excel(faltantes_file)

        # Procesar alternativas iniciales
        alternativas = procesar_faltantes(
            faltantes_df, 
            inventario, 
            columnas_adicionales=['nombre', 'laboratorio', 'presentacion'], 
            bodega_seleccionada=bodega_seleccionada,
            opcion_seleccionada=opcion_seleccionada
        )

        global resultado_acumulado

        if alternativas.empty:
            st.warning("No se encontraron alternativas en esta búsqueda. Intenta con otras opciones o bodegas.")
        else:
            st.success("¡Alternativas generadas exitosamente!")
            st.write("Aquí tienes las alternativas generadas:")
            st.dataframe(alternativas)

            # Actualizar el resultado acumulado
            resultado_acumulado = pd.concat([resultado_acumulado, alternativas], ignore_index=True)

            # Botón para seguir buscando opciones
            if st.button("Seguir buscando opciones"):
                st.info("Realiza otra selección para continuar.")

# Descargar el resultado acumulado
if not resultado_acumulado.empty:
    st.header("Descargar Resultados Consolidados")

    @st.cache_data
    def convertir_a_excel(df):
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Alternativas Consolidadas")
        processed_data = output.getvalue()
        return processed_data

    resultado_excel = convertir_a_excel(resultado_acumulado)
    st.download_button(
        label="Descargar archivo consolidado de alternativas",
        data=resultado_excel,
        file_name="alternativas_consolidadas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.warning("No hay resultados para descargar. Por favor, procesa un archivo de faltantes.")
