from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
from app.db.session import get_db
from app.db.models import (
    TipoDocumento, Estado, DocumentoCompra, ItemsCompras,Codigos,Bodega,Proveedor,Inventario,CentroOperacion
)
from app.schemas.compras import Items_Compras_Base
from typing import List, Optional,Tuple
from datetime import date, datetime,timedelta
import asyncio
from functools import lru_cache

router = APIRouter()


# ===== VERSIÓN 1: OPTIMIZACIÓN SQL (Recomendada) =====
@router.get("/optimized", response_model=List[Items_Compras_Base])
def read_compras_optimized(
    db: Session = Depends(get_db),
    limit: int = Query(1000, le=5000),
    offset: int = Query(0, ge=0),
    fecha_inicio: Optional[date] = Query(None),
    fecha_final: Optional[date] = Query(None)
):
    """
    Versión optimizada con:
    - Paginación
    - Eager loading correcto
    - Query única sin loops
    - Filtros parametrizables
    - ORDER BY requerido por SQL Server
    """
    tipos_documentos_compras = ['OCI', 'OCC', 'OCS']
    fecha_inicio = fecha_inicio or date(2024, 6, 1)
    fecha_final = fecha_final or date.today()

    # Query optimizada con subquery para el estado
    # IMPORTANTE: SQL Server requiere ORDER BY cuando se usa LIMIT/OFFSET
    compras = (
        db.query(
            ItemsCompras,
            Estado.f054_descripcion.label('estado_descripcion')
        )
        .join(ItemsCompras.documento_compra)
        .outerjoin(
            Estado,
            (Estado.f054_id_grupo_clase_docto == DocumentoCompra.f420_id_grupo_clase_docto) &
            (Estado.f054_id == DocumentoCompra.f420_ind_estado)
        )
        .filter(DocumentoCompra.f420_id_tipo_docto.in_(tipos_documentos_compras))
        .filter(ItemsCompras.f421_fecha.between(fecha_inicio, fecha_final))
        .options(
            joinedload(ItemsCompras.bodegas),
            joinedload(ItemsCompras.items),
            joinedload(ItemsCompras.existencias),
            joinedload(ItemsCompras.documento_compra)
                .joinedload(DocumentoCompra.clase_proveedor)
        )
        .order_by(ItemsCompras.f421_fecha.desc(), ItemsCompras.f421_rowid_oc_docto)  # REQUERIDO por MSSQL
        .limit(limit)
        .offset(offset)
        .all()  # Solo llamar .all() UNA VEZ
    )

    result = []
    for comp, estado_desc in compras:
        # Extraer relaciones (más eficiente que tu versión)
        bodega = comp.bodegas[0].f150_descripcion if comp.bodegas else None
        item = comp.items[0].f120_descripcion.strip() if comp.items else None
        existencia = comp.existencias[0].f400_cant_existencia_1 if comp.existencias else None

        # Proveedor
        razon_social = None
        if comp.documento_compra and comp.documento_compra.clase_proveedor:
            razon_social = (comp.documento_compra.clase_proveedor.f200_razon_social or "").strip()

        result.append({
            "id_oc": comp.f421_rowid_oc_docto,
            "id_item": comp.f421_rowid_item_ext,
            "id_bodega": comp.f421_rowid_bodega,
            "fecha": comp.f421_fecha,
            "fecha_aprobacion": getattr(comp.documento_compra, "f420_fecha_ts_aprobacion", None),
            "feha_parcial": getattr(comp.documento_compra, "f420_fecha_ts_parcial", None),
            "fecha_cumplido": getattr(comp.documento_compra, "f420_fecha_ts_cumplido", None),
            "id_unidad_medida": (comp.f421_id_unidad_medida or "").strip(),
            "cantidad_pedida": comp.f421_cant_pedida,
            "cantidad_entrada": comp.f421_cant_entrada,
            "id_estado": comp.f421_ind_estado,
            "precio": comp.f421_precio_unitario,
            "tipo_documento": getattr(comp.documento_compra, "f420_id_tipo_docto", None),
            "documento_compra": getattr(comp.documento_compra, "f420_consec_docto", None),
            "estado_doc": estado_desc,
            "bodegas": bodega,
            "items": item,
            "existencias": existencia,
            "razon_social": razon_social
        })

    return result


# ===== VERSIÓN SIMPLE: Sin paginación (para datasets pequeños) =====
@router.get("/simple", response_model=List[Items_Compras_Base])
def read_compras_simple(
    db: Session = Depends(get_db),
    fecha_inicio: Optional[date] = Query(date(2024, 6, 1)),
    fecha_final: Optional[date] = Query(None)
):
    """
    Versión simple sin paginación - usa esta si tienes menos de 10k registros
    Más rápida que la original porque:
    - Elimina el query de Estado dentro del loop
    - Corrige el bug de .all() duplicado
    """
    tipos_documentos_compras = ['OCI', 'OCC', 'OCS']
    fecha_final = fecha_final or date.today()

    compras = (
        db.query(
            ItemsCompras,
            Estado.f054_descripcion.label('estado_descripcion')
        )
        .join(ItemsCompras.documento_compra)
        .outerjoin(
            Estado,
            (Estado.f054_id_grupo_clase_docto == DocumentoCompra.f420_id_grupo_clase_docto) &
            (Estado.f054_id == DocumentoCompra.f420_ind_estado)
        )
        .filter(DocumentoCompra.f420_id_tipo_docto.in_(tipos_documentos_compras))
        .filter(ItemsCompras.f421_fecha.between(fecha_inicio, fecha_final))
        .options(
            joinedload(ItemsCompras.bodegas),
            joinedload(ItemsCompras.items),
            joinedload(ItemsCompras.existencias),
            joinedload(ItemsCompras.documento_compra)
                .joinedload(DocumentoCompra.clase_proveedor)
        )
        .order_by(ItemsCompras.f421_fecha.desc())  # Para consistencia de resultados
        .all()
    )

    result = []
    for comp, estado_desc in compras:
        bodega = comp.bodegas[0].f150_descripcion if comp.bodegas else None
        item = comp.items[0].f120_descripcion.strip() if comp.items else None
        existencia = comp.existencias[0].f400_cant_existencia_1 if comp.existencias else None

        razon_social = None
        if comp.documento_compra and comp.documento_compra.clase_proveedor:
            razon_social = (comp.documento_compra.clase_proveedor.f200_razon_social or "").strip()

        result.append({
            "id_oc": comp.f421_rowid_oc_docto,
            "id_item": comp.f421_rowid_item_ext,
            "id_bodega": comp.f421_rowid_bodega,
            "fecha": comp.f421_fecha,
            "fecha_aprobacion": getattr(comp.documento_compra, "f420_fecha_ts_aprobacion", None),
            "feha_parcial": getattr(comp.documento_compra, "f420_fecha_ts_parcial", None),
            "fecha_cumplido": getattr(comp.documento_compra, "f420_fecha_ts_cumplido", None),
            "id_unidad_medida": (comp.f421_id_unidad_medida or "").strip(),
            "cantidad_pedida": comp.f421_cant_pedida,
            "cantidad_entrada": comp.f421_cant_entrada,
            "id_estado": comp.f421_ind_estado,
            "precio": comp.f421_precio_unitario,
            "tipo_documento": getattr(comp.documento_compra, "f420_id_tipo_docto", None),
            "documento_compra": getattr(comp.documento_compra, "f420_consec_docto", None),
            "estado_doc": estado_desc,
            "bodegas": bodega,
            "items": item,
            "existencias": existencia,
            "razon_social": razon_social
        })

    return result


# ===== VERSIÓN 2: CON CACHE (Para reportes frecuentes) =====
from cachetools import TTLCache
from hashlib import md5

# Cache de 5 minutos para queries repetidas
query_cache = TTLCache(maxsize=100, ttl=300)

@router.get("/cached", response_model=List[Items_Compras_Base])
def read_compras_cached(
    db: Session = Depends(get_db),
    fecha_inicio: date = Query(date(2024, 6, 1)),
    fecha_final: date = Query(date.today())
):
    """Versión con cache para consultas repetidas"""
    cache_key = f"{fecha_inicio}_{fecha_final}"
    
    if cache_key in query_cache:
        return query_cache[cache_key]
    
    # Usar la función optimizada
    result = read_compras_optimized(
        db=db,
        limit=5000,
        offset=0,
        fecha_inicio=fecha_inicio,
        fecha_final=fecha_final
    )
    
    query_cache[cache_key] = result
    return result


# ===== VERSIÓN 3: RESPUESTA STREAMING (Para datasets grandes) =====
from fastapi.responses import StreamingResponse
import json

@router.get("/stream")
def read_compras_stream(
    db: Session = Depends(get_db),
    batch_size: int = Query(500, le=1000)
):
    """
    Streaming para datasets muy grandes
    Envía datos en chunks sin cargar todo en memoria
    """
    def generate():
        tipos_documentos_compras = ['OCI', 'OCC', 'OCS']
        fecha_inicio = date(2024, 6, 1)
        fecha_final = date.today()
        
        offset = 0
        yield '{"data":['
        
        first = True
        while True:
            batch = (
                db.query(ItemsCompras)
                .join(ItemsCompras.documento_compra)
                .filter(DocumentoCompra.f420_id_tipo_docto.in_(tipos_documentos_compras))
                .filter(ItemsCompras.f421_fecha.between(fecha_inicio, fecha_final))
                .options(
                    joinedload(ItemsCompras.bodegas),
                    joinedload(ItemsCompras.items),
                    joinedload(ItemsCompras.existencias),
                    joinedload(ItemsCompras.documento_compra)
                        .joinedload(DocumentoCompra.clase_proveedor)
                )
                .order_by(ItemsCompras.f421_fecha.desc())  # REQUERIDO por MSSQL
                .limit(batch_size)
                .offset(offset)
                .all()
            )
            
            if not batch:
                break
                
            for comp in batch:
                if not first:
                    yield ','
                first = False
                
                # Serializar item
                item_data = {
                    "id_oc": comp.f421_rowid_oc_docto,
                    "cantidad_pedida": comp.f421_cant_pedida,
                    # ... otros campos
                }
                yield json.dumps(item_data)
            
            offset += batch_size
        
        yield ']}'
    
    return StreamingResponse(
        generate(),
        media_type="application/json"
    )


# ===== SOBRE PARQUET =====
"""
PARQUET: Útil para reportes/análisis, NO para APIs en tiempo real

Casos de uso para Parquet:
1. Exportación de datos históricos
2. Data warehousing
3. Análisis con pandas/polars
4. Integración con herramientas BI

Ejemplo de endpoint de exportación:
"""

@router.get("/export/parquet")
def export_compras_parquet(db: Session = Depends(get_db)):
    """Exporta datos a Parquet para análisis"""
    import pandas as pd
    import pyarrow.parquet as pq
    from io import BytesIO
    
    # Obtener datos
    compras = read_compras_optimized(db=db, limit=50000, offset=0)
    
    # Convertir a DataFrame
    df = pd.DataFrame(compras)
    
    # Guardar en memoria como Parquet
    buffer = BytesIO()
    df.to_parquet(buffer, engine='pyarrow', compression='snappy')
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=compras_{date.today()}.parquet"}
    )


# ===== ÍNDICES RECOMENDADOS EN LA BASE DE DATOS =====
"""
Para máximo rendimiento, crear estos índices en tu BD:

CREATE INDEX idx_items_compras_fecha ON items_compras(f421_fecha);
CREATE INDEX idx_items_compras_oc ON items_compras(f421_rowid_oc_docto);
CREATE INDEX idx_doc_compra_tipo ON documento_compra(f420_id_tipo_docto);
CREATE INDEX idx_doc_compra_estado ON documento_compra(f420_id_grupo_clase_docto, f420_ind_estado);
CREATE INDEX idx_estado_compuesto ON estado(f054_id_grupo_clase_docto, f054_id);
"""
# Función para mapear los resultados (necesitamos un mapeo explícito ya que no usamos objetos)
def map_to_response_model(row: Tuple) -> dict:
    """
    Mapea la tupla de resultados SQL (scalar) a la estructura del diccionario/schema.
    El orden de las columnas debe coincidir con el orden en la cláusula .query().
    """
    (
        id_oc, id_item, id_bodega, fecha, unidad_medida, 
        cant_pedida, cant_entrada, id_estado, precio, 
        tipo_documento, consec_docto, fecha_aprobacion, 
        feha_parcial, fecha_cumplido, 
        estado_desc, item_desc, bodega_desc, existencia_cant, razon_social,Centro_operacion
    ) = row

    return {
        # ItemsCompras
        "id_oc": id_oc,
        "id_item": id_item,
        "id_bodega": id_bodega,
        "fecha": fecha,
        "id_unidad_medida": (unidad_medida or "").strip(),
        "cantidad_pedida": cant_pedida,
        "cantidad_entrada": cant_entrada,
        "id_estado": id_estado,
        "precio": precio,

        # DocumentoCompra
        "tipo_documento": tipo_documento,
        "documento_compra": consec_docto,
        "fecha_aprobacion": fecha_aprobacion,
        "feha_parcial": feha_parcial,
        "fecha_cumplido": fecha_cumplido,
        
        # JOINS
        "estado_doc": estado_desc, 
        "items": (item_desc or "").strip(),
        "bodegas": bodega_desc,
        "existencias": existencia_cant,
        "razon_social": (razon_social or "").strip(),
        "centro_operacion": (Centro_operacion or "").strip()
    }


@router.get("/solicitudes_carga_escalar", response_model=List[Items_Compras_Base])
def read_compras_carga_escalar(
    db: Session = Depends(get_db),
    limit: int = Query(1000, le=5000), 
    offset: int = Query(0, ge=0),
):
    """
    Endpoint de Solicitudes optimizado para CARGA ESCALAR (máximo rendimiento sin índices).
    Evita la costosa "Hidratación de Objetos" de SQLAlchemy.
    """
    
    tipos_documentos_compras = ['SIC', 'SC']
    
    # === CÁLCULO DEL RANGO TEMPORAL (90 DÍAS) ===
    fecha_final = date.today()
    fecha_inicio = fecha_final - timedelta(days=90)
    fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time()) 
    
    # === FASE SQL: CARGA ESCALAR CON JOINS EXPLÍCITOS ===
    # Seleccionamos explícitamente CADA columna que necesitamos.
    # El rendimiento mejora porque la base de datos y Python solo manejan tuplas de datos simples.
    query_cols = (
        # Columnas de la tabla principal (ItemsCompras)
        ItemsCompras.f421_rowid_oc_docto.label('id_oc'),
        ItemsCompras.f421_rowid_item_ext.label('id_item'),
        ItemsCompras.f421_rowid_bodega.label('id_bodega'),
        ItemsCompras.f421_fecha.label('fecha'),
        ItemsCompras.f421_id_unidad_medida.label('unidad_medida'),
        ItemsCompras.f421_cant_pedida.label('cant_pedida'),
        ItemsCompras.f421_cant_entrada.label('cant_entrada'),
        ItemsCompras.f421_ind_estado.label('id_estado'),
        ItemsCompras.f421_precio_unitario.label('precio'),

        # Columnas de DocumentoCompra (JOIN 1)
        DocumentoCompra.f420_id_tipo_docto.label('tipo_documento'),
        DocumentoCompra.f420_consec_docto.label('consec_docto'),
        DocumentoCompra.f420_fecha_ts_aprobacion.label('fecha_aprobacion'),
        DocumentoCompra.f420_fecha_ts_parcial.label('feha_parcial'),
        DocumentoCompra.f420_fecha_ts_cumplido.label('fecha_cumplido'),
        
        # Columnas de Estado (JOIN 2 - Eliminación N+1)
        Estado.f054_descripcion.label('estado_desc'),
        
        # Columnas de Codigos/Items (JOIN 3)
        Codigos.f120_descripcion.label('item_desc'),
        
        # Columnas de Bodega (JOIN 4)
        Bodega.f150_descripcion.label('bodega_desc'),
        
        # Columnas de Inventario (JOIN 5 - Clave compuesta: asumo un JOIN LEFT)
        Inventario.f400_cant_existencia_1.label('existencia_cant'),
        
        # Columnas de Proveedor (JOIN 6)
        Proveedor.f200_razon_social.label('razon_social'),

        CentroOperacion.f285_descripcion.label('centro_operacion')
    )
    
    query = (
        db.query(*query_cols)
        # JOINs explícitos para cargar todos los datos en UNA consulta
        .join(DocumentoCompra, ItemsCompras.f421_rowid_oc_docto == DocumentoCompra.f420_rowid)
        # JOIN Estado
        .outerjoin(
            Estado,
            (Estado.f054_id_grupo_clase_docto == DocumentoCompra.f420_id_grupo_clase_docto) &
            (Estado.f054_id == DocumentoCompra.f420_ind_estado)
        )
        # JOIN Items
        .outerjoin(Codigos, ItemsCompras.f421_rowid_item_ext == Codigos.f120_id)
        # JOIN Bodega
        .outerjoin(Bodega, ItemsCompras.f421_rowid_bodega == Bodega.f150_rowid)
        # JOIN Inventario (JOIN de clave compuesta)
        .outerjoin(
            Inventario, 
            (Inventario.f400_rowid_item_ext == ItemsCompras.f421_rowid_item_ext) &
            (Inventario.f400_rowid_bodega == ItemsCompras.f421_rowid_bodega)
        )
        # JOIN Proveedor
        .outerjoin(Proveedor, DocumentoCompra.f420_rowid_tercero_prov == Proveedor.f200_rowid)
        .outerjoin(
            CentroOperacion,
            (CentroOperacion.f285_id == DocumentoCompra.f420_id_co) &
            (CentroOperacion.f285_id_cia == DocumentoCompra.f420_id_cia)
        )

        # FILTROS
        .filter(ItemsCompras.f421_fecha >= fecha_inicio_dt) 
        .filter(DocumentoCompra.f420_id_tipo_docto.in_(tipos_documentos_compras))
        
        # ORDENAMIENTO Y PAGINACIÓN
        .order_by(ItemsCompras.f421_fecha.desc(), ItemsCompras.f421_rowid_oc_docto)
        .limit(limit)
        .offset(offset)
        .all()
    )

    # === FASE PYTHON: Mapeo de Tuplas a Diccionarios ===
    # El mapeo de tuplas es mucho más rápido que la hidratación de objetos
    return [map_to_response_model(row) for row in query]