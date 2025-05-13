import redis
import random
import time
from multiprocessing import Pool
from redis.exceptions import RedisError  # ✅ Importa excepciones correctamente

INSULTS = [
    "You are an idiot!", "You are a fool!", "You are stupid!",
    "You are a clown!", "You are a moron!"
]

class StressTestRedisProducer:
    def __init__(self):
        self.queue_name = 'insult_queue'

    def send_insult(self, i):
        """Envía insultos a Redis (una conexión por proceso)"""
        try:
            r = redis.Redis(  # ✅ Usa redis.Redis en lugar de StrictRedis
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_timeout=10,
                socket_keepalive=True
            )

            insult = random.choice(INSULTS)
            r.rpush(self.queue_name, insult)
            print(f"Produced: {insult}")

        except RedisError as e:  # ✅ Usa la excepción importada
            print(f"Error en el envío: {str(e)}")

    def stress_test(self, n_messages=1000, n_processes=20):
        """Ejecuta el stress test enviando insultos con múltiples procesos"""
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
