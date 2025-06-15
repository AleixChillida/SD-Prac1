import pika
import random
import time
from multiprocessing import Process
import os

INSULTS = [
    "You are an idiot!", "You are a fool!", "You are stupid!",
    "You are a clown!", "You are a moron!"
]

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'insult_queue'


def stress_producer(n_requests):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    for _ in range(n_requests):
        insult = random.choice(INSULTS)
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=insult)
    connection.close()


def rabbitmq_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def callback(ch, method, properties, body):
        _ = body.decode()
        # Simula trabajo opcional (descomenta si quieres ralentizar artificialmente)
        # time.sleep(0.0001)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def get_queue_message_count():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    queue = channel.queue_declare(queue=QUEUE_NAME, passive=True)
    message_count = queue.method.message_count
    connection.close()
    return message_count


def wait_until_queue_empty():
    while True:
        count = get_queue_message_count()
        if count == 0:
            break
        time.sleep(0.05)


def run_test(n_consumers):
    n_processes = 16
    requests_per_process = 10000
    total_requests = n_processes * requests_per_process

    print(f"\n[TEST] Multinode RabbitMQ with {n_consumers} consumers")
    print(f"Producing {total_requests} messages with {n_processes} processes...")

    # Lanzar consumidores
    consumers = []
    for _ in range(n_consumers):
        c = Process(target=rabbitmq_consumer)
        c.start()
        consumers.append(c)

    time.sleep(2)  # Espera para que los consumidores se conecten

    start_time = time.time()

    # Lanzar productores
    producers = []
    for _ in range(n_processes):
        p = Process(target=stress_producer, args=(requests_per_process,))
        p.start()
        producers.append(p)

    for p in producers:
        p.join()

    # Esperar a que la cola esté vacía
    wait_until_queue_empty()

    end_time = time.time()
    total_time = end_time - start_time
    throughput = total_requests / total_time

    print("\n--- RabbitMQ Multinode Stress Test Results ---")
    print(f"Consumers: {n_consumers}")
    print(f"Total requests: {total_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Throughput: {throughput:.2f} req/s")

    # Terminar consumidores
    for c in consumers:
        c.terminate()
        c.join()


if __name__ == "__main__":
    run_test(2)  # Test con 2 nodos
    run_test(3)  # Test con 3 nodos
