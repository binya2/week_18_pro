import asyncio
import json
import re
from shared.database.mongo_connection import mongo_manager
from shared.database.kafka_connection import kafka_manager
from shared.models import PizzaOrders
from shared.config import settings

KEYWORDS = ["allergy", "peanut", "gluten"]


def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'[^\w\s]', '', text)
    return cleaned.upper()


async def process_text(msg):
    try:
        data = json.loads(msg.value().decode('utf-8'))
        order_id = data.get('order_id')
        instructions = data.get('special_instructions', "").lower()

        print(f"🕵️ Text Worker: Analyzing order {order_id}...")

        order = await PizzaOrders.find_one(PizzaOrders.order_id == order_id)
        if not order:
            print(f"Order {order_id} not found in DB.")
            return
        is_flagged = any(word in instructions for word in KEYWORDS)
        cleaned = clean_text(data.get('special_instructions', ""))
        order.allergies_flagged = is_flagged
        order.cleaned_protocol = cleaned
        await order.save()

        print(f"✅ Text Worker: Updated {order_id} (Flagged: {is_flagged})")

    except Exception as e:
        print(f"Error processing text: {e}")


async def consume():
    await mongo_manager.connect(document_models=[PizzaOrders])
    consumer = kafka_manager.create_consumer(
        topics=[settings.KAFKA_TOPIC],
        group_id="text-team"
    )
    try:
        while True:
            msg = await asyncio.to_thread(consumer.poll, 1.0)
            if msg is None:
                continue
            if msg.error():
                continue
            await process_text(msg)
    finally:
        consumer.close()
        await mongo_manager.close()


if __name__ == "__main__":
    asyncio.run(consume())