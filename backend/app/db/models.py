from sqlalchemy import Column, Integer, String, Float, DateTime,ForeignKey,PrimaryKeyConstraint,ForeignKeyConstraint
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

   #Claves primarias compuestas
   

    items = relationship("Codigos", back_populates="existencias")
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
    bod_inv = relationship("MovInventario", back_populates="mov_bodegas")

# Tabla de codigos de items
class Codigos(Base):
    __tablename__ = "t120_mc_items"
    f120_id=Column(Integer,primary_key= True, index=True)
    f120_referencia= Column(String(50), nullable=True)
    f120_descripcion=Column(String(255), nullable=True)
    f120_id_unidad_inventario=Column(String(10), nullable=True)

    existencias = relationship("Inventario", back_populates="items")
    items_compras_inventario = relationship("ItemsCompras", back_populates="items",foreign_keys="[ItemsCompras.f421_rowid_item_ext]")
    cod_mov_inventario = relationship("MovInventario", back_populates="mov_items", foreign_keys="[MovInventario.f4702_rowid_item_ext]")


# SECCION COMPRAS

# Tabla de proveedores

#tABLA CLASE PROVEEDORES
class TipoProveedor(Base): #OK
    __tablename__ = "t209_mm_clase_proveedor"
    f209_id=Column(String(10), primary_key=True, index=True)
    f209_descripcion=Column(String(100), nullable=True)
    f202_rowid_tercero=Column(Integer, ForeignKey("t200_mm_terceros.f200_rowid"), nullable=True)

    clase_proveedor= relationship("Proveedor",back_populates="tipo_proveedor",
        foreign_keys=[f202_rowid_tercero])

# Tabla de proveedores

class Proveedor(Base): #OK
    __tablename__ = "t200_mm_terceros"
    f200_rowid=Column(Integer, primary_key=True, index=True)
    f200_nit=Column(String(150), nullable=True)
    f200_razon_social=Column(String(255), nullable=True)
    
    tipo_proveedor= relationship("TipoProveedor", back_populates="clase_proveedor")
    documento_compra=relationship("DocumentoCompra",back_populates="clase_proveedor",foreign_keys=lambda:[DocumentoCompra.f420_rowid_tercero_prov],uselist=True)


# Tabla dOCUMENTOS COMPRAS

#tabla de documentos generales de orden de compra

class DocumentoCompra(Base):#OK
    __tablename__ = "t420_cm_oc_docto"
    f420_rowid=Column(Integer, primary_key=True, index=True)
    f420_id_tipo_docto=Column(String(4),ForeignKey("t021_mm_tipos_documentos.f021_id"), index=True)
    f420_consec_docto=Column(Integer,index=True)
    f420_fecha=Column(DateTime, nullable=True)
    f420_id_grupo_clase_docto=Column(Integer,nullable=True)
    f420_ind_estado=Column(Integer,ForeignKey("t054_mm_estados.f054_id"),index=True,nullable=True)
    f420_rowid_tercero_sol_comp=Column(Integer,nullable=True)
    f420_rowid_tercero_prov=Column(Integer,ForeignKey("t200_mm_terceros.f200_rowid"),index=True,nullable=True)
    f420_fecha_ts_creacion=Column(DateTime, nullable=True)
    f420_fecha_ts_aprobacion=Column(DateTime, nullable=True)
    f420_fecha_ts_parcial=Column(DateTime, nullable=True)
    f420_fecha_ts_cumplido=Column(DateTime, nullable=True)


    tipo_documento = relationship("TipoDocumento", back_populates="documento_compra")
    estado_doc = relationship(
        "Estado", 
        back_populates="documentos_por_estado", 
        foreign_keys=[f420_ind_estado],
        primaryjoin="DocumentoCompra.f420_ind_estado == Estado.f054_id",  # Agregué primaryjoin explícito
        uselist=False
    )
    estado_grupo = relationship(
        "Estado",
        back_populates="documentos_por_grupo",
        foreign_keys=[f420_id_grupo_clase_docto],
        primaryjoin="DocumentoCompra.f420_id_grupo_clase_docto == Estado.f054_id_grupo_clase_docto",
        uselist=False,  # Cambié a False porque solo debe traer un registro
        viewonly=True  # Agregué viewonly porque es informativa
    )
    clase_proveedor = relationship("Proveedor", back_populates="documento_compra", foreign_keys=[f420_rowid_tercero_prov], uselist=False)
    items_compras_inventario = relationship("ItemsCompras", back_populates="documento_compra")

#tabla de items x ordenes de compra
class ItemsCompras(Base):
    __tablename__ = "t421_cm_oc_movto"
    __table_args__ = (
        PrimaryKeyConstraint("f421_rowid_oc_docto", "f421_rowid_item_ext", "f421_rowid_bodega"),
        # si necesitas relacionar con Inventario
        ForeignKeyConstraint(
            ["f421_rowid_item_ext", "f421_rowid_bodega"],
            ["t400_cm_existencia.f400_rowid_item_ext", "t400_cm_existencia.f400_rowid_bodega"]
        ),
    )

    f421_rowid_oc_docto=Column(Integer, ForeignKey("t420_cm_oc_docto.f420_rowid"),index=True)
    f421_rowid_item_ext=Column(Integer, ForeignKey("t120_mc_items.f120_id"))
    f421_rowid_bodega=Column(Integer, ForeignKey("t150_mc_bodegas.f150_rowid"), index=True)
    f421_fecha=Column(DateTime,nullable=True)
    f421_id_unidad_medida=Column(String(5), nullable=True)
    f421_cant_pedida=Column(Float, nullable=True)
    f421_cant_entrada=Column(Float, nullable=True)
    f421_ind_estado=Column(Integer, nullable=True)
    f421_precio_unitario=Column(Float, nullable=True)


    documento_compra = relationship("DocumentoCompra",back_populates="items_compras_inventario", foreign_keys=[f421_rowid_oc_docto], uselist=False) #OK
    items = relationship("Codigos", back_populates="items_compras_inventario",overlaps="existencias",foreign_keys=[f421_rowid_item_ext],uselist=True) #OK
    bodegas = relationship("Bodega",back_populates="items_compras_inventario",overlaps="items_compras_inventario",uselist=True) #OK
    # Relación con t400_cm_existencia (Inventario)
    existencias = relationship("Inventario", back_populates="items_compras_inventario",overlaps="bodegas,items_compras_inventario",uselist=True)

    proveedor = relationship("Proveedor",
        secondary="t420_cm_oc_docto",
        primaryjoin="ItemsCompras.f421_rowid_oc_docto==DocumentoCompra.f420_rowid",
        secondaryjoin="DocumentoCompra.f420_rowid_tercero_prov==Proveedor.f200_rowid",
        uselist=False,
        viewonly=True
    )


# TABLAS MOVIMIENTOS DE INVENTARIOS

class Conceptos(Base):
    __tablename__ = "t145_mc_conceptos"

    f145_id=Column(Integer, primary_key=True, index=True)
    f145_descripcion=Column(String(150), nullable=True)

    


class ClasesDocumento(Base):
    __tablename__ = "t028_mm_clases_documento"

    f028_id= Column(Integer, primary_key=True, index=True)
    f028_descripcion= Column(String(100), nullable=True)
    f028_id_grupo_clase_docto= Column(Integer, nullable=True)

    # Relación con DocumentosInventario
    documentos_inventario = relationship("DocumentosInventario", back_populates="clase_documento")
   


class DocumentosInventario(Base):
    __tablename__ = "t450_cm_docto_invent"

    f450_ts= Column(DateTime, nullable=True)
    f450_rowid_docto= Column(Integer, primary_key=True, index=True)
    f450_id_clase_docto= Column(Integer, ForeignKey("t028_mm_clases_documento.f028_id"), nullable=True)
    f450_id_concepto= Column(Integer, ForeignKey("t145_mc_conceptos.f145_id"), index=True)
    f450_ind_estado_cm= Column(Integer, ForeignKey("t054_mm_estados.f054_id"),nullable=True)


    clase_documento = relationship("ClasesDocumento", back_populates="documentos_inventario")
    doc_inv = relationship("MovInventario",back_populates="mov_doc")

    # relacion con estado (usando los dos campos)

    estado = relationship(
        "Estado",
        uselist=False,
        viewonly=True,
    )







class MovInventario(Base):
    __tablename__ = "t4702_cm_log_movto_invent"

    f4702_ts=Column(DateTime, nullable=True)
    f4702_id_cia=Column(Integer, nullable=True)
    f4702_id_co=Column(String, nullable=True)
    f4702_id_tipo=Column(String, nullable=True)
    f4702_consec_docto=Column(Integer, nullable=True)
    f4702_rowid_movto=Column(Integer, primary_key=True,nullable=True)
    f4702_rowid_docto=Column(Integer,ForeignKey("t450_cm_docto_invent.f450_rowid_docto"),nullable=True)
    f4702_rowid_item_ext=Column(Integer,ForeignKey("t120_mc_items.f120_id"), nullable=True)
    f4702_rowid_bodega=Column(Integer,ForeignKey("t150_mc_bodegas.f150_rowid"), index=True, nullable=True)
    f4702_id_concepto=Column(Integer,ForeignKey("t145_mc_conceptos.f145_id"),index=True, nullable=False)
    f4702_cant_1=Column(Float, nullable=True)
    f4702_costo_prom_uni=Column(Float, nullable=True)
    f4702_costo_prom_tot=Column(Float,nullable=True)
    f4702_usuario=Column(String, nullable=True)

    concepto_mov = relationship("Conceptos", back_populates="Id_concepto_mov", foreign_keys=[f4702_id_concepto], uselist=False)
    mov_bodegas = relationship("Bodega",back_populates="bod_mov_inventario", foreign_keys=[f4702_rowid_bodega], uselist=False)
    mov_items = relationship("Codigos",back_populates="cod_mov_inventario", foreign_keys=[f4702_rowid_item_ext], uselist=False)
    mov_doc = relationship("DocumentosInventario", back_populates="doc_inv")


    estado = relationship(
        "Estado",
        secondary="t450_cm_docto_invent",
        primaryjoin="MovInventario.f4702_rowid_docto == DocumentosInventario.f450_rowid_docto",
        secondaryjoin="DocumentosInventario.f450_ind_estado_cm == Estado.f054_id",
        foreign_keys="[DocumentosInventario.f450_rowid_docto, DocumentosInventario.f450_ind_estado_cm]",
        uselist=False,
        viewonly=True
    )

    
























