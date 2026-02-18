from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- SERVER SETTINGS (הוסף את אלו) ---
    SERVER_HOST: str = Field(default="0.0.0.0")
    SERVER_PORT: int = Field(default=8000)
    DEBUG: bool = True
    PROJECT_NAME: str = "Pizza Order API"

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
    KAFKA_CONSUMER_TOPIC: str = Field(default="default-consumer-topic")
    KAFKA_PRODUCER_TOPIC: str = Field(default="default-producer-topic")
    KAFKA_CONSUMER_GROUP: str = Field(default="default-consumers")

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    class Config:
        env_file = ".env"


settings = Settings()
