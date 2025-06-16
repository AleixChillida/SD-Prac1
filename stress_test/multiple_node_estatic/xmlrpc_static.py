import time
import xmlrpc.client
from multiprocessing import Process, Queue
import random
import string

# Lista de URLs de servidores XML-RPC (cada uno representa un nodo)
SERVER_URLS = [
    "http://localhost:8001",  # Nodo 1
    "http://localhost:8002",  # Nodo 2
    "http://localhost:8003"   # Nodo 3
]

NUM_PROCESSES = 16                # Número total de procesos paralelos
REQUESTS_PER_PROCESS = 100        # Peticiones por proceso

# Genera un insulto aleatorio con letras minúsculas
def random_insult():
    return "You are a " + ''.join(random.choices(string.ascii_lowercase, k=8)) + "!"

# Función ejecutada por cada proceso: envía N peticiones a un servidor aleatorio
def worker(requests, q, server_urls):
    server_url = random.choice(server_urls)                    # Selecciona un servidor
    server = xmlrpc.client.ServerProxy(server_url)             # Proxy al servidor remoto
    start = time.time()

    for _ in range(requests):
        insult = random_insult()
        server.add_insult(insult)                              # Llamada RPC al método remoto

    end = time.time()
    q.put(end - start)                                         # Registra el tiempo que tardó

# Ejecuta el test completo con el número de nodos indicado
def run_stress_test(num_nodes):
    service_urls = SERVER_URLS[:num_nodes]                    # Usa solo los N primeros nodos

    print(f"\n--- Running stress test with {num_nodes} node(s) ---")

    q = Queue()
    processes = []
    start_time = time.time()

    # Lanza procesos que realizarán peticiones distribuidas entre los servidores
    for _ in range(NUM_PROCESSES):
        p = Process(target=worker, args=(REQUESTS_PER_PROCESS, q, service_urls))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total_time = time.time() - start_time
    total_requests = NUM_PROCESSES * REQUESTS_PER_PROCESS

    print(f"\nTotal requests: {total_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Requests per second (throughput): {total_requests / total_time:.2f} req/s")

    return total_time

# Función principal que ejecuta el test con 1, 2 y 3 nodos y calcula speedups
def main():
    print("===== XML-RPC MULTI-NODE STATIC STRESS TEST =====")

    times = {}
    for n in [1, 2, 3]:
        time_taken = run_stress_test(n)
        times[n] = time_taken

    print("\n===== SPEEDUP ANALYSIS =====")
    t1 = times[1]
    for n in [2, 3]:
        speedup = t1 / times[n]
        print(f"[Speedup] {n} node(s): {speedup:.2f} (T1 = {t1:.2f}s, T{n} = {times[n]:.2f}s)")

if __name__ == "__main__":
    main()
