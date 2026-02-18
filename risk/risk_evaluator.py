import asyncio
import json
import re
from datetime import datetime

from shared.database.mongo_connection import mongo_manager
from shared.database.kafka_connection import kafka_manager
from shared.models import PizzaOrders, PizzaRecipe, PizzaAnalysisResult, Status
from shared.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_allergies(special_instructions, common_allergens):
    if not special_instructions:
        return False
    for allergen in common_allergens:
        if allergen in special_instructions:
            return True
    return False


async def risk_evaluator(msg):
    try:
        if not msg.value():
            return None
        data = json.loads(msg.value().decode('utf-8'))

        order_id = data.get('order_id')
        order = await PizzaOrders.find_one(PizzaOrders.order_id == order_id)
        special_instructions = data.get('special_instructions', "").lower()
        common_allergens = data.get("common_allergens")

        is_allergic = await check_allergies(special_instructions, common_allergens)

        if is_allergic:
            order.status = Status.CANCELLED

        order.allergies_flagged = bool(common_allergens)
        order.update_date = datetime.now()

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
    logger.info("rrisk Evaluator Worker Started")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                continue

        await risk_evaluator(msg)
    finally:
        consumer.close()
        await mongo_manager.close()


if __name__ == "__main__":
    asyncio.run(worker())
