from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic  # pyright: ignore[reportPrivateImportUsage]
import logging


# log config
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s-%(levelname)s-%(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class KafkaAdmin:
    def __init__(self, bootstrap_servers: str | list[str], **config) -> None:
        """
        creates the Admin client configure topics and paritions and brokers
        bootstrap_server: host:port or list of host:port initial server python connects to
        **config: any extra configuration properties
        """
        if isinstance(bootstrap_servers, list):
            bs = ",".join(bootstrap_servers)
        else:
            bs = str(bootstrap_servers)

        # inital configs
        self.configs = {
            "bootstrap.servers": bs,
            "socket.timeout.ms": 30_000,  # timeout for network requests
            "request.timeout.ms": 40_000,  # time to wait for ack to come from broker if acks!=0
        }
        self.configs.update(config)
        self.admin_client = AdminClient(self.configs)
        logger.info(f"Kafka Admin initialized with brokers: {bs}")

    def create_topics(
        self,
        topic_names: list[str],
        num_partitions: int = 3,
        replication_factor: int = 1,
        retention_ms: int | None = None,
        cleanup_policy: str = "delete",
        min_insync_replicas: int = 1,
        compression_type: str = "producer",
    ) -> dict[str, bool]:
        """
        Creates the topics and returns a dict with each topic matched to a bool
        indicating if topics were created or not
        This method calls .results() resolving the futures making it a blocking
        operation- its intended.
        """
        topic_config = {}
        if cleanup_policy:
            topic_config["cleanup.policy"] = cleanup_policy
        if min_insync_replicas:
            topic_config["min.insync.replicas"] = str(min_insync_replicas)
        if compression_type:
            topic_config["compression.type"] = compression_type
        if retention_ms:
            topic_config["retention.ms"] = str(retention_ms)

        new_topics = [
            NewTopic(
                topic=t,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
                config=topic_config,
            )
            for t in topic_names
        ]
        futures = self.admin_client.create_topics(new_topics)

        results: dict[str, bool] = {}

        for topic, future in futures.items():
            try:
                future.result()
                logger.info(f"Topic {topic} created successfully")
                results[topic] = True
            except KafkaException as e:
                logger.error(f"Failed to create topic {topic}: {e}")
                results[topic] = False
        return results
    

    def delete_topics(self, topic_names: list[str]) -> dict[str, bool]:

        futures = self.admin_client.delete_topics(topic_names)
        results: dict[str, bool] = {}

        for topic, fut in futures.items():
            try:
                fut.result()
                logger.info(f"Topic '{topic}' deleted successfully")
                results[topic] = True
            except KafkaException as e:
                logger.error(f"Failed to delete topic '{topic}': {e}")
                results[topic] = False
        return results
