from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import pegar_sessao, verificar_token
from models import ItensPedido, Pedido, Usuario
from schemas import ItemPedidoSchema, PedidoSchema

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
    
    if pedido.status == 'C':
        raise HTTPException(status_code=401, detail="O pedido já esta cancelado")
    
    pedido.status = 'C'
    session.commit()

    return {"message": f"Pedido N°{pedido.id} cancelado com sucesso", "pedido": pedido}

@order_router.get('/order/listar')
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem permissão para realizar essa ação")
    
    pedidos = session.query(Pedido).all()
    return {"pedidos": pedidos}

@order_router.post("/order/adicionar_item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int,item_schema: ItemPedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==item_schema.pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")

    if usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem permissão para realizar essa ação")

    item_pedido = ItensPedido(item_schema.quantidade, item_schema.sabor, item_schema.tamanho, item_schema.preco_unitario, id_pedido)
    
    session.add(item_pedido)
    pedido.calcula_preco()
    session.commit()

    return {"message": f"Item adicionado ao pedido N°{pedido.id} com sucesso", "item": item_pedido.id, "pedido": pedido.id}
