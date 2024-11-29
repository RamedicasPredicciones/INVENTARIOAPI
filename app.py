import requests
import pandas as pd
from IPython.display import display

# URL de la API que quieres leer
url = "https://apkit.ramedicas.com/api/items/ws-batchsunits?token=3f8857af327d7f1adb005b81a12743bc17fef5c48f228103198100d4b032f556"

# Haz la solicitud a la API, deshabilitando la verificación de SSL
response = requests.get(url, verify=False)

if response.status_code == 200:
    # Convertir la respuesta en formato JSON a un DataFrame
    data = response.json()
    df = pd.DataFrame(data)

    # Mostrar el DataFrame completo
    display(df)

    # Guardar el DataFrame completo en un archivo Excel
    df.to_excel("productos_completos.xlsx", index=False)

else:
    print(f"Error: {response.status_code}")
