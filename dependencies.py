from fastapi import Depends, HTTPException
from jose import jwt, JWTError

from main import ALGORITHM, SECRET_KEY, oauth2_schema
from models import Usuario, db
from sqlalchemy.orm import Session, sessionmaker


def pegar_sessao():
    Session = sessionmaker(bind = db)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = dic_info.get("sub")

    except JWTError as erro:
        print(f"Erro: {erro}")
        raise HTTPException(status_code=401, detail="Você não tem acesso a essa rota")

    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario não encontrado ou token inválido/expirado")

    return usuario