from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Pedido, Cliente, Produto, ItemPedido, OrderStatus
from app.schemas.schemas import PedidoCreate, PedidoStatusUpdate, PedidoOut

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("/", response_model=List[PedidoOut])
def listar_pedidos(
    skip: int = 0,
    limit: int = 100,
    cliente_id: Optional[int] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Pedido)
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    if status:
        query = query.filter(Pedido.status == status)
    return query.order_by(Pedido.criado_em.desc()).offset(skip).limit(limit).all()


@router.get("/{pedido_id}", response_model=PedidoOut)
def buscar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def criar_pedido(data: PedidoCreate, db: Session = Depends(get_db)):
    # Valida cliente
    cliente = db.query(Cliente).filter(Cliente.id == data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    if not data.itens:
        raise HTTPException(status_code=400, detail="O pedido deve ter ao menos um item")

    pedido = Pedido(
        cliente_id=data.cliente_id,
        observacao=data.observacao,
        total=0.0,
    )
    db.add(pedido)
    db.flush()  # gera o id sem commit

    total = 0.0
    for item_data in data.itens:
        produto = db.query(Produto).filter(Produto.id == item_data.produto_id).first()
        if not produto:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Produto {item_data.produto_id} não encontrado")
        if produto.estoque < item_data.quantidade:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente para '{produto.nome}' (disponível: {produto.estoque})",
            )

        subtotal = produto.preco * item_data.quantidade
        total += subtotal

        item = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=item_data.quantidade,
            preco_unitario=produto.preco,
        )
        produto.estoque -= item_data.quantidade
        db.add(item)

    pedido.total = round(total, 2)
    db.commit()
    db.refresh(pedido)
    return pedido


@router.patch("/{pedido_id}/status", response_model=PedidoOut)
def atualizar_status(pedido_id: int, data: PedidoStatusUpdate, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Regra: pedido cancelado não pode mudar de status
    if pedido.status == OrderStatus.cancelado:
        raise HTTPException(status_code=400, detail="Pedido cancelado não pode ser alterado")

    # Se cancelar, devolve estoque
    if data.status == OrderStatus.cancelado:
        for item in pedido.itens:
            item.produto.estoque += item.quantidade

    pedido.status = data.status
    db.commit()
    db.refresh(pedido)
    return pedido


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    # Devolve estoque ao deletar
    for item in pedido.itens:
        item.produto.estoque += item.quantidade
    db.delete(pedido)
    db.commit()
