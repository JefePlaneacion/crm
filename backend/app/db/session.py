from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib
# Datos de conexión
server = "190.85.249.37"
database = "UnoEE_Pruebas"
username = "Planeacion_BDpruebas"
password = "PR2525+++"

# Cadena de conexión de SQLAlchemy
conn_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=YES&TrustServerCertificate=YES"

# Crear el engine de SQLAlchemy
engine = create_engine(conn_string,connect_args={"check_same_thread": False})

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

