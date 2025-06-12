import time
import redis
import random
import multiprocessing
from collections import Counter

# Configuración
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_NAME = 'insult_queue'

NUM_PROCESSES = 16
REQUESTS_PER_PROCESS = 5000
TOTAL_REQUESTS = NUM_PROCESSES * REQUESTS_PER_PROCESS

INSULTS = [
    "Eres un bobalicón", "Vaya chapucero", "Pedazo de zopenco",
    "Más tonto que un ladrillo", "Tienes menos luces que un sótano"
]

def purge_queue():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.delete(QUEUE_NAME)
    print(f"[Queue] Redis list '{QUEUE_NAME}' purged.")

def stress_producer(proc_id, n_requests, return_dict):
    try:
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        for _ in range(n_requests):
            insult = f"{random.choice(INSULTS)} [{proc_id}]"
            r.rpush(QUEUE_NAME, insult)
        return_dict[proc_id] = n_requests
    except Exception as e:
        print(f"[Producer {proc_id}] ERROR: {e}")
        return_dict[proc_id] = 0

def redis_consumer_worker():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    while True:
        msg = r.lpop(QUEUE_NAME)
        if msg is None:
            time.sleep(0.05)
        else:
            pass  # Simula procesamiento

def get_queue_length():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    return r.llen(QUEUE_NAME)

def wait_until_queue_empty():
    while get_queue_length() > 0:
        time.sleep(0.05)

def run_stress_test(n_nodes):
    print(f"\n--- Running Redis stress test with {n_nodes} node(s) ---")

    purge_queue()  # Limpia antes de empezar

    # Lanzar consumidores
    consumers = []
    for _ in range(n_nodes):
        p = multiprocessing.Process(target=redis_consumer_worker)
        p.start()
        consumers.append(p)

    time.sleep(2)

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
