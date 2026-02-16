from shared.models import PizzaOrders
from shared.utils.caching import cache  # הייבוא של הדקורטור


class OrderService:

    @staticmethod
    @cache(expire=60, prefix="order:")  # <-- הקסם קורה כאן
    async def get_order_by_id(order_id: str):
        return await PizzaOrders.find_one(PizzaOrders.order_id == order_id)