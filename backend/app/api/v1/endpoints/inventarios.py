from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session,joinedload
from app.db.session import get_db
from app.services.inventario_service import Inventario 
from app.schemas.inventario import InventarioBase
from typing import List
import json



router = APIRouter()

@router.get("/", response_model=List[InventarioBase])

def read_inventarios(db: Session = Depends(get_db)):

    inventarios =(
        db.query(Inventario)
        .options(
            joinedload(Inventario.bodegas),
            joinedload(Inventario.items)
        )
        .all()
    )
    

    result = []
    for inv in inventarios:
        result.append({
            "id_item": inv.f400_rowid_item_ext,
            "id_bodega": inv.f400_rowid_bodega,
            "abc_costo": inv.f400_abc_rotacion_costo,
            "abc_veces": inv.f400_abc_rotacion_veces,
            "costo_unitario": inv.f400_costo_prom_uni,
            "costo_total": inv.f400_costo_prom_tot,
            "fecha_compra": inv.f400_fecha_ult_compra,
            "fecha_entrada": inv.f400_fecha_ult_entrada,
            "fecha_salida": inv.f400_fecha_ult_salida,
            "existencia": inv.f400_cant_existencia_1,
            "comprometida": inv.f400_cant_comprometida_1,
            "pendiente_salir": inv.f400_cant_pendiente_salir_1,
            "pendiente_entrar": inv.f400_cant_pendiente_entrar_1,
            "bodega": inv.bodegas.f150_descripcion if inv.bodegas else None,
            "codigo_item": inv.items.f120_referencia.strip() if inv.items else None,
            "item": inv.items.f120_descripcion if inv.items else None,
            "codigo_bodega": inv.bodegas.f150_id if inv.bodegas else None
        })

    return result
