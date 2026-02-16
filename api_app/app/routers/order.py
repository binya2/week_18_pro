from fastapi import APIRouter

router = APIRouter(prefix="/order", tags=["order_router"])

@router.get("/order/{order_id}")
async def read_order(order_id: int):
    return {
        "order_id": order_id,
        "description": "Pizza with cheese"
    }