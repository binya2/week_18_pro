from typing import List, Optional
from confluent_kafka import Producer, Consumer
from shared.config import settings


class KafkaManager:
    def __init__(self):
        self._producer: Optional[Producer] = None

    def start(self):

        if self._producer:
            return

        print(f"Connecting to Kafka at {settings.KAFKA_BOOTSTRAP_SERVERS}...")

        conf = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "client.id": settings.KAFKA_CLIENT_ID,
            "acks": settings.KAFKA_ACKS,
            # שיפורי ביצועים מומלצים
            "linger.ms": 10,
            "compression.type": "gzip"
        }

        try:
            self._producer = Producer(conf)
            print("Kafka Producer initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize Kafka Producer: {e}")
            raise e

    def stop(self):

        if self._producer:
            print("Flushing Kafka messages...")
            self._producer.flush(timeout=5.0)
            self._producer = None
            print("Kafka Producer closed.")

    def get_producer(self) -> Producer:

        if not self._producer:
            raise RuntimeError("Kafka Producer is not initialized. Call 'start()' first.")
        return self._producer

    @staticmethod
    def get_consumer(topics: List[str], group_id: str = None) -> Consumer:
        gid = group_id or settings.KAFKA_CONSUMER_GROUP

        conf = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": gid,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True
        }

        consumer = Consumer(conf)
        consumer.subscribe(topics)
        print(f"Created Kafka Consumer for group '{gid}' listening to {topics}")
        return consumer


kafka_manager = KafkaManager()
