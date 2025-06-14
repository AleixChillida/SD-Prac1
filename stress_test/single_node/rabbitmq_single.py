import pika
import random
from multiprocessing import Process

INSULTS = [
    "You are an idiot!", "You are a fool!", "You are stupid!",
    "You are a clown!", "You are a moron!"
]

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'insult_queue'


def stress_producer(n_requests):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    for _ in range(n_requests):
        insult = random.choice(INSULTS)
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=insult)
    connection.close()


def get_queue_message_count():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    queue = channel.queue_declare(queue=QUEUE_NAME, passive=True)  # passive=True no crea cola, solo consulta
    message_count = queue.method.message_count
    connection.close()
    return message_count


def wait_until_queue_empty():
    while True:
        count = get_queue_message_count()
        if count == 0:
            break
        time.sleep(0.05)


def main():
    n_processes = 16
    requests_per_process = 5000
    total_requests = n_processes * requests_per_process

    print(f"Starting RabbitMQ stress test with {n_processes} processes, {requests_per_process} requests each...")

    start_time = time.time()

    # Lanzar productores en paralelo
    processes = []
    for _ in range(n_processes):
        p = Process(target=stress_producer, args=(requests_per_process,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    # Esperar a que la cola quede vacía (consumidor debe estar corriendo)
    wait_until_queue_empty()

    end_time = time.time()
    total_time = end_time - start_time
    throughput = total_requests / total_time

    print("\n--- RabbitMQ Stress Test Results ---")
    print(f"Total requests: {total_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Requests per second (throughput): {throughput:.2f} req/s")


if __name__ == "__main__":
    import time
    main()
