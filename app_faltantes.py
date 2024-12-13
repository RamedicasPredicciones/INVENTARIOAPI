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

    # Redondear las columnas 'existencias_codart_alternativa' a números enteros
    alternativas_disponibles_df['existencias_codart_alternativa'] = alternativas_disponibles_df['existencias_codart_alternativa'].apply(lambda x: math.ceil(x) if pd.notnull(x) else x)

    # Agregar la columna de cantidad necesaria ajustada por el embalaje
    alternativas_disponibles_df['cantidad_necesaria'] = alternativas_disponibles_df.apply(
        lambda row: math.ceil(row['faltante'] * row['embalaje'] / row['embalaje_alternativa'])
        if pd.notnull(row['embalaje']) and pd.notnull(row['embalaje_alternativa']) and row['embalaje_alternativa'] > 0
        else None,
        axis=1
    )

    # Agregar columna de porcentaje suplido
    alternativas_disponibles_df['porcentaje_suplido'] = alternativas_disponibles_df.apply(
        lambda row: min(row['existencias_codart_alternativa'] / row['cantidad_necesaria'], 1.0)
        if pd.notnull(row['cantidad_necesaria']) and row['cantidad_necesaria'] > 0 else 0,
        axis=1
    )

    # Filtrar para mantener solo las alternativas que cubren al menos el 50% del faltante
    alternativas_disponibles_df = alternativas_disponibles_df[alternativas_disponibles_df['porcentaje_suplido'] >= 0.5]

    # Seleccionar la mejor alternativa por cada faltante
    alternativas_disponibles_df = (
        alternativas_disponibles_df.sort_values(by=['porcentaje_suplido', 'existencias_codart_alternativa'], ascending=[False, False])
        .groupby(['cur', 'codart'])
        .first()
        .reset_index()
    )

    # Agregar las columnas adicionales si es necesario
    if columnas_adicionales:
        for columna in columnas_adicionales:
            if columna in inventario_df.columns:
                alternativas_disponibles_df[columna] = inventario_df[columna]

    return alternativas_disponibles_df
