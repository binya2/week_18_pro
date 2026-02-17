from typing import List, Any

from bson import json_util, errors
from fastapi import UploadFile, HTTPException
from pydantic import TypeAdapter

from shared.models import PizzaOrders, PizzaRecipe, PizzaAnalysis
from shared.database.kafka_connection import kafka_manager
from shared.config import settings

TRANSFORM_KEY_VALUE = "key_value_to_list"
TRANSFORM_NONE = "none"
TRANSFORM_SINGLE = "single_doc"

SCHEMA_REGISTRY = {
    "prep": {
        "model": PizzaRecipe,
        "transform": TRANSFORM_KEY_VALUE,
        "mapping": {"key": "pizza_type", "value": "instructions"}
    },
    "orders": {
        "model": PizzaOrders,
        "transform": TRANSFORM_NONE
    },
    "analysis": {
        "model": PizzaAnalysis,
        "transform": TRANSFORM_SINGLE
    }
}


class UploadService:
    @staticmethod
    def _detect_config(filename: str) -> dict:
        clean_name = filename.lower()
        for keyword, config in SCHEMA_REGISTRY.items():
            if keyword in clean_name:
                return config

        raise HTTPException(
            status_code=400,
            detail=f"Unknown file type: '{filename}'"
        )

    @staticmethod
    def _transform_data(data: Any, config: dict) -> List[dict]:
        transform_type = config.get("transform", TRANSFORM_NONE)
        if transform_type == TRANSFORM_KEY_VALUE:
            if not isinstance(data, dict):
                raise ValueError("Expected JSON object (dict) for Key-Value mapping")
            mapping = config.get("mapping", {})
            key_field = mapping.get("key", "id")
            value_field = mapping.get("value", "content")
            return [{key_field: k, value_field: v} for k, v in data.items()]
        elif transform_type == TRANSFORM_SINGLE:
            if isinstance(data, dict):
                return [data]
        return data

    @staticmethod
    async def process_and_save(file: UploadFile):
        config = UploadService._detect_config(file.filename)
        model_class = config["model"]

        if file.content_type != "application/json":
            raise HTTPException(status_code=400, detail="Invalid file type")

        content = await file.read()
        try:
            raw_data = json_util.loads(content)
            normalized_data = UploadService._transform_data(raw_data, config)
            adapter = TypeAdapter(List[model_class])
            parsed_objects = adapter.validate_python(normalized_data)

            if parsed_objects:
                await model_class.insert_many(parsed_objects)
            if model_class == PizzaOrders:
                await UploadService.push_to_kafka(parsed_objects)
            return {
                "status": "success",
                "model": model_class.__name__,
                "items_saved": len(parsed_objects)
            }
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Validation Error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    @staticmethod
    async def push_to_kafka(orders_list: List[PizzaOrders]):
        if not orders_list:
            return
        producer = kafka_manager.get_producer()
        for order in orders_list:
            order_json = order.model_dump_json()
            producer.produce(
                topic=settings.KAFKA_PRODUCER_TOPIC,
                key=str(order.order_id),
                value=order_json.encode('utf-8')
            )
        producer.poll(0)
