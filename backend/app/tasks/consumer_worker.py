import json
import logging
import sys
from confluent_kafka import Consumer, KafkaError, KafkaException
from app.core.config import settings
from app.tasks.agent_tasks import run_agent_workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_consumer():
    conf = {
        'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'agent-workflow-consumer-group',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(conf)
    topic = 'agent-events'
    consumer.subscribe([topic])
    logger.info(f"Subscribed to topic: {topic}")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(f"{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Proper message
                try:
                    event_data = json.loads(msg.value().decode('utf-8'))
                    logger.info(f"Received event: {event_data}")
                    
                    # Dispatch to Celery for asynchronous processing
                    run_agent_workflow.delay(event_data)
                    logger.info(f"Dispatched event {event_data.get('event_id', 'unknown')} to Celery")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    logger.info("Starting Kafka Consumer Worker...")
    run_consumer()
