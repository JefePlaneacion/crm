from sqlalchemy.orm import Session
from app.db.models import Inventario, Bodega, Codigos
import pandas as pd
from sqlalchemy import func
from fastapi.encoders import jsonable_encoder


def get_inventarios(db: Session):

    result =db.query(
        Inventario,
        Bodega.f150_descripcion.label("Bodega"),
        Codigos.f120_descripcion.label("Descripción_Item"),
        Codigos.f120_referencia.label("Referencia_Item")
    ).join(Codigos, Inventario.f400_rowid_item_ext == Codigos.f120_id,isouter=True
    ).join(Bodega, Inventario.f400_rowid_bodega == Bodega.f150_rowid,isouter=True
    ).all()

    result_dicts = [
        {
            
            "f400_rowid_item_ext": Inventario.f400_rowid_item_ext,
            "f400_rowid_bodega": Inventario.f400_rowid_bodega,
            "f400_abc_rotacion_costo": Inventario.f400_abc_rotacion_costo,
            "f400_abc_rotacion_veces": Inventario.f400_abc_rotacion_veces,
            "f400_costo_prom_uni": Inventario.f400_costo_prom_uni,
            "f400_costo_prom_tot": Inventario.f400_costo_prom_tot,
            "f400_fecha_ult_compra": Inventario.f400_fecha_ult_compra,
            "f400_fecha_ult_entrada": Inventario.f400_fecha_ult_entrada,
            "f400_fecha_ult_salida": Inventario.f400_fecha_ult_salida,
            "f400_cant_existencia_1": Inventario.f400_cant_existencia_1,
            "f400_cant_comprometida_1": Inventario.f400_cant_comprometida_1,
            "f400_cant_pendiente_salir_1": Inventario.f400_cant_pendiente_salir_1,
            "f400_cant_pendiente_entrar_1": Inventario.f400_cant_pendiente_entrar_1,
            "Bodega": Bodega.f150_descripcion,
            "Descripción_Item": Codigos.f120_descripcion,
            "Referencia_Item": Codigos.f120_referencia
        }
        for inventario, bodega, descripcion_item, referencia_item in result
    ]
    df = pd.DataFrame(result_dicts)

    # Eliminar columna interna de SQLAlchemy que no necesitamos
    df.drop(columns=['_sa_instance_state'], inplace=True, errors='ignore')

    # Renombrar columnas para hacerlas más legibles
    df = df.rename(columns={
        'f400_rowid_item_ext': 'ID Item',
        'f400_rowid_bodega': 'ID Bodega',
        'f400_abc_rotacion_costo': 'ABC Rotación Costo',
        'f400_abc_rotacion_veces': 'ABC Rotación Veces',
        'f400_costo_prom_uni': 'Costo Promedio Unitario',
        'f400_costo_prom_tot': 'Costo Promedio Total',
        'f400_fecha_ult_compra': 'Fecha Última Compra',
        'f400_fecha_ult_entrada': 'Fecha Última Entrada',
        'f400_fecha_ult_salida': 'Fecha Última Salida',
        'f400_cant_existencia_1': 'Cantidad Existencia 1',
        'f400_cant_comprometida_1': 'Cantidad Comprometida 1',
        'f400_cant_pendiente_salir_1': 'Cantidad Pendiente Salir 1',
        'f400_cant_pendiente_entrar_1': 'Cantidad Pendiente Entrar 1'
    })

    jsonable_result = jsonable_encoder(df.to_dict(orient="records"))
    return jsonable_result




    


def calcular_valor_inventario(db: Session):
    return db.query(Inventario).with_entities(func.sum(Inventario.f400_costo_prom_tot)).scalar() or 0.0

