import time
import pika
from multiprocessing import Pool, current_process

NUM_REQUESTS = 1000
NUM_PROCESSES = 20
BLOCK_SIZE = 100

QUEUE_NAMES_1_NODE = ["insult_queue.1"]
QUEUE_NAMES_2_NODES = ["insult_queue.1", "insult_queue.2"]
QUEUE_NAMES_3_NODES = ["insult_queue.1", "insult_queue.2", "insult_queue.3"]

def send_insult(i, queue_names):
    message = f"insult-{i}"
    queue_name = queue_names[i % len(queue_names)]
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=False)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=1)  # No persistente
        )
        connection.close()
    except Exception as e:
        print(f"[{current_process().name}] Error enviando a {queue_name}: {e}")

def single_node_test():
    print("Iniciando test con un solo nodo...")
    t0 = time.perf_counter()
    with Pool(NUM_PROCESSES) as pool:
        pool.starmap(send_insult, [(i, QUEUE_NAMES_1_NODE) for i in range(NUM_REQUESTS)])
    t1 = time.perf_counter()

    real_time = t1 - t0
    throughput = NUM_REQUESTS / real_time
    print(f"[RabbitMQ - 1 nodo] Tiempo REAL de ejecución: {real_time:.2f}s")
    print(f"[RabbitMQ - 1 nodo] Throughput REAL: {throughput:.2f} req/s\n")
    return real_time

def static_scaling_test(queue_names):
    print(f"[RabbitMQ - {len(queue_names)} nodos] Ejecutando stress test...")
    t0 = time.perf_counter()
    with Pool(NUM_PROCESSES) as pool:
        pool.starmap(send_insult, [(i, queue_names) for i in range(NUM_REQUESTS)])
    t1 = time.perf_counter()

    real_time = t1 - t0
    throughput = NUM_REQUESTS / real_time
    print(f"[RabbitMQ - {len(queue_names)} nodos] Tiempo REAL de ejecución: {real_time:.2f}s")
    print(f"[RabbitMQ - {len(queue_names)} nodos] Throughput REAL: {throughput:.2f} req/s\n")
    return real_time

def compare_static_scaling():
    t1 = static_scaling_test(QUEUE_NAMES_1_NODE)
    t2 = static_scaling_test(QUEUE_NAMES_2_NODES)
    t3 = static_scaling_test(QUEUE_NAMES_3_NODES)
    print("Speedups (con tiempo REAL):")
    print(f"Speedup con 1 nodo (base): 1.00")
    print(f"Speedup con 2 nodos: {t1 / t2:.2f}")
    print(f"Speedup con 3 nodos: {t1 / t3:.2f}\n")

def dynamic_scaling(queue_names):
    print("Iniciando test de escalado dinámico...")
    total_requests = NUM_REQUESTS
    processed = 0
    num_procs = 2

    t0_total = time.perf_counter()

    while processed < total_requests:
        current_block = min(BLOCK_SIZE, total_requests - processed)
        t0_block = time.perf_counter()
        with Pool(num_procs) as pool:
            pool.starmap(send_insult, [(i, queue_names) for i in range(processed, processed + current_block)])
        t1_block = time.perf_counter()

        block_time = t1_block - t0_block
        throughput = current_block / block_time if block_time > 0 else 0

        if throughput < 50:
            num_procs = min(10, num_procs + 2)
        elif throughput > 100:
            num_procs = max(2, num_procs - 1)

        processed += current_block

    t1_total = time.perf_counter()
    real_time = t1_total - t0_total
    throughput_total = NUM_REQUESTS / real_time

    print(f"\n[RabbitMQ - Escalado dinámico] Tiempo REAL de ejecución: {real_time:.2f}s")
    print(f"[RabbitMQ - Escalado dinámico] Throughput REAL: {throughput_total:.2f} req/s\n")

def main():
    single_node_test()
    compare_static_scaling()
    dynamic_scaling(QUEUE_NAMES_3_NODES)

if __name__ == "__main__":
    main()
