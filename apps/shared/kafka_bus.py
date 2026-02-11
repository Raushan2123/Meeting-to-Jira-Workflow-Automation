# import json
# from kafka import KafkaProducer, KafkaConsumer
# from apps.shared.config import KAFKA_BOOTSTRAP_SERVERS

# def get_producer():
#     return KafkaProducer(
#         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#         value_serializer=lambda v: json.dumps(v).encode("utf-8")
#     )

# def get_consumer(topic: str, group_id: str):
#     return KafkaConsumer(
#         topic,
#         bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#         group_id=group_id,
#         value_deserializer=lambda m: json.loads(m.decode("utf-8")),
#         auto_offset_reset="earliest"
#     )


from kafka import KafkaConsumer, KafkaProducer
from apps.shared.config import KAFKA_BOOTSTRAP_SERVERS
import json

def get_consumer(topic: str, group_id: str):
    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
