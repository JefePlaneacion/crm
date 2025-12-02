from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import List, Optional
import csv
import io

from app.db.session import get_db
from app.db.models import (
    MovInventario, Bodega, Codigos, DocumentosInventario, Estado, ClasesDocumento
)
from app.schemas.mov_inventarios import MovInventarioBase

router = APIRouter()

# Lista hardcodeada de conceptos
CONCEPTOS_FILTRO = [701, 511, 512, 602]

@router.get("/", response_model=List[MovInventarioBase])
def read_mov_inventarios(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Fecha inicial (ISO)"),
    end_date: Optional[datetime] = Query(None, description="Fecha final (ISO, exclusivo)"),
    limit: int = Query(10000, ge=1, le=100000, description="Límite de registros (default: 10000)"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    all: bool = Query(False, description="Si es true, ignora filtros de fecha"),
):
    """
    Obtiene movimientos de inventario con filtros y paginación.
    - Por defecto: últimos 90 días, límite 10k
    - all=true: ignora fechas pero usa paginación
    - Para 1.1M+ registros, usar paginación con offset/limit
    - Para exportar todo, usar el endpoint /export-csv
    """
    # Filtros de fecha por defecto (últimos 90 días) si no piden 'all' y no pasan fechas
    where_ = []
    if not all:
        if not start_date and not end_date:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)
        if start_date:
            where_.append(MovInventario.f470_ts >= start_date)
        if end_date:
            where_.append(MovInventario.f470_ts < end_date)

    # Query con joins explícitos
    q = (
        db.query(
            MovInventario.f470_ts.label("fecha_doc"),
            MovInventario.f470_id_cia.label("compania"),
            MovInventario.f470_rowid.label("id_docto"),
            DocumentosInventario.f450_rowid_docto.label("id_doc_row"),
            Estado.f054_descripcion.label("estado"),
            MovInventario.f470_id_concepto.label("concepto"),
            MovInventario.f470_rowid_item_ext.label("cod_ref"),
            Codigos.f120_referencia.label("codigo_item"),
            Codigos.f120_descripcion.label("item"),
            MovInventario.f470_id_unidad_medida.label("unidad"),
            MovInventario.f470_cant_base.label("cantidad"),
            MovInventario.f470_costo_prom_uni.label("costo_unitario"),
            MovInventario.f470_costo_prom_tot.label("costo_total"),
            Bodega.f150_descripcion.label("bodega"),
            Bodega.f150_id.label("codigo_bodega"),
        )
        .outerjoin(
            DocumentosInventario,
            MovInventario.f470_rowid_docto == DocumentosInventario.f450_rowid_docto
        )
        .outerjoin(
            ClasesDocumento,
            DocumentosInventario.f450_id_clase_docto == ClasesDocumento.f028_id
        )
        .outerjoin(
            Estado,
            and_(
                Estado.f054_id_grupo_clase_docto == ClasesDocumento.f028_id_grupo_clase_docto,
                Estado.f054_id == DocumentosInventario.f450_ind_estado_cm
            )
        )
        .outerjoin(
            Bodega,
            Bodega.f150_rowid == MovInventario.f470_rowid_bodega
        )
        .outerjoin(
            Codigos,
            Codigos.f120_id == MovInventario.f470_rowid_item_ext
        )
    )

    # Aplicar filtro de conceptos SIEMPRE
    q = q.filter(MovInventario.f470_id_concepto.in_(CONCEPTOS_FILTRO))

    # Aplicar otros filtros (fechas) si existen
    if where_:
        q = q.filter(and_(*where_))

    q = q.order_by(MovInventario.f470_ts.desc(), MovInventario.f470_rowid.desc()) \
         .limit(limit).offset(offset)

    rows = q.all()

    # Mapear a tu schema
    return [
        MovInventarioBase(
            fecha_doc=r.fecha_doc,
            compania=r.compania,
            id_docto=r.id_docto,
            estado=r.estado,
            concepto=r.concepto,
            id_doc_row=r.id_doc_row,
            cod_ref=r.cod_ref,
            codigo_item=(r.codigo_item.strip() if r.codigo_item else None),
            item=r.item,
            unidad=r.unidad,
            cantidad=float(r.cantidad) if r.cantidad is not None else None,
            costo_unitario=float(r.costo_unitario) if r.costo_unitario is not None else None,
            costo_total=float(r.costo_total) if r.costo_total is not None else None,
            bodega=r.bodega,
            codigo_bodega=r.codigo_bodega,
        )
        for r in rows
    ]


@router.get("/count")
def count_mov_inventarios(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Fecha inicial (ISO)"),
    end_date: Optional[datetime] = Query(None, description="Fecha final (ISO, exclusivo)"),
    all: bool = Query(False, description="Si es true, ignora filtros de fecha"),
):
    """
    Cuenta el total de registros de movimientos de inventario con los filtros aplicados.
    Útil para saber cuántos registros hay antes de exportar.
    """
    where_ = []
    
    if not all:
        if not start_date and not end_date:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)
        if start_date:
            where_.append(MovInventario.f470_ts >= start_date)
        if end_date:
            where_.append(MovInventario.f470_ts < end_date)
    
    # Query simple de conteo
    q = db.query(MovInventario.f470_rowid)
    
    # Aplicar filtro de conceptos SIEMPRE
    q = q.filter(MovInventario.f470_id_concepto.in_(CONCEPTOS_FILTRO))
    
    # Aplicar filtros de fecha si existen
    if where_:
        q = q.filter(and_(*where_))
    
    total = q.count()
    
    return {
        "total": total,
        "conceptos_filtrados": CONCEPTOS_FILTRO,
        "fecha_inicio": start_date.isoformat() if start_date else None,
        "fecha_fin": end_date.isoformat() if end_date else None,
        "all": all,
        "recomendacion": "Para exportar grandes volúmenes (>100k), usar /export-csv"
    }


@router.get("/export-csv")
def export_mov_inventarios_csv(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Fecha inicial (ISO)"),
    end_date: Optional[datetime] = Query(None, description="Fecha final (ISO, exclusivo)"),
    all: bool = Query(False, description="Si es true, ignora filtros de fecha"),
    chunk_size: int = Query(10000, ge=1000, le=50000, description="Tamaño de chunk para streaming"),
):
    """
    Exporta TODOS los movimientos de inventario a CSV usando streaming.
    Ideal para grandes volúmenes (1M+ registros).
    El archivo se descarga progresivamente sin saturar memoria.
    """
    where_ = []
    
    if not all:
        if not start_date and not end_date:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)
        if start_date:
            where_.append(MovInventario.f470_ts >= start_date)
        if end_date:
            where_.append(MovInventario.f470_ts < end_date)

    def generate_csv():
        """Generador que produce el CSV en chunks"""
        # Buffer para escribir CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        writer.writerow([
            'fecha_doc', 'compania', 'id_docto', 'id_doc_row', 'estado',
            'concepto', 'cod_ref', 'codigo_item', 'item', 'unidad',
            'cantidad', 'costo_unitario', 'costo_total', 'bodega', 'codigo_bodega'
        ])
        yield output.getvalue()
        output.truncate(0)
        output.seek(0)
        
        # Query base
        q = (
            db.query(
                MovInventario.f470_ts.label("fecha_doc"),
                MovInventario.f470_id_cia.label("compania"),
                MovInventario.f470_rowid.label("id_docto"),
                DocumentosInventario.f450_rowid_docto.label("id_doc_row"),
                Estado.f054_descripcion.label("estado"),
                MovInventario.f470_id_concepto.label("concepto"),
                MovInventario.f470_rowid_item_ext.label("cod_ref"),
                Codigos.f120_referencia.label("codigo_item"),
                Codigos.f120_descripcion.label("item"),
                MovInventario.f470_id_unidad_medida.label("unidad"),
                MovInventario.f470_cant_base.label("cantidad"),
                MovInventario.f470_costo_prom_uni.label("costo_unitario"),
                MovInventario.f470_costo_prom_tot.label("costo_total"),
                Bodega.f150_descripcion.label("bodega"),
                Bodega.f150_id.label("codigo_bodega"),
            )
            .outerjoin(
                DocumentosInventario,
                MovInventario.f470_rowid_docto == DocumentosInventario.f450_rowid_docto
            )
            .outerjoin(
                ClasesDocumento,
                DocumentosInventario.f450_id_clase_docto == ClasesDocumento.f028_id
            )
            .outerjoin(
                Estado,
                and_(
                    Estado.f054_id_grupo_clase_docto == ClasesDocumento.f028_id_grupo_clase_docto,
                    Estado.f054_id == DocumentosInventario.f450_ind_estado_cm
                )
            )
            .outerjoin(
                Bodega,
                Bodega.f150_rowid == MovInventario.f470_rowid_bodega
            )
            .outerjoin(
                Codigos,
                Codigos.f120_id == MovInventario.f470_rowid_item_ext
            )
        )
        
        # Aplicar filtros
        q = q.filter(MovInventario.f470_id_concepto.in_(CONCEPTOS_FILTRO))
        if where_:
            q = q.filter(and_(*where_))
        
        q = q.order_by(MovInventario.f470_ts.desc(), MovInventario.f470_rowid.desc())
        
        # Procesar en chunks usando yield_per
        offset = 0
        while True:
            chunk = q.limit(chunk_size).offset(offset).all()
            
            if not chunk:
                break
            
            # Escribir chunk al CSV
            for r in chunk:
                writer.writerow([
                    r.fecha_doc.isoformat() if r.fecha_doc else '',
                    r.compania or '',
                    r.id_docto or '',
                    r.id_doc_row or '',
                    r.estado or '',
                    r.concepto or '',
                    r.cod_ref or '',
                    r.codigo_item.strip() if r.codigo_item else '',
                    r.item or '',
                    r.unidad or '',
                    float(r.cantidad) if r.cantidad is not None else '',
                    float(r.costo_unitario) if r.costo_unitario is not None else '',
                    float(r.costo_total) if r.costo_total is not None else '',
                    r.bodega or '',
                    r.codigo_bodega or '',
                ])
            
            yield output.getvalue()
            output.truncate(0)
            output.seek(0)
            
            offset += chunk_size
            
            # Liberar memoria
            db.expire_all()
    
    # Nombre del archivo con timestamp
    filename = f"mov_inventarios_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export-json-chunks")
def export_mov_inventarios_json_chunks(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None, description="Fecha inicial (ISO)"),
    end_date: Optional[datetime] = Query(None, description="Fecha final (ISO, exclusivo)"),
    all: bool = Query(False, description="Si es true, ignora filtros de fecha"),
    chunk_size: int = Query(10000, ge=1000, le=50000, description="Tamaño de chunk"),
):
    """
    Exporta movimientos en chunks JSON (JSONL - JSON Lines).
    Cada línea es un objeto JSON válido.
    Ideal para procesamiento progresivo en frontend.
    """
    where_ = []
    
    if not all:
        if not start_date and not end_date:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)
        if start_date:
            where_.append(MovInventario.f470_ts >= start_date)
        if end_date:
            where_.append(MovInventario.f470_ts < end_date)

    def generate_jsonl():
        """Generador que produce JSONL (JSON Lines)"""
        # Query base (igual que CSV)
        q = (
            db.query(
                MovInventario.f470_ts.label("fecha_doc"),
                MovInventario.f470_id_cia.label("compania"),
                MovInventario.f470_rowid.label("id_docto"),
                DocumentosInventario.f450_rowid_docto.label("id_doc_row"),
                Estado.f054_descripcion.label("estado"),
                MovInventario.f470_id_concepto.label("concepto"),
                MovInventario.f470_rowid_item_ext.label("cod_ref"),
                Codigos.f120_referencia.label("codigo_item"),
                Codigos.f120_descripcion.label("item"),
                MovInventario.f470_id_unidad_medida.label("unidad"),
                MovInventario.f470_cant_base.label("cantidad"),
                MovInventario.f470_costo_prom_uni.label("costo_unitario"),
                MovInventario.f470_costo_prom_tot.label("costo_total"),
                Bodega.f150_descripcion.label("bodega"),
                Bodega.f150_id.label("codigo_bodega"),
            )
            .outerjoin(
                DocumentosInventario,
                MovInventario.f470_rowid_docto == DocumentosInventario.f450_rowid_docto
            )
            .outerjoin(
                ClasesDocumento,
                DocumentosInventario.f450_id_clase_docto == ClasesDocumento.f028_id
            )
            .outerjoin(
                Estado,
                and_(
                    Estado.f054_id_grupo_clase_docto == ClasesDocumento.f028_id_grupo_clase_docto,
                    Estado.f054_id == DocumentosInventario.f450_ind_estado_cm
                )
            )
            .outerjoin(
                Bodega,
                Bodega.f150_rowid == MovInventario.f470_rowid_bodega
            )
            .outerjoin(
                Codigos,
                Codigos.f120_id == MovInventario.f470_rowid_item_ext
            )
        )
        
        # Aplicar filtros
        q = q.filter(MovInventario.f470_id_concepto.in_(CONCEPTOS_FILTRO))
        if where_:
            q = q.filter(and_(*where_))
        
        q = q.order_by(MovInventario.f470_ts.desc(), MovInventario.f470_rowid.desc())
        
        # Procesar en chunks
        offset = 0
        while True:
            chunk = q.limit(chunk_size).offset(offset).all()
            
            if not chunk:
                break
            
            # Convertir cada registro a JSON y enviarlo
            for r in chunk:
                item = MovInventarioBase(
                    fecha_doc=r.fecha_doc,
                    compania=r.compania,
                    id_docto=r.id_docto,
                    estado=r.estado,
                    concepto=r.concepto,
                    id_doc_row=r.id_doc_row,
                    cod_ref=r.cod_ref,
                    codigo_item=(r.codigo_item.strip() if r.codigo_item else None),
                    item=r.item,
                    unidad=r.unidad,
                    cantidad=float(r.cantidad) if r.cantidad is not None else None,
                    costo_unitario=float(r.costo_unitario) if r.costo_unitario is not None else None,
                    costo_total=float(r.costo_total) if r.costo_total is not None else None,
                    bodega=r.bodega,
                    codigo_bodega=r.codigo_bodega,
                )
                # Cada línea es un JSON completo
                yield item.model_dump_json() + "\n"
            
            offset += chunk_size
            db.expire_all()
    
    return StreamingResponse(
        generate_jsonl(),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": "attachment; filename=mov_inventarios.jsonl"}
    )