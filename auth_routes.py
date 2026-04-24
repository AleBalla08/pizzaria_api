from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario
from dependencies import pegar_sessao
from main import bcrypt_context,SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRING_MINUTES
from schemas import LoginSchema, UsuarioSchema
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario):
    data_expiracao = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRING_MINUTES))
    dic_info = {
        "sub":id_usuario,
        "exp": data_expiracao
    }
    encoded_jwt = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return encoded_jwt

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False

    return usuario

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
        raise HTTPException(status_code=400, detail="Usuário com esse E-Mail já cadastrado.")
    else:
        try:
            senha_crypto = bcrypt_context.hash(usuario_schema.senha)
            novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_crypto, usuario_schema.ativo, usuario_schema.admin)
            session.add(novo_usuario)
            session.commit()
            return {"message": f"Usuário cadastrado com sucesso - Email {usuario_schema.email}"}
        except Exception as e:
            raise HTTPException(status_code=400, detail="Erro ao registrar Usuário")
        
@auth_router.post('/login')
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario nao encontrado ou credenciais erradas")
    else:
        access_token = criar_token(usuario.id)
        return {
            'access_token': access_token,
            'token_type': 'Bearer'
        }