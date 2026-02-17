import asyncio
import json

from enricher.enricher import EnrichmentService
from shared.database.mongo_connection import mongo_manager
from shared.database.redis_connection import redis_manager
from shared.database.kafka_connection import kafka_manager
from shared.models import PizzaOrders, PizzaAnalysis
from shared.config import settings


async def consume():
    await mongo_manager.connect(document_models=[PizzaOrders, PizzaAnalysis])
    await redis_manager.connect()

    consumer = kafka_manager.create_consumer(
        topics=[settings.KAFKA_TOPIC],
        group_id="enricher-team"
    )

    print("🕵️ Enricher Worker Started...")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            try:
                data = json.loads(msg.value().decode('utf-8'))
                await EnrichmentService.process_pizza(data)

            except Exception as e:
                print(f"Error processing message: {e}")

    finally:
        print("Shutting down worker...")
        consumer.close()
        await mongo_manager.close()
        await redis_manager.close()


if __name__ == "__main__":
    asyncio.run(consume())