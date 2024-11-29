import requests
import pandas as pd

def cargar_inventario():
    # URL de la API para obtener los productos
    url_inventario = "https://apkit.ramedicas.com/api/items/ws-batchsunits?token=3f8857af327d7f1adb005b81a12743bc17fef5c48f228103198100d4b032f556"
    
    try:
        # Hacer la solicitud GET para obtener los datos de la API
        response = requests.get(url_inventario, verify=False)

        # Verificar si la respuesta fue exitosa
        if response.status_code == 200:
            # Convertir la respuesta JSON a un DataFrame
            data_inventario = response.json()
            inventario_df = pd.DataFrame(data_inventario)

            # Normalizar las columnas para evitar discrepancias en mayúsculas/minúsculas
            inventario_df.columns = inventario_df.columns.str.lower().str.strip()

            # Mostrar el DataFrame (opcional)
            print(inventario_df.head())

            # Retornar el DataFrame
            return inventario_df
        else:
            print(f"Error al obtener datos de la API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la conexión con la API: {e}")
        return None
