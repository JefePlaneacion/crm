import pandas as pd
from sqlalchemy import create_engine

# Datos de conexión
server = "190.85.249.37"
database = "UnoEE"
username = "PLANEACION"
password = "Damis2025"

# Cadena de conexión de SQLAlchemy
conn_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=YES&TrustServerCertificate=YES"

# Crear el engine de SQLAlchemy
engine = create_engine(conn_string)

# Conexión y manejo de errores
try:
    # Usando 'with' para asegurar que la conexión se cierre correctamente
    with engine.connect() as conn:
        # Consulta SQL
        query = "SELECT top 300* FROM t450_cm_docto_invent WHERE "
        

        # Leer la consulta directamente con pandas
        df = pd.read_sql(query, conn)
        
        # Exportar el DataFrame a Excel
        df.to_excel('TABLAS_RESUM_INTPPP.xlsx', index=False, sheet_name='Datos_Consultados')
        
        # Mostrar las primeras filas del DataFrame
        print(df.head())

except Exception as e:
    # Manejo de errores de conexión o consulta
    print(f"Error al conectar a la base de datos: {e}")
