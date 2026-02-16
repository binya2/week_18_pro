from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- SERVER ---
    PROJECT_NAME: str = "Pizza Order API"
    DEBUG: bool = True

    # --- MONGO ---
    MONGODB_URL: str = Field(default="mongodb://localhost:27017")
    DATABASE_NAME: str = Field(default="week_18_proo")

    # --- REDIS ---
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: str | None = None
    DECODE_RESPONSES: bool = True

    # --- KAFKA ---
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092")
    KAFKA_CLIENT_ID: str = Field(default="api-service")
    KAFKA_ACKS: str = Field(default="all")
    KAFKA_TOPIC: str = Field(default="pizza-orders")
    KAFKA_CONSUMER_GROUP: str = Field(default="pizza-consumers")

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    def get_kafka_producer_config(self) -> dict:
        return {
            "bootstrap.servers": self.KAFKA_BOOTSTRAP_SERVERS,
            "client.id": self.KAFKA_CLIENT_ID,
            "acks": self.KAFKA_ACKS,
            "linger.ms": 10
        }

    class Config:
        env_file = ".env"


settings = Settings()