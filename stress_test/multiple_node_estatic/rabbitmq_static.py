import pika
import random
import time
import multiprocessing
from collections import Counter

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

    stored_insults = set()  # Simulación de add_insult

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
    message_count = queue.method.message_count
    connection.close()
    return message_count

def wait_until_queue_empty():
    while True:
        if get_queue_message_count() == 0:
            break
        time.sleep(0.05)

def run_stress_test(n_nodes):
    print(f"\n--- Running stress test with {n_nodes} node(s) ---")

    purge_queue()

    # Lanzar consumidores
    consumers = []
    for _ in range(n_nodes):
        p = multiprocessing.Process(target=consumer_worker)
        p.start()
        consumers.append(p)

    time.sleep(2)  # Esperar a que los consumidores arranquen

    start_time = time.time()

    # Lanzar productores
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    producers = []

    for i in range(NUM_PROCESSES):
        p = multiprocessing.Process(target=stress_producer, args=(i, REQUESTS_PER_PROCESS, return_dict))
        p.start()
        producers.append(p)

    for p in producers:
        p.join()

    wait_until_queue_empty()
    end_time = time.time()
    total_time = end_time - start_time
    throughput = TOTAL_REQUESTS / total_time

    # Detener consumidores
    for c in consumers:
        c.terminate()

    usage = Counter(return_dict.values())

    print(f"\n[Result] Total requests: {TOTAL_REQUESTS}")
    print(f"[Result] Total time: {total_time:.2f} seconds")
    print(f"[Result] Throughput: {throughput:.2f} req/s")

    return total_time

def main():
    print("RABBITMQ MULTI-NODE STATIC STRESS TEST")

    times = {}
    for n in [1, 2, 3]:
        time_taken = run_stress_test(n)
        if time_taken:
            times[n] = time_taken
        else:
            print(f"[Error] Test failed for {n} nodes")
            return

    print("\n===== SPEEDUP ANALYSIS =====")
    t1 = times[1]
    for n in [2, 3]:
        speedup = t1 / times[n]
        print(f"[Speedup] {n} node(s): {speedup:.2f}x (T1 = {t1:.2f}s, T{n} = {times[n]:.2f}s)")

if __name__ == "__main__":
    main()
