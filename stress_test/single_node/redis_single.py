import time
import redis
import random
import multiprocessing

# Configuración
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_NAME = 'insult_queue_0'

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

def stress_producer(proc_id, n_requests, return_dict):
    try:
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        for i in range(n_requests):
            insult = f"{random.choice(INSULTS)} [{proc_id}-{i}]"
            r.rpush(QUEUE_NAME, insult)
        return_dict[proc_id] = n_requests
    except Exception as e:
        print(f"[Producer {proc_id}] ERROR: {e}")
        return_dict[proc_id] = 0

def redis_consumer_worker():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    stored_insults = set()

    while True:
        msg = r.lpop(QUEUE_NAME)
        if msg is None:
            time.sleep(0.05)
        else:
            if msg not in stored_insults:
                stored_insults.add(msg)

def get_queue_length():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    return r.llen(QUEUE_NAME)

def wait_until_queue_empty():
    while get_queue_length() > 0:
        time.sleep(0.05)

def run_stress_test():
    print(f"\n--- Running Redis single-node stress test ---")

    purge_queue()

    # Lanzar un único consumidor
    consumer = multiprocessing.Process(target=redis_consumer_worker)
    consumer.start()

    time.sleep(1)  # Espera breve para que el consumidor esté listo

    # Lanzar productores
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    producers = []

    start_time = time.time()

    for i in range(NUM_PROCESSES):
        p = multiprocessing.Process(
            target=stress_producer,
            args=(i, REQUESTS_PER_PROCESS, return_dict)
        )
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

    return total_time

def main():
    print("REDIS SINGLE-NODE STRESS TEST")
    run_stress_test()

if __name__ == "__main__":
    main()
