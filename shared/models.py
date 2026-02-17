from enum import Enum
from typing import Optional, List

from beanie import Document
from pydantic import Field, BaseModel


class Status(str, Enum):
    PREPARING = "preparing"
    DELIVERED = "delivered"
    BURNT = "burnt"


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
