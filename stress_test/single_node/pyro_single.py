import time
import multiprocessing
import Pyro4

# Configuración
NUM_PROCESSES = 16
REQUESTS_PER_PROCESS = 5000
TOTAL_REQUESTS = NUM_PROCESSES * REQUESTS_PER_PROCESS
SERVICE_NAME = "insult.service.1"  # Solo un nodo para single-node

def stress_test_process(proc_id, uri, return_dict):
    try:
        proxy = Pyro4.Proxy(uri)
        local_count = 0

        for i in range(REQUESTS_PER_PROCESS):
            insult = f"You are a fool #{proc_id}-{i}!"
            proxy.add_insult(insult)
            local_count += 1

        return_dict[proc_id] = local_count

    except Exception as e:
        print(f"[Process {proc_id}] ERROR: {e}")
        return_dict[proc_id] = 0

def run_single_node_test():
    print("\n--- Running Pyro single-node stress test ---")

    # Obtener URI del servicio desde el NameServer
    ns = Pyro4.locateNS()
    uri = str(ns.lookup(SERVICE_NAME))

    # Lanzar productores
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []

    start_time = time.time()

    for i in range(NUM_PROCESSES):
        p = multiprocessing.Process(target=stress_test_process, args=(i, uri, return_dict))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    end_time = time.time()
    total_time = end_time - start_time
    throughput = TOTAL_REQUESTS / total_time

    print(f"\n[Result] Total requests: {TOTAL_REQUESTS}")
    print(f"[Result] Total time: {total_time:.2f} seconds")
    print(f"[Result] Throughput: {throughput:.2f} req/s")

def main():
    print("PYRO SINGLE-NODE STRESS TEST")
    run_single_node_test()

if __name__ == "__main__":
    main()
