from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from app.models.models import OrderStatus


# ── Categoria ──────────────────────────────────────────────
class CategoriaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None

class CategoriaOut(CategoriaBase):
    id: int
    criado_em: datetime
    model_config = {"from_attributes": True}


# ── Produto ────────────────────────────────────────────────
class ProdutoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    estoque: int = 0
    categoria_id: Optional[int] = None

    @field_validator("preco")
    @classmethod
    def preco_positivo(cls, v):
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return v

    @field_validator("estoque")
    @classmethod
    def estoque_nao_negativo(cls, v):
        if v < 0:
            raise ValueError("Estoque não pode ser negativo")
        return v

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[float] = None
    estoque: Optional[int] = None
    categoria_id: Optional[int] = None

class ProdutoOut(ProdutoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
    categoria: Optional[CategoriaOut] = None
    model_config = {"from_attributes": True}


# ── Cliente ────────────────────────────────────────────────
class ClienteBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    endereco: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None

class ClienteOut(ClienteBase):
    id: int
    criado_em: datetime
    model_config = {"from_attributes": True}


# ── Pedido ─────────────────────────────────────────────────
class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int

    @field_validator("quantidade")
    @classmethod
    def quantidade_positiva(cls, v):
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        return v

class ItemPedidoOut(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    preco_unitario: float
    produto: Optional[ProdutoOut] = None
    model_config = {"from_attributes": True}

class PedidoCreate(BaseModel):
    cliente_id: int
    observacao: Optional[str] = None
    itens: List[ItemPedidoCreate]

class PedidoStatusUpdate(BaseModel):
    status: OrderStatus

class PedidoOut(BaseModel):
    id: int
    cliente_id: int
    status: OrderStatus
    total: float
    observacao: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
    cliente: Optional[ClienteOut] = None
    itens: List[ItemPedidoOut] = []
    model_config = {"from_attributes": True}
