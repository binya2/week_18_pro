import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from api_app.app.routers import order_router, upload_router
from shared.config import settings
from shared.models import PizzaOrders, PizzaAnalysis, PizzaRecipe
from shared.database.mongo_connection import mongo_manager
from shared.database.redis_connection import redis_manager
from shared.database.kafka_connection import kafka_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up services...")
    models: list = [PizzaOrders, PizzaAnalysis, PizzaRecipe]
    await mongo_manager.connect(document_models=models)
    await redis_manager.connect()
    kafka_manager.start()
    yield
    await redis_manager.close()
    await mongo_manager.close()
    kafka_manager.stop()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(order_router)
app.include_router(upload_router)

if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
    )
