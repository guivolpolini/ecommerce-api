from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.auth.auth import hash_senha, verificar_senha, criar_token
from app.auth.usuario_schema import UsuarioCreate, UsuarioOut, LoginRequest, TokenOut
from app.auth.dependencies import get_usuario_atual

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/cadastro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def cadastrar(data: UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Usuario).filter(Usuario.email == data.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    usuario = Usuario(
        nome=data.nome,
        email=data.email,
        senha_hash=hash_senha(data.senha),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenOut)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()

    if not usuario or not verificar_senha(data.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )

    if not usuario.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")

    token = criar_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}


@router.get("/me", response_model=UsuarioOut)
def meu_perfil(usuario_atual: Usuario = Depends(get_usuario_atual)):
    return usuario_atual
