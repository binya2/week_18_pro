from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from ..core import mongo_config
from ..models import PizzaOrders


async def init_db():
    """Initialize database connection and Beanie ODM"""
    # Create MongoDB client
    client = AsyncIOMotorClient(mongo_config.MONGODB_URL)

    # Initialize Beanie with all document models
    await init_beanie(
        database=client[mongo_config.DATABASE_NAME],
        document_models=[PizzaOrders]
    )


