from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import pegar_sessao, verificar_token
from models import Pedido, Usuario
from schemas import PedidoSchema

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verificar_token)])

@order_router.get('/')
async def get_orders():
    """Endpoint to retrieve a list of orders."""
    return {"message": "List of orders"}

@order_router.post('/order')
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    try:
        novo_pedido = Pedido(usuario=pedido_schema.usuario)
        session.add(novo_pedido)
        session.commit()
        return {"mensagem":f"Pedido criado com sucesso - id: {novo_pedido.id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao gerar pedido: {e}")
    

@order_router.post('/order/cancelar/{id_pedido}')
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):

    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem permissão para realizar essa ação")
        
    pedido.status = 'C'
    session.commit()

    return {"message": f"Pedido N°{id_pedido} cancelado com sucesso"}
