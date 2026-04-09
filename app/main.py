from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import categorias, produtos, clientes, pedidos
from app.auth.router import router as auth_router
from app.routers.upload import router as upload_router
from app.routers.pagamentos import router as pagamentos_router

# Importa todos os models para criar as tabelas
import app.models.models  # noqa
import app.models.usuario  # noqa

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce API",
    description="API REST completa para e-commerce com FastAPI + MySQL + JWT Auth + Upload + MercadoPago",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve as imagens como arquivos estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router)
app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(clientes.router)
app.include_router(pedidos.router)
app.include_router(upload_router)
app.include_router(pagamentos_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "mensagem": "E-commerce API está no ar! 🚀",
        "docs": "/docs",
        "redoc": "/redoc",
    }
