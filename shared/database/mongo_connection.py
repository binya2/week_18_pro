from typing import List
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from shared.config import settings


class MongoManager:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None

    async def connect(self, document_models: List):
        print("Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            uuidRepresentation="standard"
        )
        self.database = self.client[settings.DATABASE_NAME]

        await init_beanie(
            database=self.database,
            document_models=document_models
        )
        print("Connected to MongoDB.")

    async def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")


mongo_manager = MongoManager()