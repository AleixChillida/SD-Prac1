import time
import redis
import subprocess
import os
from multiprocessing import Pool, current_process

NUM_REQUESTS = 1000
NUM_PROCESSES = 20
BATCH_SIZE = NUM_REQUESTS // NUM_PROCESSES

QUEUE_NAMES_1_NODE = ["insult_queue.1"]
QUEUE_NAMES_2_NODES = ["insult_queue.1", "insult_queue.2"]
QUEUE_NAMES_3_NODES = ["insult_queue.1", "insult_queue.2", "insult_queue.3"]
RESULT_KEY = "filtered_texts"

# Enviar lote de insultos
def send_insult_batch(start_index, count, queue_names):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    for i in range(start_index, start_index + count):
        insult = f"insult-{i}"
        queue = queue_names[i % len(queue_names)]
        try:
            r.rpush(queue, insult)
        except Exception as e:
            print(f"[{current_process().name}] Error enviando {insult} a {queue}: {e}")

# Limpiar colas
def clear_queues(queue_names):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    for queue in queue_names:
        r.delete(queue)
    r.delete(RESULT_KEY)

# Lanzar consumers desde redis_impl/insult_consumer3.py
def launch_consumers(queue_names):
    processes = []
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "insult_service", "redis_impl", "insult_consumer3.py"))

    for i, _ in enumerate(queue_names):
        p = subprocess.Popen(["python", script_path, str(i)])
        processes.append(p)

    time.sleep(2)  # Esperamos a que arranquen
    return processes

# Terminar consumers
def terminate_consumers(processes):
    for p in processes:
        p.terminate()
        p.wait()

# Test base
def run_test(queue_names, label=""):
    clear_queues(queue_names)
    consumers = launch_consumers(queue_names)

    t0 = time.perf_counter()
    with Pool(NUM_PROCESSES) as pool:
        args = [(i * BATCH_SIZE, BATCH_SIZE, queue_names) for i in range(NUM_PROCESSES)]
        pool.starmap(send_insult_batch, args)
    t1 = time.perf_counter()

    terminate_consumers(consumers)

    real_time = t1 - t0
    throughput = NUM_REQUESTS / real_time

    print(f"[Redis - {label}] Tiempo total: {real_time:.2f}s | Throughput: {throughput:.2f} req/s\n")
    return real_time

# Escalado estático
def compare_static_scaling():
    t1 = run_test(QUEUE_NAMES_1_NODE, "1 nodo")
    t2 = run_test(QUEUE_NAMES_2_NODES, "2 nodos")
    t3 = run_test(QUEUE_NAMES_3_NODES, "3 nodos")
    print("Speedups (con tiempo REAL):")
    print(f"Speedup con 1 nodo (base): 1.00")
    print(f"Speedup con 2 nodos: {t1 / t2:.2f}")
    print(f"Speedup con 3 nodos: {t1 / t3:.2f}\n")

# Escalado dinámico
def dynamic_scaling(queue_names):
    print("Iniciando test de escalado dinámico...")
    clear_queues(queue_names)
    consumers = launch_consumers(queue_names)

    total_requests = NUM_REQUESTS
    processed = 0
    num_procs = 2
    block_size = 100

    t0_total = time.perf_counter()

    while processed < total_requests:
        current_block = min(block_size, total_requests - processed)
        t0_block = time.perf_counter()
        with Pool(num_procs) as pool:
            args = [(processed + i, 1, queue_names) for i in range(current_block)]
            pool.starmap(send_insult_batch, args)
        t1_block = time.perf_counter()

        block_time = t1_block - t0_block
        throughput = current_block / block_time

        if throughput < 50:
            num_procs = min(10, num_procs + 2)
        elif throughput > 100:
            num_procs = max(2, num_procs - 1)

        processed += current_block

    t1_total = time.perf_counter()
    terminate_consumers(consumers)

    real_time = t1_total - t0_total
    throughput_total = NUM_REQUESTS / real_time

    print(f"\n[Redis - Escalado dinámico] Tiempo total: {real_time:.2f}s | Throughput total: {throughput_total:.2f} req/s\n")

def main():
    run_test(QUEUE_NAMES_1_NODE, "1 nodo")
    compare_static_scaling()
    dynamic_scaling(QUEUE_NAMES_3_NODES)

if __name__ == "__main__":
    main()
