import json
import logging
from confluent_kafka import Producer
from app.core.config import settings

logger = logging.getLogger(__name__)

class EventProducer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventProducer, cls).__new__(cls)
            cls._instance._init_producer()
        return cls._instance

    def _init_producer(self):
        conf = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'packagepro-backend-producer'
        }
        self.producer = Producer(conf)

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def send_event(self, topic: str, event_data: dict):
        try:
            value = json.dumps(event_data).encode('utf-8')
            self.producer.produce(topic, value, callback=self.delivery_report)
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")

    def flush(self):
        self.producer.flush()

# Singleton instance
kafka_producer = EventProducer()
