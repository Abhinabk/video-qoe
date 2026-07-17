from AdminWrapper import KafkaAdmin

def quick_test():
    """
    Quick test function demonstrating KafkaAdmin usage
    Run this to verify your Kafka setup
    """
    print("\n" + "="*70)
    print("KAFKA ADMIN - QUICK TEST")
    print("="*70 + "\n")
    
    # Initialize admin client
    admin = KafkaAdmin(
        bootstrap_servers='localhost:9092'
    )
    
    # Test 1: Create topics with different configurations
    # print("\n[TEST 1] Creating topics...")
    test_topics = ['test-topic-1', 'test-topic-2', 'test-topic-3']
    
    results = admin.create_topics(
        topic_names=test_topics,
        num_partitions=3,
        replication_factor=1,
        retention_ms=604800000,  # 7 days
        compression_type='producer',
        cleanup_policy='delete',
        min_insync_replicas=1,
    )
    print(f"Creation results: {results}")

    # Test 2: Clean up - Delete test topics
    print("\n[TEST 5] Cleaning up - Deleting test topics...")
    delete_results = admin.delete_topics(test_topics)
    print(f"Deletion results: {delete_results}")

quick_test()
    