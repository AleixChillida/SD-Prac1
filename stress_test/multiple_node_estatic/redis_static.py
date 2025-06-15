import time
import redis
import random
from multiprocessing import Process
from insult_service.redis_impl.insult_consumer import consumer_process
import os

# Insultos de prueba
INSULTS = [
    "Eres un bobalicón",
    "Vaya chapucero",
    "Pedazo de zopenco",
    "Más tonto que un ladrillo",
    "Tienes menos luces que un sótano"
]

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

def run_stress_test(n_nodes):
    n_processes = 16
    requests_per_process = 10000
    total_requests = n_processes * requests_per_process

    print(f"\nIniciando stress test Redis con {n_nodes} nodos (consumidores)")
    print(f"  - {n_processes} procesos productores")
    print(f"  - {requests_per_process} peticiones por proceso (total: {total_requests})\n")

    # Lanzar consumidores (nodos)
    consumer_processes = []
    for i in range(n_nodes):
        p = Process(target=consumer_process)
        p.start()
        consumer_processes.append(p)

    time.sleep(2)  # Espera breve para asegurar que los consumidores ya están corriendo

    start_time = time.time()

    # Lanzar productores
    producers = []
    for _ in range(n_processes):
        p = Process(target=stress_producer, args=(requests_per_process,))
        p.start()
        producers.append(p)

    for p in producers:
        p.join()

    wait_until_queue_empty()

    end_time = time.time()
    total_time = end_time - start_time
    throughput = total_requests / total_time

    print(f"\n--- Resultados Redis con {n_nodes} nodos ---")
    print(f"Total de peticiones: {total_requests}")
    print(f"Tiempo total: {total_time:.2f} segundos")
    print(f"Rendimiento (throughput): {throughput:.2f} req/s")

    # Terminar consumidores
    for p in consumer_processes:
        p.terminate()
        p.join()

if __name__ == "__main__":
    run_stress_test(2)  # Test con 2 nodos
    run_stress_test(3)  # Test con 3 nodos
