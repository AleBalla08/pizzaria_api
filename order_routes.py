from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import pegar_sessao
from models import Pedido
from schemas import PedidoSchema

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get('/')
async def get_orders():
    """Endpoint to retrieve a list of orders."""
    return {"message": "List of orders"}

@order_router.post('/order')
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    try:
        novo_pedido = Pedido(usuario=pedido_schema.id_usuario)
        session.add(novo_pedido)
        session.commit()
        return {"mensagem":f"Pedido criado com sucesso - id: {novo_pedido.id}"}
    except Exception as e:
        raise HTTPException(status=400, detail=f"Erro ao gerar pedido: {e}")
