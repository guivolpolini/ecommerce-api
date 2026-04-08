from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Produto, Categoria
from app.schemas.schemas import ProdutoCreate, ProdutoUpdate, ProdutoOut

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=List[ProdutoOut])
def listar_produtos(
    skip: int = 0,
    limit: int = 100,
    categoria_id: Optional[int] = Query(None),
    nome: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Produto)
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)
    if nome:
        query = query.filter(Produto.nome.ilike(f"%{nome}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/{produto_id}", response_model=ProdutoOut)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.post("/", response_model=ProdutoOut, status_code=status.HTTP_201_CREATED)
def criar_produto(data: ProdutoCreate, db: Session = Depends(get_db)):
    if data.categoria_id:
        categoria = db.query(Categoria).filter(Categoria.id == data.categoria_id).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
    produto = Produto(**data.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.put("/{produto_id}", response_model=ProdutoOut)
def atualizar_produto(produto_id: int, data: ProdutoUpdate, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if data.categoria_id:
        categoria = db.query(Categoria).filter(Categoria.id == data.categoria_id).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
