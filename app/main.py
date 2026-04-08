from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import categorias, produtos, clientes, pedidos

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce API",
    description="API REST completa para e-commerce com FastAPI + MySQL",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(clientes.router)
app.include_router(pedidos.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "mensagem": "E-commerce API está no ar! 🚀",
        "docs": "/docs",
        "redoc": "/redoc",
    }
