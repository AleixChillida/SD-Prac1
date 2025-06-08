import time
import redis
import random
from multiprocessing import Process, current_process
from datetime import datetime

# Insultos de prueba
INSULTS = [
    "Eres un bobalicón",
    "Vaya chapucero",
    "Pedazo de zopenco",
    "Más tonto que un ladrillo",
    "Tienes menos luces que un sótano"
]

# Configuración de Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_NAME = 'insult_queue'


def stress_producer(n_requests):
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    for _ in range(n_requests):
        insult = random.choice(INSULTS)
        r.rpush(QUEUE_NAME, insult)


def wait_until_queue_empty():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    while r.llen(QUEUE_NAME) > 0:
        time.sleep(0.05)


def main():
    n_processes = 8
    requests_per_process = 100
    total_requests = n_processes * requests_per_process

    print(f"Starting Redis stress test with {n_processes} processes, {requests_per_process} requests each...")

    start_time = time.time()

    # Lanzar procesos
    processes = []
    for _ in range(n_processes):
        p = Process(target=stress_producer, args=(requests_per_process,))
        p.start()
        processes.append(p)

    # Esperar a que todos terminen
    for p in processes:
        p.join()

    # Esperar a que la cola se vacíe (el consumidor debe estar corriendo)
    wait_until_queue_empty()

    end_time = time.time()

    total_time = end_time - start_time
    throughput = total_requests / total_time

    print("\n--- Redis Stress Test Results ---")
    print(f"Total requests: {total_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Requests per second (throughput): {throughput:.2f} req/s")


if __name__ == "__main__":
    main()
