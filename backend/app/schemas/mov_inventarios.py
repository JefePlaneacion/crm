from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Schemas para relaciones anidadas
class BodegaBase(BaseModel):
    f150_id: int
    f150_descripcion: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class CodigoBase(BaseModel):
    f120_id: int
    f120_descripcion: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ConceptoBase(BaseModel):
    f145_id: int
    f145_descripcion: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class EstadoBase(BaseModel):
    f054_id: int
    f054_descripcion: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class DocumentoInventarioBase(BaseModel):
    f450_rowid_docto: int
    f450_id_clase_docto: Optional[int] = None
    f450_ind_estado_cm: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# Schema principal
class MovInventarioBase(BaseModel):
    id_movimiento: int
    id_bodega: Optional[int] = None
    id_docto: Optional[int] = None
    fecha_doc: Optional[datetime] = None
    tipo_docto: Optional[str] = None
    consecutivo_docto: Optional[int] = None
    estado: Optional[str] = None
    cod_ref: Optional[int] = None
    codigo_item: Optional[str] = None
    item: Optional[str] = None
    cantidad: Optional[float] = None
    costo_unitario: Optional[float] = None
    costo_total: Optional[float] = None
    usuario: Optional[str] = None
    bodega: Optional[str] = None
    codigo_bodega: Optional[str] = None
    concepto: Optional[str] = None
    