from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint, and_
from sqlalchemy.orm import relationship
from app.db.session import Base

# TIPOS DE DOCUMENTOS
class TipoDocumento(Base):
    __tablename__ = "t021_mm_tipos_documentos"
    f021_id = Column(String(5), primary_key=True, index=True)
    f021_descripcion = Column(String(100), nullable=True)
    documento_compra = relationship("DocumentoCompra", back_populates="tipo_documento", lazy="selectin")

# ESTADOS
class Estado(Base):
    __tablename__ = "t054_mm_estados"
    f054_id_grupo_clase_docto = Column(Integer, nullable=True, index=True)
    f054_id = Column(Integer, primary_key=True, index=True)
    f054_descripcion = Column(String(100), nullable=True)

    documentos_por_estado = relationship(
        "DocumentoCompra",
        back_populates="estado_doc",
        foreign_keys="[DocumentoCompra.f420_ind_estado]",
        primaryjoin="Estado.f054_id == DocumentoCompra.f420_ind_estado",
        lazy="selectin",
    )
    documentos_por_grupo = relationship(
        "DocumentoCompra",
        back_populates="estado_grupo",
        primaryjoin="Estado.f054_id_grupo_clase_docto == DocumentoCompra.f420_id_grupo_clase_docto",
        foreign_keys="[DocumentoCompra.f420_id_grupo_clase_docto]",
        viewonly=True,
        lazy="selectin",
    )

# INVENTARIO
class Inventario(Base):
    __tablename__ = "t400_cm_existencia"
    __table_args__ = (PrimaryKeyConstraint('f400_rowid_item_ext', 'f400_rowid_bodega'),)
    f400_rowid_item_ext = Column(Integer, ForeignKey("t120_mc_items.f120_id"), nullable=True)
    f400_rowid_bodega = Column(Integer, ForeignKey("t150_mc_bodegas.f150_rowid"), nullable=True)
    f400_abc_rotacion_costo = Column(String(10), nullable=True)
    f400_abc_rotacion_veces = Column(String(10), nullable=True)
    f400_costo_prom_uni = Column(Float, nullable=True)
    f400_costo_prom_tot = Column(Float, nullable=True)
    f400_fecha_ult_compra = Column(DateTime, nullable=True)
    f400_fecha_ult_entrada = Column(DateTime, nullable=True)
    f400_fecha_ult_salida = Column(DateTime, nullable=True)
    f400_cant_existencia_1 = Column(Float, nullable=True)
    f400_cant_comprometida_1 = Column(Float, nullable=True)
    f400_cant_pendiente_salir_1 = Column(Float, nullable=True)
    f400_cant_pendiente_entrar_1 = Column(Float, nullable=True)

    items = relationship("Codigos", back_populates="existencias", lazy="selectin")
    bodegas = relationship("Bodega", back_populates="existencias", lazy="selectin")
    # 🔧 Evitar selectinload con clave compuesta (genera tuple IN)
    items_compras_inventario = relationship(
        "ItemsCompras",
        back_populates="existencias",
        lazy="noload",                 # << clave
        overlaps="items_compras_inventario,bodegas,items"
    )

# BODEGA
class Bodega(Base):
    __tablename__ = "t150_mc_bodegas"
    f150_rowid = Column(Integer, primary_key=True, index=True)
    f150_id = Column(String(10), nullable=True)
    f150_descripcion = Column(String(150), nullable=True)
    f150_descripcion_corta = Column(String(150), nullable=True)

    existencias = relationship("Inventario", back_populates="bodegas", lazy="selectin")
    # 🔧 Evitar selectinload aquí también
    items_compras_inventario = relationship(
        "ItemsCompras",
        back_populates="bodegas",
        lazy="noload",                 # << clave
        overlaps="items_compras_inventario,existencias"
    )
    bod_inv = relationship("MovInventario", back_populates="mov_bodegas", lazy="selectin")
# CODIGOS/ITEMS
class Codigos(Base):
    __tablename__ = "t120_mc_items"
    f120_id = Column(Integer, primary_key=True, index=True)
    f120_referencia = Column(String(50), nullable=True, index=True)
    f120_descripcion = Column(String(255), nullable=True)
    f120_id_unidad_inventario = Column(String(10), nullable=True)

    existencias = relationship("Inventario", back_populates="items", lazy="selectin")
    # 🔧 Evitar selectinload (tupla IN)
    items_compras_inventario = relationship(
        "ItemsCompras",
        back_populates="items",
        foreign_keys="[ItemsCompras.f421_rowid_item_ext]",
        lazy="noload",                 # << clave
        overlaps="items_compras_inventario,existencias"
    )
    cod_mov_inventario = relationship("MovInventario", back_populates="mov_items", foreign_keys="[MovInventario.f470_rowid_item_ext]", lazy="selectin")

# PROVEEDOR / TIPO PROVEEDOR
class TipoProveedor(Base):
    __tablename__ = "t209_mm_clase_proveedor"
    f209_id = Column(String(10), primary_key=True, index=True)
    f209_descripcion = Column(String(100), nullable=True)
   
class Proveedor(Base):
    __tablename__ = "t200_mm_terceros"
    f200_rowid = Column(Integer, primary_key=True, index=True)
    f200_nit = Column(String(150), nullable=True)
    f200_razon_social = Column(String(255), nullable=True)
    
    documento_compra = relationship("DocumentoCompra", back_populates="clase_proveedor",
                                    foreign_keys=lambda: [DocumentoCompra.f420_rowid_tercero_prov],
                                    uselist=True, lazy="selectin")

class CentroOperacion(Base):
    __tablename__ = "t285_co_centro_op"
    f285_id_cia= Column(Integer, nullable=True)
    f285_id = Column(String(10), primary_key=True, index=True)
    f285_descripcion = Column(String(150), nullable=True)

    documentos_compra = relationship("DocumentoCompra", back_populates="centro_operacion", lazy="joined")

# DOC COMPRA
class DocumentoCompra(Base):
    __tablename__ = "t420_cm_oc_docto"
    __table_args__ = (
        ForeignKeyConstraint(
            # Columnas de la tabla hija
            ['f420_id_cia', 'f420_id_co'],
            # Columnas de la tabla padre
            ['t285_co_centro_op.f285_id_cia', 't285_co_centro_op.f285_id']
        ),
    )
    f420_rowid = Column(Integer, primary_key=True, index=True)
    f420_id_cia=Column(Integer, nullable=True)
    f420_id_co=Column(String(10), nullable=True)
    f420_id_tipo_docto = Column(String(4), ForeignKey("t021_mm_tipos_documentos.f021_id"), index=True)
    f420_consec_docto = Column(Integer, index=True)
    f420_fecha = Column(DateTime, nullable=True)
    f420_id_grupo_clase_docto = Column(Integer, nullable=True)
    f420_ind_estado = Column(Integer, ForeignKey("t054_mm_estados.f054_id"), index=True, nullable=True)
    f420_rowid_tercero_sol_comp = Column(Integer, nullable=True)
    f420_rowid_tercero_prov = Column(Integer, ForeignKey("t200_mm_terceros.f200_rowid"), index=True, nullable=True)
    f420_fecha_ts_creacion = Column(DateTime, nullable=True)
    f420_fecha_ts_aprobacion = Column(DateTime, nullable=True)
    f420_fecha_ts_parcial = Column(DateTime, nullable=True)
    f420_fecha_ts_cumplido = Column(DateTime, nullable=True)

    tipo_documento = relationship("TipoDocumento", back_populates="documento_compra", lazy="selectin")
    estado_doc = relationship("Estado", back_populates="documentos_por_estado",
                              foreign_keys=[f420_ind_estado],
                              primaryjoin="DocumentoCompra.f420_ind_estado == Estado.f054_id",
                              uselist=False, lazy="selectin")
    estado_grupo = relationship("Estado", back_populates="documentos_por_grupo",
                                foreign_keys=[f420_id_grupo_clase_docto],
                                primaryjoin="DocumentoCompra.f420_id_grupo_clase_docto == Estado.f054_id_grupo_clase_docto",
                                uselist=False, viewonly=True, lazy="selectin")
    clase_proveedor = relationship("Proveedor", back_populates="documento_compra",
                                   foreign_keys=[f420_rowid_tercero_prov], uselist=False, lazy="selectin")
    items_compras_inventario = relationship(
        "ItemsCompras",
        back_populates="documento_compra",
        lazy="joined",               # << antes: default/selectin -> ahora JOIN
        overlaps="items,bodegas,existencias"
    )

    # NUEVA RELACIÓN: Centro de Operación
    centro_operacion = relationship(
        "CentroOperacion",
        # 1. Condición de JOIN compuesta para el WHERE/ON de SQL
        primaryjoin=and_(
            CentroOperacion.f285_id == f420_id_co,
            CentroOperacion.f285_id_cia == f420_id_cia
        ),
        # 2. Definición de las columnas que actúan como Foreign Key
        foreign_keys=[f420_id_cia, f420_id_co],
        
        back_populates="documentos_compra",
        uselist=False, # Uno a Uno/Muchos
        lazy="joined"
    )

# ITEMS COMPRA
class ItemsCompras(Base):
    __tablename__ = "t421_cm_oc_movto"
    __table_args__ = (
        PrimaryKeyConstraint("f421_rowid_oc_docto", "f421_rowid_item_ext", "f421_rowid_bodega"),
        ForeignKeyConstraint(
            ["f421_rowid_item_ext", "f421_rowid_bodega"],
            ["t400_cm_existencia.f400_rowid_item_ext", "t400_cm_existencia.f400_rowid_bodega"]
        ),
    )
    f421_rowid_oc_docto = Column(Integer, ForeignKey("t420_cm_oc_docto.f420_rowid"), index=True)
    f421_rowid_item_ext = Column(Integer, ForeignKey("t120_mc_items.f120_id"))
    f421_rowid_bodega = Column(Integer, ForeignKey("t150_mc_bodegas.f150_rowid"), index=True)
    f421_fecha = Column(DateTime, nullable=True)
    f421_id_unidad_medida = Column(String(5), nullable=True)
    f421_cant_pedida = Column(Float, nullable=True)
    f421_cant_entrada = Column(Float, nullable=True)
    f421_ind_estado = Column(Integer, nullable=True)
    f421_precio_unitario = Column(Float, nullable=True)

    documento_compra = relationship("DocumentoCompra", back_populates="items_compras_inventario", foreign_keys=[f421_rowid_oc_docto], uselist=False, lazy="selectin")
    items = relationship(
        "Codigos",
        back_populates="items_compras_inventario",
        overlaps="existencias,items_compras_inventario",
        foreign_keys=[f421_rowid_item_ext],
        uselist=True,
        lazy="joined"                # << antes: selectin
    )
    bodegas = relationship(
        "Bodega",
        back_populates="items_compras_inventario",
        overlaps="items_compras_inventario,existencias",
        uselist=True,
        lazy="joined"                # << antes: selectin
    )
    existencias = relationship(
        "Inventario",
        back_populates="items_compras_inventario",
        overlaps="bodegas,items_compras_inventario",
        uselist=True,
        lazy="noload"                # mantener noload (compuesta-compuesta)
    )
# CONCEPTOS
class Conceptos(Base):
    __tablename__ = "t145_mc_conceptos"
    f145_id = Column(Integer, primary_key=True, index=True)
    f145_descripcion = Column(String(150), nullable=True)

# CLASES DOCUMENTO
class ClasesDocumento(Base):
    __tablename__ = "t028_mm_clases_documento"
    f028_id = Column(Integer, primary_key=True, index=True)
    f028_descripcion = Column(String(100), nullable=True)
    f028_id_grupo_clase_docto = Column(Integer, nullable=True, index=True)
    documentos_inventario = relationship("DocumentosInventario", back_populates="clase_documento", lazy="selectin")

# DOC INVENTARIO
class DocumentosInventario(Base):
    __tablename__ = "t450_cm_docto_invent"
    f450_ts = Column(DateTime, nullable=True)
    f450_rowid_docto = Column(Integer, primary_key=True, index=True)
    f450_id_clase_docto = Column(Integer, ForeignKey("t028_mm_clases_documento.f028_id"), nullable=True, index=True)
    f450_id_concepto = Column(Integer, ForeignKey("t145_mc_conceptos.f145_id"), index=True)
    f450_ind_estado_cm = Column(Integer, ForeignKey("t054_mm_estados.f054_id"), nullable=True, index=True)

    clase_documento = relationship("ClasesDocumento", back_populates="documentos_inventario", lazy="selectin")
    doc_inv = relationship("MovInventario", back_populates="mov_doc", lazy="selectin")
    estado = relationship("Estado", uselist=False, viewonly=True, lazy="selectin")

# MOV INVENTARIO
class MovInventario(Base):
    __tablename__ = "t470_cm_movto_invent"
    f470_ts = Column(DateTime, nullable=True, index=True)
    f470_id_cia = Column(Integer, nullable=True, index=True)
    f470_rowid = Column(Integer, primary_key=True, nullable=True)
    f470_rowid_docto = Column(Integer, ForeignKey("t450_cm_docto_invent.f450_rowid_docto"), nullable=True, index=True)
    f470_rowid_item_ext = Column(Integer, ForeignKey("t120_mc_items.f120_id"), nullable=True, index=True)
    f470_rowid_bodega = Column(Integer, ForeignKey("t150_mc_bodegas.f150_rowid"), nullable=True, index=True)
    f470_id_periodo = Column(Integer, nullable=True)
    f470_ind_estado_cm = Column(Integer, nullable=True)
    f470_id_concepto = Column(Integer, nullable=True)
    f470_id_unidad_medida = Column(String, nullable=True)
    f470_cant_base = Column(Integer, nullable=True)
    f470_costo_prom_uni = Column(Integer, nullable=True)
    f470_costo_prom_tot = Column(Integer, nullable=True)

    mov_doc = relationship("DocumentosInventario", back_populates="doc_inv", lazy="selectin")
    mov_bodegas = relationship("Bodega", back_populates="bod_inv", lazy="selectin")
    mov_items = relationship("Codigos", back_populates="cod_mov_inventario", lazy="selectin")


    
























