from fastapi import APIRouter, HTTPException
from api_app.app.service.orders_service import OrderService
router = APIRouter(prefix="/order", tags=["order_router"])


@router.get("/{order_id}")
async def read_order(order_id: str):
    result = await OrderService.get_order(order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order": result
    }