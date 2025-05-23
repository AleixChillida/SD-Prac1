import time
import redis
from multiprocessing import Pool, current_process

NUM_REQUESTS = 1000
NUM_PROCESSES = 20
BLOCK_SIZE = 100

QUEUE_NAMES_1_NODE = ["insult_queue.1"]
QUEUE_NAMES_2_NODES = ["insult_queue.1", "insult_queue.2"]
QUEUE_NAMES_3_NODES = ["insult_queue.1", "insult_queue.2", "insult_queue.3"]
RESULT_KEY = "filtered_texts"

INSULTS = [
    "Eres un bobalicón",
    "Vaya chapucero",
    "Pedazo de zopenco",
    "Más tonto que un ladrillo",
    "Tienes menos luces que un sótano",
    "Hola, ¿cómo estás?"
]

def send_insult(i, queue_names):
    insult = INSULTS[i % len(INSULTS)]
    queue = queue_names[i % len(queue_names)]
    proc_name = current_process().name

    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        t0 = time.perf_counter()
        r.rpush(queue, insult)
        t1 = time.perf_counter()
        return t1 - t0
    except Exception as e:
        print(f"[{proc_name}] Error enviando {insult} a {queue}: {e}")
        return 1.0

def clear_queues(queue_names):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    for queue in queue_names:
        r.delete(queue)
    r.delete(RESULT_KEY)

def single_node_test():
    print("Iniciando test con un solo nodo...")
    clear_queues(QUEUE_NAMES_1_NODE)
    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, QUEUE_NAMES_1_NODE) for i in range(NUM_REQUESTS)])
    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time
    print(f"[Redis - 1 nodo] Tiempo total: {total_time:.2f}s | Throughput: {throughput:.2f} req/s\n")
    return total_time

def static_scaling_test(queue_names):
    print(f"[Redis - {len(queue_names)} nodos] Ejecutando stress test...")
    clear_queues(queue_names)
    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, queue_names) for i in range(NUM_REQUESTS)])
    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time
    print(f"[Redis - {len(queue_names)} nodos] Tiempo total: {total_time:.2f}s | Throughput: {throughput:.2f} req/s\n")
    return total_time

def compare_static_scaling():
    t1 = static_scaling_test(QUEUE_NAMES_1_NODE)
    t2 = static_scaling_test(QUEUE_NAMES_2_NODES)
    t3 = static_scaling_test(QUEUE_NAMES_3_NODES)
    print(f"Speedup con 1 nodo (base): 1.00")
    print(f"Speedup con 2 nodos: {t1 / t2:.2f}")
    print(f"Speedup con 3 nodos: {t1 / t3:.2f}\n")

def dynamic_scaling(queue_names):
    print("Iniciando test de escalado dinámico...")
    total_requests = NUM_REQUESTS
    processed = 0
    num_procs = 2
    durations = []

    clear_queues(queue_names)

    while processed < total_requests:
        current_block = min(BLOCK_SIZE, total_requests - processed)
        with Pool(num_procs) as pool:
            block_durations = pool.starmap(send_insult, [(i, queue_names) for i in range(processed, processed + current_block)])
        durations.extend(block_durations)
        processed += current_block

        avg = sum(block_durations) / len(block_durations)
        throughput = current_block / avg if avg > 0 else 0

        if throughput < 50:
            num_procs = min(10, num_procs + 2)
        elif throughput > 100:
            num_procs = max(2, num_procs - 1)


    total_time = sum(durations)
    throughput_total = NUM_REQUESTS / total_time
    print(f"\n[Redis - Escalado dinámico] Tiempo total: {total_time:.2f}s | Throughput total: {throughput_total:.2f} req/s\n")

def main():
    single_node_test()
    compare_static_scaling()
    dynamic_scaling(QUEUE_NAMES_3_NODES)

if __name__ == "__main__":
    main()
