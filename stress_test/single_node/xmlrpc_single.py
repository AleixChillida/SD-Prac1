import time
import xmlrpc.client
from multiprocessing import Process, Queue, cpu_count
import random
import string

SERVER_URL = "http://localhost:8000"
NUM_PROCESSES = 16
REQUESTS_PER_PROCESS = 100

def random_insult():
    # Genera un insulto aleatorio
    return "You are a " + ''.join(random.choices(string.ascii_lowercase, k=8)) + "!"

def worker(requests, q):
    server = xmlrpc.client.ServerProxy(SERVER_URL)
    start = time.time()

    for _ in range(requests):
        insult = random_insult()
        server.add_insult(insult)

    end = time.time()
    q.put(end - start)

def main():
    print(f"Starting stress test with {NUM_PROCESSES} processes, "
          f"{REQUESTS_PER_PROCESS} requests each...")

    q = Queue()
    processes = []

    start_time = time.time()

    for _ in range(NUM_PROCESSES):
        p = Process(target=worker, args=(REQUESTS_PER_PROCESS, q))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total_time = time.time() - start_time
    total_requests = NUM_PROCESSES * REQUESTS_PER_PROCESS

    print(f"\nTotal requests: {total_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Requests per second (throughput): {total_requests / total_time:.2f} req/s")

if __name__ == "__main__":
    main()