from datagenerator.simulator import run
from wrappers.AdminWrapper import KafkaAdmin
from wrappers.ProducerWrapper import KafkaProducer 
import logging
import json

# log config
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s-%(levelname)s-%(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
#create the topic
topic_name = ["video-qoe"]
bootstrap_servers='localhost:9092'
admin = KafkaAdmin(bootstrap_servers)
admin.create_topics(topic_names=topic_name,num_partitions=5, replication_factor=1)

# the producer
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    acks="all",
    enable_idempotence=True,
    value_serializer=lambda value,ctx: json.dumps(value).encode("utf-8"),
    key_serializer= lambda key,ctx: key.encode("utf-8")
)

# the produce message
def kafka_sink(record: dict):
    producer.produce_msg(
        topic = topic_name[0],
        value=record,
        key=record["region"]
    )

try:
    run(kafka_sink)
except KeyboardInterrupt:
    pass 
finally:
    producer.flush()
