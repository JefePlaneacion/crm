from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib
# Datos de conexión
server = "190.85.249.37"
database = "UnoEE"
username = "PLANEACION"
password = "Damis2025"

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


__tablename__ = "t470_cm_movto_invent"
    f470_ts=Column(DateTime, nullable=True)
    f470_id_cia=Column(Integer, nullable=True)
    f470_rowid=Column(Integer, primary_key=True, nullable=True)
    f470_rowid_docto=Column(Integer, ForeignKey("t450_cm_docto_invent.f450_rowid_docto"),nullable=True)
    f470_rowid_item_ext=Column(Integer,ForeignKey("t120_mc_items.f120_id") nullable=True)
    f470_rowid_bodega=Column(Integer,ForeignKey("t150_mc_bodegas.f150_id"),nullable=True)
    f470_id_periodo=Column(Integer, nullable=True)
    f470_ind_estado_cm=Column(Integer ,nullable=True)
    f470_id_concepto=Column(Integer,nullable=True)
    f470_id_unidad_medida=Column(String,nullable=True)
    f470_cant_base=Column(Integer,nullable=True)
    f470_costo_prom_uni=Column(Integer,nullable=True)
    f470_costo_prom_tot=Column(Integer,nullable=True)
    
    mov_doc= relationship("DocumentosInventario",back_populates="doc_inv")
    mov_bodegas=relationship("Bodega",back_populates="bod_inv")
    mov_items=relationship("Codigos",back_populates="cod_mov_inventario")
