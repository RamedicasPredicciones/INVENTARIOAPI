import requests
import pandas as pd
import streamlit as st

def cargar_inventario_y_completar():
    # URL de la API para obtener los productos
    url_inventario = "https://apkit.ramedicas.com/api/items/ws-batchsunits?token=3f8857af327d7f1adb005b81a12743bc17fef5c48f228103198100d4b032f556"
    
    try:
        # Hacer la solicitud GET para obtener los datos de la API
        response = requests.get(url_inventario, verify=False)
        if response.status_code == 200:
            # Convertir la respuesta JSON a un DataFrame
            data_inventario = response.json()
            inventario_df = pd.DataFrame(data_inventario)

            # Normalizar las columnas para evitar discrepancias en mayúsculas/minúsculas
            inventario_df.columns = inventario_df.columns.str.lower().str.strip()

            # Filtrar solo las bodegas permitidas
            bodegas_permitidas = ["A011", "C015", "C018", "D017"]
            inventario_df = inventario_df[inventario_df['bodega'].isin(bodegas_permitidas)]

            # Asegurarse de que las columnas 'unidadeslote' y 'unidadespresentacionlote' sean enteros
            for col in ['unidadeslote', 'unidadespresentacionlote']:
                if col in inventario_df.columns:
                    inventario_df[col] = pd.to_numeric(inventario_df[col], errors='coerce').fillna(0).round().astype(int)

            return inventario_df
        else:
            st.error(f"Error al obtener datos de la API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error en la conexión con la API: {e}")
        return None
