import math
import pandas as pd

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

    # Filtrar las alternativas que tienen una opción alternativa válida (opcion_alternativa > 0)
    alternativas_disponibles_df = alternativas_disponibles_df[alternativas_disponibles_df['opcion_alternativa'] > 0]

    return alternativas_disponibles_df
