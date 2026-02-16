from enum import Enum

from beanie import Document
from pydantic import Field


class Status(str, Enum):
    PREPARING = "preparing"
    DELIVERED = "delivered"

class PizzaRequest(Document):
    order_id: str
    pizza_type: str
    size: str = Field(default="medium")
    quantity: int = Field(default=1)
    is_delivery: bool
    special_instructions: str = Field(default="")


class PizzaOrders(Document):
    order_id: str
    pizza_type: str
    size: str = Field(default="medium")
    quantity: int = Field(default=1)
    is_delivery: bool
    special_instructions: str = Field(default="")
    status: Status = Field(default="preparing")

