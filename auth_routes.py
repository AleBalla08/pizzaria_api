from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario
from dependencies import pegar_sessao
from main import bcrypt_context
from schemas import UsuarioSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get('/')
async def authenticate():
    """Endpoint for user authentication."""
    return {"message": "Authentication endpoint", "authenticated": False}

@auth_router.post("/create-account")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    if not session:
        return {"message":"Sessão não encontrada."}
    
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status=400, detail="Usuário com esse E-Mail já cadastrado.")
    else:
        try:
            senha_crypto = bcrypt_context.hash(usuario_schema.senha)
            novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_crypto, usuario_schema.ativo, usuario_schema.admin)
            session.add(novo_usuario)
            session.commit()
            return {"message": f"Usuário cadastrado com sucesso - Email {usuario_schema.email}"}
        except Exception as e:
            raise HTTPException(status=400, detail="Erro ao registrar Usuário")