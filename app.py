import streamlit as st
from app_inventario import cargar_inventario_y_completar
from app_faltantes import procesar_faltantes
import pandas as pd

# URL de la plantilla para faltantes
PLANTILLA_URL = "https://docs.google.com/spreadsheets/d/1CPMBfCiuXq2_l8KY68HgexD-kyNVJ2Ml/export?format=xlsx"

# Configuración inicial de Streamlit
st.set_page_config(page_title="RAMEDICAS - Generador de Alternativas", layout="wide")

# URL del fondo (asegúrate de que sea un enlace público directo)
FONDO_URL = "https://drive.google.com/uc?id=12bErHbEtceFn_JvSxwvnxKPUUH7YZykC"

# Aplicar fondo a la app
def aplicar_fondo(fondo_url):
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-image: url("{fondo_url}");
                background-size: cover;
                background-position: center center;
                background-attachment: fixed;
                background-repeat: no-repeat;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Llamada a la función para aplicar el fondo
aplicar_fondo(FONDO_URL)

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

# Filtrar opciones disponibles
if 'opcionart' in inventario.columns:
    inventario.rename(columns={'opcionart': 'opcion'}, inplace=True)

# Convertir la columna "opcion" a numérica
if 'opcion' in inventario.columns:
    inventario['opcion'] = pd.to_numeric(inventario['opcion'], errors='coerce').fillna(0)

# Ordenar el inventario por "opcion" ascendente
inventario = inventario.sort_values(by=['opcion'])

opciones_disponibles = inventario[inventario['opcion'] >= 1]['opcion'].unique().tolist()
opcion_seleccionada = st.multiselect("Selecciona la opcion", options=opciones_disponibles, default=[])

# Tabla acumulativa de resultados
resultados_acumulados = pd.DataFrame()

def buscar_alternativas(faltantes_df, inventario, bodega_seleccionada, opcion_seleccionada):
    # Filtrar inventario por las opciones seleccionadas
    if opcion_seleccionada:
        inventario = inventario[inventario['opcion'].isin(opcion_seleccionada)]
    return procesar_faltantes(
        faltantes_df, 
        inventario, 
        columnas_adicionales=['nombre', 'laboratorio', 'presentacion'], 
        bodega_seleccionada=bodega_seleccionada
    )

# Procesar faltantes si el usuario sube un archivo
if faltantes_file:
    with st.spinner("Procesando faltantes..."):
        faltantes_df = pd.read_excel(faltantes_file)

        alternativas = buscar_alternativas(
            faltantes_df,
            inventario,
            bodega_seleccionada,
            opcion_seleccionada
        )

        if alternativas.empty:
            st.warning("No se encontraron alternativas para los faltantes actuales. Por favor, selecciona otras opciones y vuelve a buscar.")
        else:
            st.success("¡Alternativas generadas exitosamente!")
            resultados_acumulados = pd.concat([resultados_acumulados, alternativas], ignore_index=True)

            st.dataframe(resultados_acumulados)

        # Descargar resultados acumulados
        if not resultados_acumulados.empty:
            @st.cache_data
            def convertir_a_excel(df):
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    # Filtrar las columnas deseadas
                    columnas_deseadas = [
                        "cur", "codart", "faltante", "embalaje", "codart_alternativa", 
                        "nomart", "presentacionart", "embalaje_alternativa", "nomcomercial", 
                        "descontart", "ffarmaceuticaart", "nomfabrart", "opcion_alternativa", 
                        "numlote", "fechavencelote", "unidadeslote", 
                        "existencias_codart_alternativa", "bodega", "cantidad_necesaria", 
                        "estado_suplido"
                    ]
                    # Asegurarse de que solo las columnas disponibles sean seleccionadas
                    df_filtrado = df[columnas_deseadas]
                    df_filtrado.to_excel(writer, index=False, sheet_name="Alternativas")
                return output.getvalue()

            alternativas_excel = convertir_a_excel(resultados_acumulados)
            st.download_button(
                label="Descargar archivo de alternativas",
                data=alternativas_excel,
                file_name="alternativas_generadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
else:
    st.warning("Por favor, sube un archivo de faltantes para procesar.")
