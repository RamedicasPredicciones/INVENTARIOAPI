import pandas as pd
import streamlit as st

# Cargar los archivos de faltantes e inventario (asegúrate de tener los archivos correctos)
archivo_faltantes = 'faltantes.xlsx'  # Nombre del archivo de faltantes
archivo_inventario = 'inventario.xlsx'  # Nombre del archivo de inventario

# Lee los archivos de Excel
faltantes_df = pd.read_excel(archivo_faltantes)
inventario_df = pd.read_excel(archivo_inventario)

# Muestra el título de la aplicación
st.title("Generador de Alternativas de Inventario")

# Selección de bodegas (permitir seleccionar varias bodegas)
bodegas = inventario_df['bodega'].unique()  # Obtener las bodegas disponibles en el inventario
bodegas_seleccionadas = st.multiselect(
    "Selecciona las bodegas", 
    options=bodegas, 
    default=bodegas.tolist()  # Por defecto seleccionamos todas las bodegas
)

# Si no se seleccionan bodegas, muestra un mensaje de error
if not bodegas_seleccionadas:
    st.warning("Por favor selecciona al menos una bodega.")
else:
    # Filtrar inventario según las bodegas seleccionadas
    inventario_filtrado = inventario_df[inventario_df['bodega'].isin(bodegas_seleccionadas)]
    
    # Generar lista de alternativas
    alternativas_disponibles = []

    # Iteramos sobre los faltantes
    for index, row in faltantes_df.iterrows():
        cur_faltante = row['cur']
        cantidad_faltante = row['faltante']

        # Filtrar el inventario por código de artículo faltante y las bodegas seleccionadas
        alternativas = inventario_filtrado[inventario_filtrado['codart'] == cur_faltante]

        # Verifica si hay alternativas disponibles para ese artículo faltante
        if not alternativas.empty:
            # Aquí agregas más lógica si quieres personalizar cómo seleccionar alternativas
            alternativas['numlote'] = alternativas['numlote'].astype(str)  # Asegúrate de que los números de lote estén en el formato correcto
            alternativas_disponibles.append(alternativas)

    # Mostrar las alternativas generadas
    if alternativas_disponibles:
        alternativas_finales = pd.concat(alternativas_disponibles, ignore_index=True)
        st.success("¡Alternativas generadas exitosamente!")
        st.dataframe(alternativas_finales)  # Mostrar las alternativas en formato tabla
    else:
        st.warning("No se encontraron alternativas para los artículos faltantes.")

