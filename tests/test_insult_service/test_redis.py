import time
import unittest
import redis
from insult_service.redis_impl.insult_producer import InsultProducer
from insult_service.redis_impl.insult_consumer import InsultConsumer
from insult_service.redis_impl.insult_broadcaster import InsultBroadcaster
from insult_service.redis_impl.insult_receiver import InsultReceiver

class TestInsultServiceRedis(unittest.TestCase):
    
    def setUp(self):
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        self.queue_name = "insult_queue"
        self.insults_list = "INSULTS"
        self.channel = "insult_channel"
        self.redis_client.delete(self.queue_name)
        self.redis_client.delete(self.insults_list)
        
    def test_producer_adds_insult_to_queue(self):
        producer = InsultProducer()
        producer.redis.rpush(producer.queue_name, "Test Insult")
        result = producer.redis.lpop(producer.queue_name)
        self.assertEqual(result, "Test Insult")
    
    def test_consumer_processes_insult(self):
        consumer = InsultConsumer()
        consumer.redis_client.rpush(consumer.queue_name, "Test Insult")
        result = consumer.redis_client.blpop(consumer.queue_name, timeout=1)
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "Test Insult")
        
    def test_broadcaster_publishes_insult(self):
        broadcaster = InsultBroadcaster()
        broadcaster.redis.rpush(broadcaster.insults_list, "Test Insult")
        pubsub = broadcaster.redis.pubsub()
        pubsub.subscribe(broadcaster.channel)
        time.sleep(1)
        broadcaster.redis.publish(broadcaster.channel, "Test Insult")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                self.assertEqual(message['data'], "Test Insult")
                break
    
    def test_receiver_receives_insult(self):
        receiver = InsultReceiver("test_receiver")
        pubsub = receiver.redis.pubsub()
        pubsub.subscribe(receiver.channel)
        time.sleep(1)
        receiver.redis.publish(receiver.channel, "Test Insult")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                self.assertEqual(message['data'], "Test Insult")
                break

if __name__ == '__main__':
    unittest.main()