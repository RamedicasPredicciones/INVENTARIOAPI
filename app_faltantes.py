import streamlit as st
import math
import pandas as pd

# Función para procesar los faltantes
def procesar_faltantes(faltantes_df, inventario_df, columnas_adicionales, bodega_seleccionada):
    # Normalizar las columnas para evitar discrepancias en mayúsculas/minúsculas
    faltantes_df.columns = faltantes_df.columns.str.lower().str.strip()
    inventario_df.columns = inventario_df.columns.str.lower().str.strip()

    # Verificar que el archivo de faltantes tenga las columnas necesarias
    columnas_necesarias = {'cur', 'codart', 'faltante', 'embalaje'}
    if not columnas_necesarias.issubset(faltantes_df.columns):
        raise ValueError(f"El archivo de faltantes debe contener las columnas: {', '.join(columnas_necesarias)}")

    # Filtrar las alternativas de inventario que coincidan con los códigos de producto (codart)
    codart_faltantes = faltantes_df['codart'].unique()
    alternativas_inventario_df = inventario_df[inventario_df['codart'].isin(codart_faltantes)]

    # Filtrar por bodega si es necesario
    if bodega_seleccionada:
        alternativas_inventario_df = alternativas_inventario_df[alternativas_inventario_df['bodega'].isin(bodega_seleccionada)]

    # Filtrar alternativas con existencias mayores a 0
    alternativas_disponibles_df = alternativas_inventario_df[alternativas_inventario_df['unidadespresentacionlote'] > 0]

    # Renombrar las columnas para mayor claridad
    alternativas_disponibles_df.rename(columns={
        'codart': 'codart_alternativa',
        'opcion': 'opcion_alternativa',
        'embalaje': 'embalaje_alternativa',
        'unidadespresentacionlote': 'existencias_codart_alternativa'
    }, inplace=True)

    # Unir el DataFrame de faltantes con las alternativas disponibles
    alternativas_disponibles_df = pd.merge(
        faltantes_df[['cur', 'codart', 'faltante', 'embalaje']],
        alternativas_disponibles_df,
        on='cur',
        how='inner'
    )

    # Agregar la columna de cantidad necesaria ajustada por el embalaje
    alternativas_disponibles_df['cantidad_necesaria'] = alternativas_disponibles_df.apply(
        lambda row: math.ceil(row['faltante'] * row['embalaje'] / row['embalaje_alternativa'])
        if pd.notnull(row['embalaje']) and pd.notnull(row['embalaje_alternativa']) and row['embalaje_alternativa'] > 0
        else None,
        axis=1
    )

    # Filtrar alternativas con cantidad necesaria mayor que 0
    alternativas_disponibles_df = alternativas_disponibles_df[alternativas_disponibles_df['cantidad_necesaria'] > 0]

    # Agregar las columnas adicionales si es necesario
    if columnas_adicionales:
        for columna in columnas_adicionales:
            if columna in inventario_df.columns:
                alternativas_disponibles_df[columna] = inventario_df[columna]

    return alternativas_disponibles_df

# Interfaz de Streamlit
st.title('Generador de Alternativas para Faltantes')

# Cargar el archivo de inventario y faltantes
# Para este ejemplo, puedes cargar el inventario desde un archivo o URL, por ejemplo:
inventario_df = pd.read_excel('ruta_a_inventario.xlsx')  # Cambia la ruta según corresponda
faltantes_df = pd.read_excel('ruta_a_faltantes.xlsx')  # Cambia la ruta según corresponda

# Filtrar bodegas disponibles
bodegas_disponibles = inventario_df['bodega'].unique().tolist()
bodega_seleccionada = st.multiselect("Seleccione la bodega", options=bodegas_disponibles, default=[])

# Selección de columnas adicionales
columnas_adicionales = st.multiselect(
    "Selecciona columnas adicionales para incluir en el archivo final:",
    options=["presentacionart", "numlote", "fechavencelote"],
    default=[]
)

# Procesar los faltantes
resultado_final_df = procesar_faltantes(faltantes_df, inventario_df, columnas_adicionales, bodega_seleccionada)

# Mostrar el resultado
if not resultado_final_df.empty:
    st.write("Archivo procesado correctamente.")
    st.dataframe(resultado_final_df)
else:
    st.write("No se encontraron alternativas para los faltantes seleccionados.")
