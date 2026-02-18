from enum import Enum
from typing import Optional, List
from datetime import datetime
from beanie import Document
from pydantic import Field, BaseModel, field_serializer


class Status(str, Enum):
    PREPARING = "preparing"
    DELIVERED = "delivered"
    BURNT = "burnt"
    CANCELLED = "cancelled"


class PizzaOrders(Document):
    order_id: str
    pizza_type: str
    size: str = Field(default="medium")
    quantity: int = Field(default=1)
    is_delivery: bool
    special_instructions: str = Field(default="")

    status: Status = Field(default=Status.PREPARING)

    allergies_flagged: bool = Field(default=False)
    is_meat: bool = Field(default=False)
    is_dairy: bool = Field(default=True)
    is_kosher: bool = Field(default=False)
    updated_by: str = Field(default="mongo_db")

    insert_date: datetime = Field(default=datetime(2020, 1, 1, 12, 0, 0))
    update_date: datetime = Field(default=datetime(2020, 1, 1, 12, 0, 0))

    @field_serializer('insert_date', 'update_date')
    def serialize_dt(self, dt: datetime, _info):
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    class Settings:
        name = "pizza_orders"


class PizzaAnalysis(Document):
    common_allergens: List[str]
    forbidden_non_kosher: List[str]
    meat_ingredients: List[str]
    dairy_ingredients: List[str]

    class Settings:
        name = "pizza_analysis"


class PizzaRecipe(Document):
    pizza_type: str
    instructions: str

    class Settings:
        name = "pizza_recipes"


class PizzaAnalysisResult(BaseModel):
    order_id: str
    pizza_type: str
    special_instructions: str
    recipes: str
