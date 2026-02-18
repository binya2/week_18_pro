import asyncio
import json
import re

from shared.database.mongo_connection import mongo_manager
from shared.database.kafka_connection import kafka_manager
from shared.models import PizzaOrders, PizzaRecipe, PizzaAnalysisResult
from shared.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'[^\w\s]', '', text)
    return cleaned.lower()


async def process_text(msg):
    try:
        if not msg.value():
            return None
        data = json.loads(msg.value().decode('utf-8'))

        pizza_type = data.get('pizza_type', "")
        order_id = data.get('order_id')

        special_instructions_instructions = data.get('special_instructions', "").lower()
        special_instructions_cleaned = clean_text(special_instructions_instructions)

        pizza_recipe_doc = await PizzaRecipe.find_one({"pizza_type":pizza_type})
        pizza_recipes_cleaned = ""
        if pizza_recipe_doc:
            pizza_recipes_cleaned = clean_text(pizza_recipe_doc.instructions)
            logger.info(f"Recipe found for: {pizza_type}")
        else:
            logger.warning(f"No recipe found for: {pizza_type}")

        return PizzaAnalysisResult(
            order_id=order_id,
            pizza_type=pizza_type,
            special_instructions=special_instructions_cleaned,
            recipes=pizza_recipes_cleaned
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        return None

async def worker():
    await mongo_manager.connect(document_models=[PizzaOrders, PizzaRecipe])
    kafka_manager.start()
    consumer = kafka_manager.get_consumer(
        topics=[settings.KAFKA_CONSUMER_TOPIC],
        group_id="preprocessor-team"
    )
    producer = kafka_manager.get_producer()
    logger.info("Preprocessor Worker Started")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                continue
            processed_result = await process_text(msg)
            if processed_result:
                producer.produce(
                    topic=settings.KAFKA_PRODUCER_TOPIC,
                    key=processed_result.order_id,
                    value=processed_result.model_dump_json().encode('utf-8')
                )
            producer.poll(0)
    finally:
        producer.flush()
        consumer.close()
        await mongo_manager.close()


if __name__ == "__main__":
    asyncio.run(worker())
