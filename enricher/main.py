import asyncio
import json
import logging

from enricher import EnrichmentService
from shared.database.mongo_connection import mongo_manager
from shared.database.redis_connection import redis_manager
from shared.database.kafka_connection import kafka_manager
from shared.models import PizzaOrders, PizzaAnalysis
from shared.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def worker():
    await mongo_manager.connect(document_models=[PizzaOrders, PizzaAnalysis])
    await redis_manager.connect()
    kafka_manager.start()

    consumer = kafka_manager.get_consumer(
        topics=[settings.KAFKA_CONSUMER_TOPIC],
        group_id="enricher-team"
    )
    producer = kafka_manager.get_producer()

    logger.info("🕵️ Enricher Worker Started...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue
            try:
                data = json.loads(msg.value().decode('utf-8'))
                result = await EnrichmentService.process_pizza(data)
                if result:
                    producer.produce(
                        topic=settings.KAFKA_PRODUCER_TOPIC,
                        key=result['order_id'],
                        value=json.dumps(result).encode('utf-8')
                    )
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    finally:
        logger.info("Shutting down worker...")
        consumer.close()
        producer.flush()
        await mongo_manager.close()
        await redis_manager.close()


if __name__ == "__main__":
    asyncio.run(worker())
