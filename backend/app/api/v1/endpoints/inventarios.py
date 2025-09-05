from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import inventario_service 


router = APIRouter()

@router.get("/", summary="Obtener inventarios", description="Obtiene una lista de inventarios con paginación.")

def read_inventarios(db: Session = Depends(get_db)):
    inventarios = inventario_service.get_inventarios(db)
    return inventarios
