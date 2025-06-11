# xmlrpc_multinode_stress.py
import time
import xmlrpc.client
from multiprocessing import Process, Queue
import random
import string

# URLs de los servidores
SERVER_URLS = [
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:8002"
]

NUM_PROCESSES = 32
REQUESTS_PER_PROCESS = 100

def random_insult():
    return "You are a " + ''.join(random.choices(string.ascii_lowercase, k=8)) + "!"

def worker(requests, q, server_url):
    server = xmlrpc.client.ServerProxy(server_url)
    start = time.time()

    for _ in range(requests):
        insult = random_insult()
        server.add_insult(insult)

    end = time.time()
    q.put(end - start)

def main():
    n_servers = len(SERVER_URLS)
    q = Queue()
    processes = []

    print(f"Starting XML-RPC stress test with {NUM_PROCESSES} processes, "
          f"{REQUESTS_PER_PROCESS} requests each, across {n_servers} servers...")

    start_time = time.time()

    for i in range(NUM_PROCESSES):
        server_url = SERVER_URLS[i % n_servers]
        p = Process(target=worker, args=(REQUESTS_PER_PROCESS, q, server_url))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total_time = time.time() - start_time
    total_requests = NUM_PROCESSES * REQUESTS_PER_PROCESS

    print(f"\n--- XML-RPC Multi-node Stress Test Results ---")
    print(f"Total requests: {total_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Requests per second (throughput): {total_requests / total_time:.2f} req/s")

if __name__ == "__main__":
    main()