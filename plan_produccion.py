import bs4 as bs
import pandas as pd
import requests
from openpyxl import load_workbook

url = 'https://tg.toscanagroup.com.co/api_powerbi.php'
params = {
     "auth": {
        "user": "jorge.contreras",
        "pass": "EstebanGrey1704*"
    },
    "data": {
        "type":"PLANEACION",
        "f_inicio": "2025-01-01",
        "f_fin": "2025-04-30"
    }
}

# Realizar la solicitud POST a la API
response = requests.post(url=url, json=params)

# Verificar el estado de la respuesta
if response.status_code == 200:
    # procesar respuesta JSON
    data=response.json()
    # Convertir la respuesta JSON a un DataFrame de pandas
    df = pd.DataFrame(data)

df_final=df['registros_planeacion']

df_final.to_excel('plan_produccion.xlsx', index=False)


datos_expandidos = []

for pedido in df_final:
    for producto in pedido['productos']:
        fila= {
            'id':pedido['id'],
            'cliente': pedido['nombre_factura'],
            'fecha_pedido': pedido['f_pedido'],
            'fecha_aprobacion': pedido['fecha_aprobacion'],
            'fecha_entrega': pedido['fecha_estimada'],
            'venta': pedido['venta_real'],
            'modulo_pedido': pedido['estado'],
            'estado_pedido': pedido['estado_detalle'],
            'regional_pedido': pedido['regional'],
            'url': pedido['url'],
            'dias_restantes':pedido['dias_restantes'],
            'cod_producto': producto['id_producto'],
            'desc_producto': producto['producto'].strip(),
            'color_lona': producto['color'],
            'color_estructura': producto['color_estructura'],
            'cantidad': producto['cantidad'],
            'largo': producto['largo'],
            'proyeccion': producto['proyeccion'],
            'alto':producto['alto'],
            'valor_total': producto['valor_total'],
        }

        datos_expandidos.append(fila)

df_final = pd.DataFrame(datos_expandidos)

df_final['url_click'] = df_final['url'].apply(lambda x: f'=HYPERLINK("{x}", "Ver pedido")')

df_final=df_final.drop(columns=['url'], axis=1)

df_final.to_excel('plan_produccion.xlsx', index=False)

print(df_final.head())




