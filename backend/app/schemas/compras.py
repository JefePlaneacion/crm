from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ESQUEMA DE MODELO COMPRAS

# BASE ORDENES DE COMPRA Y SOLICITUDES 

class Tipo_Doc_Base(BaseModel):
    Tipo_Documento: Optional[str] = Field(alias="f021_id")
    Descripcion_Documento:Optional[str] = Field(alias="f021_descripcion")
    class Config:
        from_attributes = True
        populate_by_name = True

class Estado_Doc_Base(BaseModel):
    Clase_Grupo_Doc: Optional[int] = Field(alias="f054_id_grupo_clase_docto")
    Numero_Estado: Optional[int] =Field(alias="f054_id")
    Descripcion_Estado: Optional[str]
    class Config:
        from_attributes = True
        populate_by_name = True

class Bodega_Base(BaseModel):
    id: Optional[int] = Field(alias="f150_rowid")
    codigo: Optional[str] = Field(alias="f150_id")
    descripcion: Optional[str] = Field(alias="f150_descripcion")
    descripcion_corta: Optional[str] = Field(alias="f150_descripcion_corta")
    class Config:
        from_attributes = True
        populate_by_name = True

class Codigos_Base(BaseModel):
    id: Optional[int] = Field(alias="f120_id")
    referencia: Optional[str] = Field(alias="f120_referencia")
    descripcion: Optional[str] = Field(alias="f120_descripcion")
    unidad_inventario: Optional[str] = Field(alias="f120_id_unidad_inventario")
    class Config:
        from_attributes = True
        populate_by_name = True

class Inventario_Base(BaseModel):
    id_item: Optional[int] = Field(alias="f400_rowid_item_ext")
    id_bodega: Optional[int] = Field(alias="f400_rowid_bodega")
    abc_costo: Optional[str] = Field(alias="f400_abc_rotacion_costo")
    abc_veces: Optional[str] = Field(alias="f400_abc_rotacion_veces")
    costo_unitario: Optional[float] = Field(alias="f400_costo_prom_uni")
    costo_total: Optional[float] = Field(alias="f400_costo_prom_tot")
    fecha_compra: Optional[datetime] = Field(alias="f400_fecha_ult_compra")
    fecha_entrada: Optional[datetime] = Field(alias="f400_fecha_ult_entrada")
    fecha_salida: Optional[datetime] = Field(alias="f400_fecha_ult_salida")
    existencia: Optional[float] = Field(alias="f400_cant_existencia_1")
    comprometida: Optional[float] = Field(alias="f400_cant_comprometida_1")
    pendiente_salir: Optional[float] = Field(alias="f400_cant_pendiente_salir_1")
    pendiente_entrar: Optional[float] = Field(alias="f400_cant_pendiente_entrar_1")

    bodega: Optional[str] = None
    item: Optional[str] = None
    codigo_item: Optional[str] = None
    codigo_bodega: Optional[str] = None
    
    

    class Config:
        from_attributes = True
        populate_by_name = True


class Doc_Compras_Base(BaseModel):
    id_doc:Optional[int]=Field(alias="f420_rowid")
    tipo_doc:Optional[str] = Field(alias="f420_id_tipo_docto")
    consecutivo_doc:Optional[int] = Field(alias="f420_consec_docto")
    fecha_doc: Optional[datetime] = Field(alias="f420_fecha")
    grupo_clase_doc: Optional[int] = Field(alias="f420_id_grupo_clase_docto")
    estado_num : Optional[int] = Field(alias="f420_ind_estado")
    id_solicitante: Optional[int] = Field(alias="f420_rowid_tercero_sol_comp")
    id_proveedor: Optional[int] = Field(alias="f420_rowid_tercero_prov")
    fecha_creacion: Optional[datetime] = Field(alias="f420_fecha_ts_creacion")
    fecha_aprobacion: Optional[datetime] = Field(alias="f420_fecha_ts_aprobacion")
    fecha_parcial: Optional[datetime] = Field(alias="f420_fecha_ts_parcial")
    fecha_cumplido: Optional[datetime] = Field(alias="f420_fecha_ts_cumplido")
    
    tipo_documento: Optional[str]=None
    estado_doc:Optional[str] = None
    clase_proveedor:Optional[str] = None
    items_compras_inventario: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class Items_Compras_Base(BaseModel):

    id_oc:Optional[int]=Field(alias="f421_rowid_oc_docto")
    id_item:Optional[int]=Field(alias="f421_rowid_item_ext")
    id_bodega:Optional[int]=Field(alias="f421_rowid_bodega")
    fecha:Optional[datetime]=Field(alias="f421_fecha")
    fecha_aprobacion: Optional[datetime]= None
    feha_parcial: Optional[datetime]= None  
    fecha_cumplido: Optional[datetime]= None
    id_unidad_medida: Optional[str]=Field(alias="f421_id_unidad_medida")
    cantidad_pedida: Optional[float]=Field(alias="f421_cant_pedida")
    cantidad_entrada: Optional[float]=Field(alias="f421_cant_entrada")
    id_estado: Optional[int]=Field(alias="f421_ind_estado")
    precio: Optional[float]=Field(alias="f421_precio_unitario")

    tipo_documento:Optional[str]=None
    documento_compra: Optional[int]= None

    items: Optional[str]= None
    bodegas: Optional[str]= None

    # Relación con t400_cm_existencia (Inventario)
    existencias:Optional[float] = None
    razon_social: Optional[str] = None
    estado_doc: Optional[str] = None

    centro_operacion: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True




    