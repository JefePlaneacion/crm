from sqlalchemy import Column, Integer, String, Float, DateTime,ForeignKey,PrimaryKeyConstraint
from app.db.session import Base
from sqlalchemy.orm import relationship

# DOCUMENTOS

# TIPOS DE DOCUMENTOS

class TipoDocumento(Base):
    __tablename__ = "t021_mm_tipos_documentos"
    f021_id=Column(String(5), primary_key= True, index=True)
    f021_descripcion=Column(String(100), nullable=True)

    documento_compra = relationship("DocumentoCompra", back_populates="tipo_documento")

# ESTADOS DE DOCUMENTOS

class Estado(Base):
    __tablename__="t054_mm_estados"
    f054_id_grupo_clase_docto=Column(Integer,nullable=True)
    f054_id=Column(Integer, primary_key=True)
    f054_descripcion=Column(String(100),nullable=True)

    documentos_por_estado = relationship(
        "DocumentoCompra",
        back_populates="estado_doc",
        foreign_keys="[DocumentoCompra.f420_ind_estado]",
        primaryjoin="Estado.f054_id == DocumentoCompra.f420_ind_estado"
    )

    # inversa por grupo
    documentos_por_grupo = relationship(
        "DocumentoCompra",
        back_populates="estado_grupo",
        primaryjoin="Estado.f054_id_grupo_clase_docto == DocumentoCompra.f420_id_grupo_clase_docto",
        foreign_keys="[DocumentoCompra.f420_id_grupo_clase_docto]",
        viewonly=True
    )


    


# Tabla de inventario
class Inventario(Base):
    __tablename__ = "t400_cm_existencia"
    __table_args__ = (PrimaryKeyConstraint('f400_rowid_item_ext', 'f400_rowid_bodega'),)
    
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

    item = relationship("Codigos", back_populates="existencias")
    bodegas= relationship("Bodega", back_populates="existencias")

    #Relación con ItemsCompras
    items_compras_inventario = relationship("ItemsCompras", back_populates="existencias")

   
# Tabla de bodegas
class Bodega(Base): #OK
    __tablename__ = "t150_mc_bodegas"

    f150_rowid=Column(Integer, primary_key = True, index=True)
    f150_id=Column(String(10), nullable=True)
    f150_descripcion=Column(String(150), nullable=True)
    f150_descripcion_corta=Column(String(150), nullable=True)

    existencias= relationship("Inventario", back_populates="bodegas")
    items_compras_inventario = relationship("ItemsCompras", back_populates="bodegas")
    bod_mov_inventario = relationship("MovInventario", back_populates="mov_bodegas")

# Tabla de codigos de items
class Codigos(Base):
    __tablename__ = "t120_mc_items"
    f120_id=Column(Integer,primary_key= True, index=True)
    f120_referencia= Column(String(50), nullable=True)
    f120_descripcion=Column(String(255), nullable=True)
    f120_id_unidad_inventario=Column(String(10), nullable=True)

    existencias = relationship("Inventario", back_populates="items")





