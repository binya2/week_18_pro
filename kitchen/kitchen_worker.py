import asyncio
import json
from shared.database.mongo_connection import mongo_manager
from shared.database.redis_connection import redis_manager
from shared.database.kafka_connection import kafka_manager
from shared.models import PizzaOrders, Status
from shared.config import settings
from shared.utils.caching import generate_cache_key


async def process_order(msg):
    try:
        data = json.loads(msg.value().decode('utf-8'))
        order_id = data.get('order_id')
        await asyncio.sleep(15)
        order = await PizzaOrders.find_one(PizzaOrders.order_id == order_id)
        if order:
            order.status = Status.DELIVERED
            await order.save()

            redis = redis_manager.get_client()
            cache_key = generate_cache_key("get_order", order_id)
            await redis.delete(cache_key)

    except Exception as e:
        print(f"Error processing message: {e}")


async def consume():
    await mongo_manager.connect(document_models=[PizzaOrders])
    await redis_manager.connect()
    consumer = kafka_manager.get_consumer(
        topics=[settings.KAFKA_TOPIC],
        group_id="kitchen-team"
    )
    try:
        while True:
            msg = await asyncio.to_thread(consumer.poll, 1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            await process_order(msg)
    finally:
        consumer.close()
        await mongo_manager.close()
        await redis_manager.close()


if __name__ == "__main__":
    asyncio.run(consume())
