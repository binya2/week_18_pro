from shared.models import PizzaOrders
from shared.utils.caching import cache


class OrderService:

    @staticmethod
    @cache(expire=60)
    async def get_order(order_id: str):
        return await PizzaOrders.find_one(PizzaOrders.order_id == order_id)