import mercadopago
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.models import Pedido, OrderStatus
from app.database import settings

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


def get_mp_sdk():
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
    return sdk


class PagamentoCreate(BaseModel):
    pedido_id: int
    email_pagador: str
    nome_pagador: str
    sobrenome_pagador: Optional[str] = ""


@router.post("/criar")
def criar_pagamento(data: PagamentoCreate, db: Session = Depends(get_db)):
    # Busca o pedido
    pedido = db.query(Pedido).filter(Pedido.id == data.pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if pedido.status != OrderStatus.pendente:
        raise HTTPException(
            status_code=400,
            detail=f"Pedido não está pendente (status atual: {pedido.status})",
        )

    sdk = get_mp_sdk()

    # Monta os itens do pedido
    itens = []
    for item in pedido.itens:
        itens.append({
            "id": str(item.produto_id),
            "title": item.produto.nome,
            "quantity": item.quantidade,
            "unit_price": float(item.preco_unitario),
            "currency_id": "BRL",
        })

    # Cria a preferência de pagamento
    preference_data = {
        "items": itens,
        "payer": {
            "email": data.email_pagador,
            "name": data.nome_pagador,
            "surname": data.sobrenome_pagador,
        },
        "external_reference": str(pedido.id),
        "statement_descriptor": "Ecommerce API",
    }

    result = sdk.preference().create(preference_data)

    if result["status"] != 201:
        raise HTTPException(status_code=400, detail=f"Erro MP: {result}")

    preference = result["response"]

    return {
        "pedido_id": pedido.id,
        "total": pedido.total,
        "link_pagamento": preference["init_point"],
        "link_teste": preference["sandbox_init_point"],
        "preference_id": preference["id"],
    }


@router.get("/sucesso")
def pagamento_sucesso(
    payment_id: Optional[str] = None,
    status: Optional[str] = None,
    external_reference: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if external_reference:
        pedido = db.query(Pedido).filter(Pedido.id == int(external_reference)).first()
        if pedido and status == "approved":
            pedido.status = OrderStatus.pago
            db.commit()

    return {
        "mensagem": "Pagamento aprovado! ✅",
        "payment_id": payment_id,
        "status": status,
        "pedido_id": external_reference,
    }


@router.get("/falha")
def pagamento_falha(external_reference: Optional[str] = None):
    return {
        "mensagem": "Pagamento recusado ❌",
        "pedido_id": external_reference,
    }


@router.get("/pendente")
def pagamento_pendente(external_reference: Optional[str] = None):
    return {
        "mensagem": "Pagamento pendente ⏳",
        "pedido_id": external_reference,
    }
