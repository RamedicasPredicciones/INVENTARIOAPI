import math
import pandas as pd

def procesar_faltantes(faltantes_df, inventario_api_df, columnas_adicionales, bodega_seleccionada):
    # Normalizar las columnas para evitar discrepancias en mayúsculas/minúsculas
    faltantes_df.columns = faltantes_df.columns.str.lower().str.strip()
    inventario_api_df.columns = inventario_api_df.columns.str.lower().str.strip()

    # Verificar que el archivo de faltantes tenga las columnas necesarias
    columnas_necesarias = {'cur', 'codart', 'faltante', 'embalaje'}
    if not columnas_necesarias.issubset(faltantes_df.columns):
        raise ValueError(f"El archivo de faltantes debe contener las columnas: {', '.join(columnas_necesarias)}")

    # Filtrar las alternativas de inventario que coincidan con los códigos de producto (cur)
    cur_faltantes = faltantes_df['cur'].unique()
    alternativas_inventario_df = inventario_api_df[inventario_api_df['cur'].isin(cur_faltantes)]

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

    # Filtrar los registros donde hay una opción alternativa disponible
    alternativas_disponibles_df = alternativas_disponibles_df[alternativas_disponibles_df['opcion_alternativa'] > 0]

    # Agregar la columna de cantidad necesaria ajustada por el embalaje
    alternativas_disponibles_df['cantidad_necesaria'] = alternativas_disponibles_df.apply(
        lambda row: math.ceil(row['faltante'] * row['embalaje'] / row['embalaje_alternativa'])
        if pd.notnull(row['embalaje']) and pd.notnull(row['embalaje_alternativa']) and row['embalaje_alternativa'] > 0
        else None,
        axis=1
    )

    # Ordenar las alternativas por código de producto y existencias de la alternativa
    alternativas_disponibles_df.sort_values(by=['codart', 'existencias_codart_alternativa'], inplace=True)

    # Buscar la mejor alternativa para cada código de artículo faltante
    mejores_alternativas = []
    for codart_faltante, group in alternativas_disponibles_df.groupby('codart'):
        faltante_cantidad = group['faltante'].iloc[0]

        # Buscar en la bodega seleccionada la mejor opción
        mejor_opcion_bodega = group[group['existencias_codart_alternativa'] >= faltante_cantidad]
        mejor_opcion = mejor_opcion_bodega.head(1) if not mejor_opcion_bodega.empty else group.nlargest(1, 'existencias_codart_alternativa')

        mejores_alternativas.append(mejor_opcion.iloc[0])

    # Crear el DataFrame final con las mejores alternativas
    resultado_final_df = pd.DataFrame(mejores_alternativas)

    # Agregar las columnas de "suplido" (si el faltante fue cubierto) y "faltante_restante"
    resultado_final_df['suplido'] = resultado_final_df.apply(
        lambda row: 'SI' if row['existencias_codart_alternativa'] >= row['cantidad_necesaria'] else 'NO',
        axis=1
    )

    # Calcular la cantidad restante de faltante, si no se suplió completamente
    resultado_final_df['faltante_restante_alternativa'] = resultado_final_df.apply(
        lambda row: row['cantidad_necesaria'] - row['existencias_codart_alternativa'] if row['suplido'] == 'NO' else 0,
        axis=1
    )

    # Selección de las columnas finales a mostrar
    columnas_finales = ['cur', 'codart', 'faltante', 'embalaje', 'codart_alternativa', 'opcion_alternativa',
                        'embalaje_alternativa', 'cantidad_necesaria', 'existencias_codart_alternativa', 'bodega', 'suplido',
                        'faltante_restante_alternativa']
    columnas_finales.extend([col.lower() for col in columnas_adicionales])
    columnas_presentes = [col for col in columnas_finales if col in resultado_final_df.columns]
    resultado_final_df = resultado_final_df[columnas_presentes]

    return resultado_final_df
