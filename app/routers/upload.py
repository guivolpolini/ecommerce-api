import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from PIL import Image
import aiofiles

from app.database import get_db
from app.models.models import Produto

UPLOAD_DIR = "uploads/produtos"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 5

os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/produtos", tags=["Upload de Imagens"])


@router.post("/{produto_id}/imagem")
async def upload_imagem(
    produto_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Verifica se produto existe
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verifica tipo do arquivo
    if arquivo.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Use JPG, PNG ou WebP",
        )

    # Lê o conteúdo e verifica tamanho
    conteudo = await arquivo.read()
    tamanho_mb = len(conteudo) / (1024 * 1024)
    if tamanho_mb > MAX_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo muito grande. Máximo {MAX_SIZE_MB}MB",
        )

    # Gera nome único para o arquivo
    extensao = arquivo.filename.split(".")[-1].lower()
    nome_arquivo = f"{uuid.uuid4()}.{extensao}"
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)

    # Salva o arquivo
    async with aiofiles.open(caminho, "wb") as f:
        await f.write(conteudo)

    # Redimensiona a imagem para no máximo 800x800
    try:
        img = Image.open(caminho)
        img.thumbnail((800, 800))
        img.save(caminho)
    except Exception:
        os.remove(caminho)
        raise HTTPException(status_code=400, detail="Arquivo de imagem inválido")

    # Remove imagem antiga se existir
    if produto.imagem:
        caminho_antigo = os.path.join(UPLOAD_DIR, produto.imagem)
        if os.path.exists(caminho_antigo):
            os.remove(caminho_antigo)

    # Salva o nome da imagem no banco
    produto.imagem = nome_arquivo
    db.commit()

    return {
        "mensagem": "Imagem enviada com sucesso!",
        "imagem": nome_arquivo,
        "url": f"/uploads/produtos/{nome_arquivo}",
    }


@router.delete("/{produto_id}/imagem")
def deletar_imagem(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if not produto.imagem:
        raise HTTPException(status_code=404, detail="Produto não tem imagem")

    caminho = os.path.join(UPLOAD_DIR, produto.imagem)
    if os.path.exists(caminho):
        os.remove(caminho)

    produto.imagem = None
    db.commit()

    return {"mensagem": "Imagem removida com sucesso!"}
