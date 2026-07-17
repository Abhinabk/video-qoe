print("\n[TEST 3] Adding partitions...")
    partition_results = admin.add_partitions_to_topic(
        topic_partitions={'test-topic-1': 5}  # Increase to 5 partitions
    )
    print(f"Partition addition results: {partition_results}")