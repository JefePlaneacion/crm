from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BodegaBase(BaseModel):
    id: Optional[int] = Field(alias="f150_rowid")
    codigo: Optional[str] = Field(alias="f150_id")
    descripcion: Optional[str] = Field(alias="f150_descripcion")
    descripcion_corta: Optional[str] = Field(alias="f150_descripcion_corta")
    class Config:
        from_attributes = True
        populate_by_name = True

class CodigosBase(BaseModel):
    id: Optional[int] = Field(alias="f120_id")
    referencia: Optional[str] = Field(alias="f120_referencia")
    descripcion: Optional[str] = Field(alias="f120_descripcion")
    unidad_inventario: Optional[str] = Field(alias="f120_id_unidad_inventario")
    class Config:
        from_attributes = True
        populate_by_name = True

class InventarioBase(BaseModel):
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


