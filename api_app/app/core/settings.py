from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- SERVER SETTINGS ---
    server_host: str = Field(default="0.0.0.0", serialization_alias="SERVER_HOST")
    server_port: int = Field(default=8000, serialization_alias="SERVER_PORT")
    debug: bool = Field(default=True, serialization_alias="DEBUG")
    project_name: str = Field(default="app_api", serialization_alias="PROJECT_NAME")
    KAFKA_TOPIC: str = Field(default="documents", serialization_alias="topic")





class KafkaProducerConfig(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092", serialization_alias="bootstrap.servers")
    KAFKA_CLIENT_ID: str = Field(default="api-service", serialization_alias="client.id")
    KAFKA_ACKS: str = Field(default="all", serialization_alias="acks")




class MongoConfig(BaseSettings):
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", )


