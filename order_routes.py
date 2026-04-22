from fastapi import APIRouter

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get('/')
async def get_orders():
    """Endpoint to retrieve a list of orders."""
    return {"message": "List of orders"}