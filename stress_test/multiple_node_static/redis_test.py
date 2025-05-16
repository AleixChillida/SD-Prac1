import redis
import random
import time
from multiprocessing import Pool
from redis.exceptions import RedisError

INSULTS = [
    "You are an idiot!", "You are a fool!", "You are stupid!",
    "You are a clown!", "You are a moron!"
]

QUEUE_NAMES = ['insult_queue_1', 'insult_queue_2', 'insult_queue_3']

class StressTestRedisProducer:
    def __init__(self):
        pass

    def send_insult(self, i):
        try:
            r = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_timeout=10,
                socket_keepalive=True
            )

            queue_name = QUEUE_NAMES[i % len(QUEUE_NAMES)]  # Round-robin en listas
            insult = random.choice(INSULTS)
            r.rpush(queue_name, insult)

        except RedisError as e:
            print(f"Error en el envío a {queue_name}: {str(e)}")

    def stress_test(self, n_messages=1000, n_processes=20):
        start = time.perf_counter()
        with Pool(n_processes) as pool:
            pool.map(self.send_insult, range(n_messages))
        duration = time.perf_counter() - start

        print(f"REDIS - Mensajes enviados: {n_messages}")
        print(f"REDIS - Tiempo total: {duration:.2f} segundos")
        print(f"REDIS - Throughput: {n_messages / duration:.2f} req/s")

if __name__ == "__main__":
    producer = StressTestRedisProducer()
    producer.stress_test(n_messages=1000, n_processes=20)
