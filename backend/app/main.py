from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import inventarios, compras, mov_inventarios

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(inventarios.router, prefix="/api/v1", tags=["Inventarios"])
app.include_router(compras.router, prefix="/api/v1/compras")
app.include_router(mov_inventarios.router, prefix="/api/v1/mov_inventarios")