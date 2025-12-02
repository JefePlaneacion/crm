from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Schemas para relaciones anidadas (si los usas en otras respuestas)
class BodegaBase(BaseModel):
    # f150_id es String(10) en el modelo -> str aquí
    f150_id: Optional[str] = None
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

# Schema principal devuelto por el endpoint
class MovInventarioBase(BaseModel):
    fecha_doc: Optional[datetime] = None
    compania: Optional[int] = None
    id_docto: Optional[int] = None
    estado: Optional[str] = None
    concepto: Optional[int] = None
    id_doc_row: Optional[int] = None
    cod_ref: Optional[int] = None          # rowid del item_ext (entero)
    codigo_item: Optional[str] = None      # referencia del item (texto)
    item: Optional[str] = None
    unidad: Optional[str] = None
    cantidad: Optional[float] = None
    costo_unitario: Optional[float] = None
    costo_total: Optional[float] = None
    bodega: Optional[str] = None
    codigo_bodega: Optional[str] = None    # f150_id es texto

    model_config = ConfigDict(from_attributes=True)
