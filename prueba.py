import pyodbc
import pandas as pd

server = "190.85.249.37"
database = "UnoEE_Pruebas"
username = "Planeacion_BDpruebas"
password = "PR2525+++"

conn_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
conn = pyodbc.connect(conn_string)
cursor = conn.cursor()

df = pd.read_sql_query("SELECT TOP 20 * FROM t860_mf_op_componentes", conn)

df.to_excel('plan_produc1.xlsx', index=False)

print(df.head())
conn.close()