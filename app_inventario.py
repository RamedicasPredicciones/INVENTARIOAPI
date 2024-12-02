import requests
import pandas as pd

def cargar_inventario_y_completar():
    # URL de la API para obtener los productos
    url_inventario = "https://apkit.ramedicas.com/api/items/ws-batchsunits?token=3f8857af327d7f1adb005b81a12743bc17fef5c48f228103198100d4b032f556"
    url_maestro_moleculas = "https://docs.google.com/spreadsheets/d/19myWtMrvsor2P_XHiifPgn8YKdTWE39O/export?format=xlsx"
    
    try:
        # Hacer la solicitud GET para obtener los datos de la API
        response = requests.get(url_inventario, verify=False)
        if response.status_code == 200:
            # Convertir la respuesta JSON a un DataFrame
            data_inventario = response.json()
            inventario_df = pd.DataFrame(data_inventario)

            # Normalizar las columnas para evitar discrepancias en mayúsculas/minúsculas
            inventario_df.columns = inventario_df.columns.str.lower().str.strip()

            # Renombrar codArt a codart para que coincida con el maestro
            if 'codart' not in inventario_df.columns and 'codart' in inventario_df.columns.str.lower():
                inventario_df.rename(columns={'codArt': 'codart'}, inplace=True)

            # Descargar y cargar el archivo maestro de moléculas
            response_maestro = requests.get(url_maestro_moleculas, verify=False)
            if response_maestro.status_code == 200:
                maestro_moleculas = pd.read_excel(response_maestro.content)
                maestro_moleculas.columns = maestro_moleculas.columns.str.lower().str.strip()

                # Realizar el cruce para agregar las columnas 'cur' y 'embalaje'
                inventario_df = inventario_df.merge(
                    maestro_moleculas[['codart', 'cur', 'embalaje']],  # Seleccionar columnas relevantes del maestro
                    on='codart',  # 'codart' ya está en minúsculas tras normalizar
                    how='left'  # Para conservar todos los datos del inventario, aunque no haya coincidencia
                )

                return inventario_df
            else:
                print(f"Error al obtener el archivo maestro de moléculas: {response_maestro.status_code}")
                return None
        else:
            print(f"Error al obtener datos de la API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la conexión con la API: {e}")
        return None
