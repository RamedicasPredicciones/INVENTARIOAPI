import math
import pandas as pd

def procesar_faltantes(faltantes_df, inventario_df, columnas_adicionales, bodega_seleccionada):
    # Normalizar columnas
    faltantes_df.columns = faltantes_df.columns.str.lower().str.strip()
    inventario_df.columns = inventario_df.columns.str.lower().str.strip()

    # Verificar columnas necesarias
    columnas_necesarias = {'cur', 'codart', 'faltante', 'embalaje'}
    if not columnas_necesarias.issubset(faltantes_df.columns):
        raise ValueError(f"El archivo de faltantes debe contener las columnas: {', '.join(columnas_necesarias)}")

    # Filtrar alternativas de inventario
    codart_faltantes = faltantes_df['codart'].unique()
    alternativas_inventario_df = inventario_df[inventario_df['codart'].isin(codart_faltantes)]

    # Filtrar por bodega
    if bodega_seleccionada:
        alternativas_inventario_df = alternativas_inventario_df[alternativas_inventario_df['bodega'].isin(bodega_seleccionada)]

    # Filtrar existencias y opciones mayores o iguales a 1
    alternativas_disponibles_df = alternativas_inventario_df[
        (alternativas_inventario_df['unidadespresentacionlote'] > 0) &
        (alternativas_inventario_df['opcion'] >= 1)
    ]

    # Renombrar columna 'opcionart' a 'opcion'
    alternativas_disponibles_df.rename(columns={
        'codart': 'codart_alternativa',
        'opcionart': 'opcion',
        'embalaje': 'embalaje_alternativa',
        'unidadespresentacionlote': 'existencias_codart_alternativa'
    }, inplace=True)

    # Combinar con faltantes
    alternativas_disponibles_df = pd.merge(
        faltantes_df[['cur', 'codart', 'faltante', 'embalaje']],
        alternativas_disponibles_df,
        on='cur',
        how='inner'
    )

    # Calcular cantidad necesaria y porcentaje suplido
    alternativas_disponibles_df['cantidad_necesaria'] = alternativas_disponibles_df.apply(
        lambda row: math.ceil(row['faltante'] * row['embalaje'] / row['embalaje_alternativa'])
        if row['embalaje_alternativa'] > 0 else None,
        axis=1
    )

    alternativas_disponibles_df['porcentaje_suplido'] = alternativas_disponibles_df.apply(
        lambda row: min(row['existencias_codart_altern

