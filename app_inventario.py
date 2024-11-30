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

            # Descargar y cargar el archivo maestro de moléculas
            maestro_moleculas = pd.read_excel(url_maestro_moleculas)
            maestro_moleculas.columns = maestro_moleculas.columns.str.lower().str.strip()

            # Realizar el cruce para agregar las columnas 'cur' y 'embalaje'
            inventario_df = inventario_df.merge(
                maestro_moleculas[['codart', 'cur', 'embalaje']],  # Seleccionar columnas relevantes del maestro
                left_on='codart',  # 'codart' ya está en minúsculas tras normalizar
                right_on='codart',  # Del maestro
                how='left'  # Para conservar todos los datos del inventario, aunque no haya coincidencia
            )

            # Mostrar el DataFrame (opcional)
            print(inventario_df.head())

            # Retornar el DataFrame completo
            return inventario_df
        else:
            print(f"Error al obtener datos de la API: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la conexión con la API: {e}")
        return None

# Llamar la función
inventario_completo = cargar_inventario_y_completar()

# Guardar el resultado como Excel con el nombre `inventario.xlsx`
if inventario_completo is not None:
    inventario_completo.to_excel("inventario.xlsx", index=False)
    print("Archivo generado: inventario.xlsx")
