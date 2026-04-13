import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.models import Cliente

router = APIRouter(prefix="/enderecos", tags=["Endereços e Frete"])


class EnderecoCreate(BaseModel):
    cliente_id: int
    cep: str
    numero: str
    complemento: Optional[str] = None


class FreteRequest(BaseModel):
    cep_destino: str


# CEP de origem da loja (pode mudar no .env futuramente)
CEP_ORIGEM = "01310100"  # Av. Paulista, SP


@router.get("/cep/{cep}")
async def buscar_cep(cep: str):
    cep = cep.replace("-", "").strip()

    if len(cep) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido — deve ter 8 dígitos")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
        except Exception:
            raise HTTPException(status_code=503, detail="Serviço de CEP indisponível")

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="CEP não encontrado")

    data = response.json()

    if "erro" in data:
        raise HTTPException(status_code=404, detail="CEP não encontrado")

    return {
        "cep": data.get("cep"),
        "logradouro": data.get("logradouro"),
        "bairro": data.get("bairro"),
        "cidade": data.get("localidade"),
        "estado": data.get("uf"),
    }


@router.post("/salvar")
async def salvar_endereco(data: EnderecoCreate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cep = data.cep.replace("-", "").strip()

    # Busca o endereço pelo CEP
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
        except Exception:
            raise HTTPException(status_code=503, detail="Serviço de CEP indisponível")

    if response.status_code != 200 or "erro" in response.json():
        raise HTTPException(status_code=404, detail="CEP não encontrado")

    endereco_data = response.json()

    endereco_completo = (
        f"{endereco_data.get('logradouro')}, {data.numero}"
        f"{', ' + data.complemento if data.complemento else ''}"
        f" - {endereco_data.get('bairro')}"
        f" - {endereco_data.get('localidade')}/{endereco_data.get('uf')}"
        f" - CEP: {endereco_data.get('cep')}"
    )

    cliente.endereco = endereco_completo
    db.commit()

    return {
        "mensagem": "Endereço salvo com sucesso!",
        "cliente_id": cliente.id,
        "endereco": endereco_completo,
    }


@router.post("/calcular-frete")
async def calcular_frete(data: FreteRequest):
    cep = data.cep_destino.replace("-", "").strip()

    if len(cep) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido")

    # Busca o CEP de destino
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
        except Exception:
            raise HTTPException(status_code=503, detail="Serviço de CEP indisponível")

    if response.status_code != 200 or "erro" in response.json():
        raise HTTPException(status_code=404, detail="CEP de destino não encontrado")

    destino = response.json()
    estado_destino = destino.get("uf")

    # Tabela de frete simulada por região
    frete_por_estado = {
        "SP": {"pac": 15.90, "sedex": 25.90, "prazo_pac": 3, "prazo_sedex": 1},
        "RJ": {"pac": 18.90, "sedex": 29.90, "prazo_pac": 4, "prazo_sedex": 2},
        "MG": {"pac": 18.90, "sedex": 29.90, "prazo_pac": 4, "prazo_sedex": 2},
        "ES": {"pac": 20.90, "sedex": 32.90, "prazo_pac": 5, "prazo_sedex": 2},
        "PR": {"pac": 20.90, "sedex": 32.90, "prazo_pac": 5, "prazo_sedex": 2},
        "SC": {"pac": 22.90, "sedex": 35.90, "prazo_pac": 5, "prazo_sedex": 3},
        "RS": {"pac": 22.90, "sedex": 35.90, "prazo_pac": 6, "prazo_sedex": 3},
    }

    frete = frete_por_estado.get(estado_destino, {
        "pac": 28.90, "sedex": 45.90, "prazo_pac": 8, "prazo_sedex": 4
    })

    return {
        "cep_destino": destino.get("cep"),
        "cidade": destino.get("localidade"),
        "estado": estado_destino,
        "opcoes_frete": [
            {
                "tipo": "PAC",
                "preco": frete["pac"],
                "prazo_dias": frete["prazo_pac"],
            },
            {
                "tipo": "SEDEX",
                "preco": frete["sedex"],
                "prazo_dias": frete["prazo_sedex"],
            },
        ],
    }
