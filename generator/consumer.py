from confluent_kafka import Consumer, KafkaError

topic_name = ["video-qoe"]
bootstrap_servers = "localhost:9092"
group_id = "test-group"

consumer = Consumer(
    {
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
    }
)
consumer.subscribe(topic_name)

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF: # pyright: ignore[reportOptionalMemberAccess]
            continue
        else:
            print(f"Consumer error: {msg.error()}")
            continue

    print(f"Partition {msg.partition()}:{msg.value()}")
