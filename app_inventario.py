# app_inventario.py
import requests
import pandas as pd

def cargar_inventario():
    # Descargar inventario desde la API (formato JSON -> Excel)
    url_inventario = "https://apkit.ramedicas.com/api/items/ws-batchsunits?token=3f8857af327d7f1adb005b81a12743bc17fef5c48f228103198100d4b032f556"
    response = requests.get(url_inventario, verify=False)

    if response.status_code == 200:
        # Convertir la respuesta en formato JSON a un DataFrame
        data_inventario = response.json()
        inventario_df = pd.DataFrame(data_inventario)

        # Normalizar las columnas para evitar discrepancias en mayúsculas/minúsculas
        inventario_df.columns = inventario_df.columns.str.lower().str.strip()

        # Guardar el DataFrame como un archivo Excel
        inventario_df.to_excel("productos_completos.xlsx", index=False)

        # Mostrar el DataFrame (opcional)
        print(inventario_df.head())
        return inventario_df
    else:
        print(f"Error al obtener datos de la API: {response.status_code}")
        return None
