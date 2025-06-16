import time
import xmlrpc.client
from multiprocessing import Process, Manager
import random
import string

# Configuración
NUM_PROCESSES = 16
REQUESTS_PER_PROCESS = 100
TOTAL_REQUESTS = NUM_PROCESSES * REQUESTS_PER_PROCESS

# Solo un servidor para la prueba single-node
SERVER_URL = "http://localhost:8001"

def random_insult():
    return "You are a " + ''.join(random.choices(string.ascii_lowercase, k=8)) + "!"

def worker(proc_id, server_url, return_dict):
    try:
        server = xmlrpc.client.ServerProxy(server_url)
        start = time.time()
        for _ in range(REQUESTS_PER_PROCESS):
            insult = random_insult()
            server.add_insult(insult)
        end = time.time()
        return_dict[proc_id] = end - start
    except Exception as e:
        print(f"[Worker {proc_id}] ERROR: {e}")
        return_dict[proc_id] = 0

def run_single_node_test():
    print("\n--- Running XML-RPC single-node stress test ---")

    manager = Manager()
    return_dict = manager.dict()
    processes = []

    start_time = time.time()

    for i in range(NUM_PROCESSES):
        p = Process(target=worker, args=(i, SERVER_URL, return_dict))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    end_time = time.time()
    total_duration = end_time - start_time
    throughput = TOTAL_REQUESTS / total_duration

    print(f"\n[Result] Total requests: {TOTAL_REQUESTS}")
    print(f"[Result] Total time: {total_duration:.2f} seconds")
    print(f"[Result] Throughput: {throughput:.2f} req/s")

def main():
    print("===== XML-RPC SINGLE-NODE STRESS TEST =====")
    run_single_node_test()

if __name__ == "__main__":
    main()
