from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session,joinedload
from app.db.session import get_db
from app.db.models import MovInventario,Bodega,Codigos,DocumentosInventario,Estado,ClasesDocumento
from app.schemas.mov_inventarios import MovInventarioBase
from sqlalchemy import and_
from typing import List
import json

router = APIRouter()

@router.get("/", response_model=List[MovInventarioBase])

def read_mov_inventarios(db: Session = Depends(get_db)):

    mov_inventarios = (
        db.query(
            MovInventario,
            Estado.f054_descripcion.label('estado_descripcion')
        )
        .outerjoin(
            DocumentosInventario,
            MovInventario.f4702_rowid_docto == DocumentosInventario.f450_rowid_docto
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
        .options(
            joinedload(MovInventario.mov_bodegas),
            joinedload(MovInventario.mov_items),
            joinedload(MovInventario.concepto_mov),
        )
        .all()
    )

    
    result = []
    for mov, estado_desc in mov_inventarios:

        '''
            estado_desc = None

                # Obtener el estado correcto usando el grupo de clase de documento
        if mov.mov_doc and mov.mov_doc.clase_documento:
            # Buscar estado que coincida con:
            # - f054_id_grupo_clase_docto == ClasesDocumento.f028_id_grupo_clase_docto
            # - f054_id == DocumentosInventario.f450_ind_estado_cm
            grupo_clase = mov.mov_doc.clase_documento.f028_id_grupo_clase_docto
            ind_estado = mov.mov_doc.f450_ind_estado_cm
            
            if grupo_clase is not None and ind_estado is not None:
                estado = db.query(Estado).filter(
                    Estado.f054_id_grupo_clase_docto == grupo_clase,
                    Estado.f054_id == ind_estado
                ).first()
                
                if estado:
                    estado_desc = estado.f054_descripcion
        '''
        
        

        result.append(MovInventarioBase(
            id_movimiento=mov.f4702_rowid_movto,
            id_bodega=mov.f4702_rowid_bodega,
            id_docto=mov.f4702_rowid_docto,
            fecha_doc=mov.f4702_ts,
            tipo_docto= mov.f4702_id_tipo,
            consecutivo_docto= mov.f4702_consec_docto,
            estado=estado_desc,
            cod_ref=mov.f4702_rowid_item_ext,
            codigo_item=mov.mov_items.f120_referencia.strip() if mov.mov_items and hasattr(mov.mov_items, 'f120_referencia') else None,
            item=mov.mov_items.f120_descripcion if mov.mov_items and hasattr(mov.mov_items, 'f120_descripcion') else None,
            cantidad=mov.f4702_cant_1,
            costo_unitario=mov.f4702_costo_prom_uni,
            costo_total=mov.f4702_costo_prom_tot,
            usuario=mov.f4702_usuario,
            bodega=mov.mov_bodegas.f150_descripcion if mov.mov_bodegas else None,
            codigo_bodega=mov.mov_bodegas.f150_id if mov.mov_bodegas else None,
            concepto=mov.concepto_mov.f145_descripcion if mov.concepto_mov else None,
            
        ))
    
    return result


