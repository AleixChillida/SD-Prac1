# xmlrpc_stress_test.py
import time
import xmlrpc.client
from multiprocessing import Pool, current_process

NUM_REQUESTS = 1000
NUM_PROCESSES = 20
BLOCK_SIZE = 100
SERVICE_NAMES_1_NODE = ["http://127.0.0.1:8000"]
SERVICE_NAMES_2_NODES = ["http://127.0.0.1:8000", "http://127.0.0.1:8001"]
SERVICE_NAMES_3_NODES = ["http://127.0.0.1:8000", "http://127.0.0.1:8001", "http://127.0.0.1:8002"]

def send_insult(i, service_urls):
    insult = f"insult-{i}"
    proc_name = current_process().name
    service_url = service_urls[i % len(service_urls)]

    try:
        transport = xmlrpc.client.Transport()
        transport.timeout = 10
        proxy = xmlrpc.client.ServerProxy(service_url, transport=transport)
        t0 = time.perf_counter()
        proxy.add_insult(insult)
        t1 = time.perf_counter()
        return t1 - t0
    except Exception as e:
        print(f"[{proc_name}] Error enviando {insult} a {service_url}: {e}")
        return 10.0  # Penalización si falla

def single_node_test():
    print("Iniciando test con un solo nodo...")
    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, SERVICE_NAMES_1_NODE) for i in range(NUM_REQUESTS)])
    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time
    print(f"[XML-RPC - 1 nodo] Tiempo total: {total_time:.2f}s | Throughput: {throughput:.2f} req/s\n")
    return total_time

def static_scaling_test(service_urls):
    print(f"[XML-RPC - {len(service_urls)} nodos] Ejecutando stress test...")
    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, service_urls) for i in range(NUM_REQUESTS)])
    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time
    print(f"[XML-RPC - {len(service_urls)} nodos] Tiempo total: {total_time:.2f}s | Throughput: {throughput:.2f} req/s\n")
    return total_time

def compare_static_scaling():
    t1 = static_scaling_test(SERVICE_NAMES_1_NODE)
    t2 = static_scaling_test(SERVICE_NAMES_2_NODES)
    t3 = static_scaling_test(SERVICE_NAMES_3_NODES)
    print(f"Speedup con 1 nodo (base): 1.00")
    print(f"Speedup con 2 nodos: {t1 / t2:.2f}")
    print(f"Speedup con 3 nodos: {t1 / t3:.2f}\n")

def dynamic_scaling(service_urls):
    print("Iniciando test de escalado dinámico...")
    total_requests = NUM_REQUESTS
    processed = 0
    num_procs = 2
    durations = []

    while processed < total_requests:
        current_block = min(BLOCK_SIZE, total_requests - processed)
        with Pool(num_procs) as pool:
            block_durations = pool.starmap(send_insult, [(i, service_urls) for i in range(processed, processed + current_block)])
        durations.extend(block_durations)
        processed += current_block

        avg = sum(block_durations) / len(block_durations)
        throughput = current_block / avg

        if throughput < 50:
            num_procs = min(10, num_procs + 2)
        elif throughput > 100:
            num_procs = max(2, num_procs - 1)

    total_time = sum(durations)
    print(f"\n[Escalado dinámico] Tiempo total: {total_time:.2f}s | Throughput total: {NUM_REQUESTS / total_time:.2f} req/s\n")

def main():
    single_node_test()
    compare_static_scaling()
    dynamic_scaling(SERVICE_NAMES_3_NODES)

if __name__ == "__main__":
    main()
