import time
import redis
import random
import multiprocessing
from collections import Counter

# Configuración
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_BASE = 'insult_queue'

NUM_PROCESSES = 16
REQUESTS_PER_PROCESS = 5000
TOTAL_REQUESTS = NUM_PROCESSES * REQUESTS_PER_PROCESS

INSULTS = [
    "Eres un bobalicón", "Vaya chapucero", "Pedazo de zopenco",
    "Más tonto que un ladrillo", "Tienes menos luces que un sótano"
]

def get_queue_name(index):
    return f"{QUEUE_BASE}_{index}"

def purge_queues(n_queues):
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    for i in range(n_queues):
        r.delete(get_queue_name(i))
    print(f"[Queue] Redis queues 'insult_queue_0' to 'insult_queue_{n_queues - 1}' purged.")

def stress_producer(proc_id, n_requests, n_queues, return_dict):
    try:
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        for i in range(n_requests):
            insult = f"{random.choice(INSULTS)} [{proc_id}-{i}]"
            queue_name = get_queue_name(i % n_queues)
            r.rpush(queue_name, insult)
        return_dict[proc_id] = n_requests
    except Exception as e:
        print(f"[Producer {proc_id}] ERROR: {e}")
        return_dict[proc_id] = 0

def redis_consumer_worker(queue_index):
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    queue_name = get_queue_name(queue_index)
    while True:
        msg = r.lpop(queue_name)
        if msg is None:
            time.sleep(0.05)
        else:
            pass  # Simula procesamiento

def get_total_queue_length(n_queues):
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    return sum(r.llen(get_queue_name(i)) for i in range(n_queues))

def wait_until_queues_empty(n_queues):
    while get_total_queue_length(n_queues) > 0:
        time.sleep(0.05)

def run_stress_test(n_nodes):
    print(f"\n--- Running Redis stress test with {n_nodes} node(s) ---")

    purge_queues(n_nodes)

    # Lanzar consumidores (uno por nodo/cola)
    consumers = []
    for i in range(n_nodes):
        p = multiprocessing.Process(target=redis_consumer_worker, args=(i,))
        p.start()
        consumers.append(p)

    time.sleep(1)  # Asegura que los consumidores estén listos

    # Lanzar productores
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    producers = []

    start_time = time.time()

    for i in range(NUM_PROCESSES):
        p = multiprocessing.Process(
            target=stress_producer,
            args=(i, REQUESTS_PER_PROCESS, n_nodes, return_dict)
        )
        p.start()
        producers.append(p)

    for p in producers:
        p.join()

    wait_until_queues_empty(n_nodes)
    end_time = time.time()

    for c in consumers:
        c.terminate()

    total_time = end_time - start_time
    throughput = TOTAL_REQUESTS / total_time

    print(f"\n[Result] Total requests: {TOTAL_REQUESTS}")
    print(f"[Result] Total time: {total_time:.2f} seconds")
    print(f"[Result] Throughput: {throughput:.2f} req/s")

    return total_time

def main():
    print("REDIS MULTI-NODE STATIC STRESS TEST")

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
