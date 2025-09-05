from sqlalchemy import Column, Integer, String, Float, DateTime,ForeignKey
from app.db.session import Base
from sqlalchemy.orm import relationship


class Inventario(Base):
    __tablename__ = "t400_cm_existencia"

    f400_rowid_item_ext= Column(Integer,ForeignKey("t120_mc_items.f120_id"), nullable=True )
    f400_rowid_bodega = Column(Integer, ForeignKey("t150_mc_bodegas.f150_rowid"), nullable=True)
    f400_abc_rotacion_costo= Column(String(10), nullable=True)
    f400_abc_rotacion_veces=Column(String(10), nullable=True)
    f400_costo_prom_uni=Column(Float, nullable=True)
    f400_costo_prom_tot=Column(Float, nullable=True)
    f400_fecha_ult_compra=Column(DateTime, nullable=True)
    f400_fecha_ult_entrada=Column(DateTime, nullable=True)
    f400_fecha_ult_salida=Column(DateTime, nullable=True)
    f400_cant_existencia_1=Column(Float, nullable=True)
    f400_cant_comprometida_1=Column(Float, nullable=True)
    f400_cant_pendiente_salir_1=Column(Float, nullable=True)
    f400_cant_pendiente_entrar_1=Column(Float, nullable=True)

   # Aquí puedes especificar que la combinación de f400_rowid_item_ext y f400_rowid_bodega es la clave primaria
    __mapper_args__ = {
        'primary_key': [f400_rowid_item_ext, f400_rowid_bodega]
    }

    items = relationship("Codigos", back_populates="existencias")
    bodegas= relationship("Bodega", back_populates="existencias")

   

class Bodega(Base):
    __tablename__ = "t150_mc_bodegas"

    f150_rowid=Column(Integer, primary_key = True, index=True)
    f150_id=Column(Integer, nullable=True)
    f150_descripcion=Column(String(150), nullable=True)
    f150_descripcion_corta=Column(String(150), nullable=True)

    existencias= relationship("Inventario", back_populates="bodegas")

class Codigos(Base): # tabla de codigos de items
    __tablename__ = "t120_mc_items"
    f120_id=Column(Integer,primary_key= True, index=True)
    f120_referencia= Column(String(50), nullable=True)
    f120_descripcion=Column(String(255), nullable=True)
    f120_id_unidad_inventario=Column(String(10), nullable=True)

    existencias = relationship("Inventario", back_populates="items")





