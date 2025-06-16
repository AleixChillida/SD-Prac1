import pika
import random
import time
import multiprocessing

# Configuración
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'insult_queue'

NUM_PROCESSES = 16
REQUESTS_PER_PROCESS = 5000
TOTAL_REQUESTS = NUM_PROCESSES * REQUESTS_PER_PROCESS

INSULTS = [
    "You are an idiot!", "You are a fool!", "You are stupid!",
    "You are a clown!", "You are a moron!"
]

def purge_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_purge(queue=QUEUE_NAME)
    connection.close()

def stress_producer(proc_id, n_requests, return_dict):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)

        for _ in range(n_requests):
            insult = f"{random.choice(INSULTS)} [{proc_id}]"
            channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=insult)

        connection.close()
        return_dict[proc_id] = n_requests
    except Exception as e:
        print(f"[Producer {proc_id}] ERROR: {e}")
        return_dict[proc_id] = 0

def consumer_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    stored_insults = set()

    def callback(ch, method, properties, body):
        insult = body.decode()
        if insult not in stored_insults:
            stored_insults.add(insult)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()

def get_queue_message_count():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    queue = channel.queue_declare(queue=QUEUE_NAME, passive=True)
    count = queue.method.message_count
    connection.close()
    return count

def wait_until_queue_empty():
    while get_queue_message_count() > 0:
        time.sleep(0.05)

def run_single_node_test():
    print("\n--- Running RabbitMQ single-node stress test ---")

    purge_queue()

    # Lanzar único consumidor
    consumer = multiprocessing.Process(target=consumer_worker)
    consumer.start()

    time.sleep(2)  # Espera breve para asegurar que el consumidor arranca

    # Lanzar productores
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    producers = []

    start_time = time.time()

    for i in range(NUM_PROCESSES):
        p = multiprocessing.Process(target=stress_producer, args=(i, REQUESTS_PER_PROCESS, return_dict))
        p.start()
        producers.append(p)

    for p in producers:
        p.join()

    wait_until_queue_empty()
    end_time = time.time()

    consumer.terminate()

    total_time = end_time - start_time
    throughput = TOTAL_REQUESTS / total_time

    print(f"\n[Result] Total requests: {TOTAL_REQUESTS}")
    print(f"[Result] Total time: {total_time:.2f} seconds")
    print(f"[Result] Throughput: {throughput:.2f} req/s")

def main():
    print("RABBITMQ SINGLE-NODE STRESS TEST")
    run_single_node_test()

if __name__ == "__main__":
    main()
