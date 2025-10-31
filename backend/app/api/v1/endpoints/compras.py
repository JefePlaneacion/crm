from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.db.models import TipoDocumento, Estado , Inventario, Bodega,Codigos,TipoProveedor,Proveedor,DocumentoCompra,ItemsCompras
from app.schemas.compras import Items_Compras_Base
from typing import List


router = APIRouter()

@router.get("/", response_model=List[Items_Compras_Base])


def read_compras(db: Session = Depends(get_db)):
    tipos_documentos_compras = ['OCI','OCC','OCSE']
    compras = (
        db.query(ItemsCompras)
        .join(ItemsCompras.documento_compra)
        .filter(DocumentoCompra.f420_id_tipo_docto.in_(tipos_documentos_compras))
        .options(
            joinedload(ItemsCompras.bodegas),
            joinedload(ItemsCompras.items),
            joinedload(ItemsCompras.existencias),
            joinedload(ItemsCompras.documento_compra)
                .joinedload(DocumentoCompra.clase_proveedor)
        )
        .all()
    )

    def single_or_list(rel):
        """Devuelve un solo elemento si hay uno, o lista si hay varios"""
        if not rel:
            return None
        elif len(rel) == 1:
            return rel[0]
        else:
            return rel

    result = []

    for comp in compras:
        # DEBUG: Imprime información del documento y proveedor
        #print(f"=== DEBUG ===")
        #print(f"ID OC: {comp.f421_rowid_oc_docto}")
        #print(f"Documento existe: {comp.documento_compra is not None}")
        
        #if comp.documento_compra:
            #print(f"ID Proveedor en doc: {comp.documento_compra.f420_rowid_tercero_prov}")
            #print(f"Proveedor existe: {comp.documento_compra.clase_proveedor is not None}")
            
            #if comp.documento_compra.clase_proveedor:
                #print(f"Razón social: {comp.documento_compra.clase_proveedor.f200_razon_social}")
        
        # Extraemos datos de relaciones
        bodegas = [b.f150_descripcion for b in comp.bodegas] if comp.bodegas else []
        items = [i.f120_descripcion.strip() for i in comp.items] if comp.items else []
        existencias = [e.f400_cant_existencia_1 for e in comp.existencias] if comp.existencias else []

        proveedor = None
        if comp.documento_compra and comp.documento_compra.clase_proveedor:
            proveedor = comp.documento_compra.clase_proveedor

        razon_social = (
            (proveedor.f200_razon_social or "").strip()
            if (proveedor and proveedor.f200_razon_social) else None
        )
        
        #print(f"Razón social final: {razon_social}")
        #print(f"=============\n")
        
        # Obtener el estado correcto con query manual
        estado_descripcion = None
        if comp.documento_compra:
            estado = db.query(Estado).filter(
                Estado.f054_id_grupo_clase_docto == comp.documento_compra.f420_id_grupo_clase_docto,
                Estado.f054_id == comp.documento_compra.f420_ind_estado
            ).first()
            
            if estado:
                estado_descripcion = estado.f054_descripcion



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
            "estado_doc": estado_descripcion,
            
            "bodegas": single_or_list(bodegas),
            "items": single_or_list(items),
            "existencias": single_or_list(existencias),
            "razon_social": razon_social
        })

    return result