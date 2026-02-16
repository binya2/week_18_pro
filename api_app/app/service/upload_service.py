from typing import List

from bson import json_util, errors
from fastapi import UploadFile, HTTPException
from pydantic import TypeAdapter

from shared.models import PizzaOrders
from shared.database.kafka_connection import kafka_manager  # ייבוא המנהל
from shared.config import settings


class UploadService:
    @staticmethod
    async def process_json_upload_file(file: UploadFile) -> List[PizzaOrders]:
        if file.content_type != "application/json":
            raise HTTPException(status_code=400, detail="Invalid file type")

        content = await file.read()
        try:
            data = json_util.loads(content)
            orders_adapter = TypeAdapter(List[PizzaOrders])
            orders_list = orders_adapter.validate_python(data)
            return orders_list

        except errors.BSONError:
            raise HTTPException(status_code=400, detail="Invalid BSON format")
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Validation Error: {str(e)}")

    @staticmethod
    async def save_json_to_mongo(orders_list: List[PizzaOrders]):
        if orders_list:
            await PizzaOrders.insert_many(orders_list)

    @staticmethod
    async def push_orders_to_kafka(orders_list: List[PizzaOrders]):

        if not orders_list:
            return

        producer = kafka_manager.get_producer()

        for order in orders_list:
            order_json = order.model_dump_json()

            producer.produce(
                topic=settings.KAFKA_TOPIC,
                key=str(order.order_id),
                value=order_json.encode('utf-8')
            )
        producer.poll(0)
