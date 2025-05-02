import pika
import random
import time
from multiprocessing import Pool

INSULTS = [
    "You are an idiot!", "You are a fool!", "You are stupid!",
    "You are a clown!", "You are a moron!"
]

class StressTestProducer:
    def __init__(self):
        self.queue_name = 'insult_queue'

    def send_insult(self, i):
        """Envía insultos a RabbitMQ"""
        # Conectar a RabbitMQ (una conexión por proceso)
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declarar la cola
        channel.queue_declare(queue=self.queue_name)

        insult = random.choice(INSULTS)
        channel.basic_publish(exchange='', routing_key=self.queue_name, body=insult)
        print(f"Produced: {insult}")

        connection.close()

    def stress_test(self, n_messages=1000, n_processes=20):
        """Ejecuta el stress test enviando insultos con múltiples procesos"""
        start = time.perf_counter()
        with Pool(n_processes) as pool:
            pool.map(self.send_insult, range(n_messages))
        duration = time.perf_counter() - start

        print(f"RABBITMQ - Mensajes enviados: {n_messages}")
        print(f"RABBITMQ - Tiempo total: {duration:.2f} segundos")
        print(f"RABBITMQ - Throughput: {n_messages / duration:.2f} req/s")

if __name__ == "__main__":
    producer = StressTestProducer()
    producer.stress_test(n_messages=1000, n_processes=20)
