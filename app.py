import streamlit as st
import pandas as pd
from app_inventario import cargar_inventario_y_completar
from app_faltantes import procesar_faltantes

# Cargar los datos de inventario y faltantes
inventario_df = cargar_inventario_y_completar()
faltantes_df = pd.read_csv("faltantes.csv")  # Ajusta según tu fuente de datos

# Filtros interactivos para seleccionar Bodega y Opción
# Aquí asumimos que las columnas de 'bodega' y 'opcion' están presentes en el DataFrame de inventario
bodegas = inventario_df['bodega'].unique()
opciones = inventario_df['opcion'].unique()

# Filtro para Bodega
bodega_seleccionada = st.selectbox("Selecciona la Bodega", options=bodegas)

# Filtro para Opción
opcion_seleccionada = st.selectbox("Selecciona la Opción", options=opciones)

# Filtrar el DataFrame según la selección
if bodega_seleccionada:
    inventario_df = inventario_df[inventario_df['bodega'] == bodega_seleccionada]

if opcion_seleccionada:
    inventario_df = inventario_df[inventario_df['opcion'] == opcion_seleccionada]

# Procesar los faltantes según los filtros seleccionados
resultados_faltantes = procesar_faltantes(faltantes_df, inventario_df, columnas_adicionales=None, bodega_seleccionada=[bodega_seleccionada])

# Mostrar los resultados
st.write(resultados_faltantes)
