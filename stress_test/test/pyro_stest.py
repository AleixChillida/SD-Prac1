import time
import Pyro4
from multiprocessing import Pool, current_process

NUM_REQUESTS = 1000
NUM_PROCESSES = 20
BLOCK_SIZE = 100

SERVICE_URIS_1_NODE = ["PYRO:insult.service.1@127.0.0.1:9090"]
SERVICE_URIS_2_NODES = [
    "PYRO:insult.service.1@127.0.0.1:9090",
    "PYRO:insult.service.2@127.0.0.1:9091"
]
SERVICE_URIS_3_NODES = [
    "PYRO:insult.service.1@127.0.0.1:9090",
    "PYRO:insult.service.2@127.0.0.1:9091",
    "PYRO:insult.service.3@127.0.0.1:9092"
]

def send_insult(i, service_uris):
    insult = f"insult-{i}"
    proc_name = current_process().name
    service_uri = service_uris[i % len(service_uris)]
    try:
        proxy = Pyro4.Proxy(service_uri)
        proxy._pyroTimeout = 10
        t0 = time.perf_counter()
        proxy.add_insult(insult)
        t1 = time.perf_counter()
        return t1 - t0
    except Exception as e:
        print(f"[{proc_name}] Error enviando {insult} a {service_uri}: {e}")
        return 10.0

def single_node_test():
    print("Iniciando test con un solo nodo...")
    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, SERVICE_URIS_1_NODE) for i in range(NUM_REQUESTS)])
    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time
    print(f"[Pyro - 1 nodo] Tiempo total: {total_time:.2f}s | Throughput: {throughput:.2f} req/s\n")
    return total_time

def static_scaling_test(service_uris):
    print(f"[Pyro - {len(service_uris)} nodos] Ejecutando stress test...")
    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, service_uris) for i in range(NUM_REQUESTS)])
    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time
    print(f"[Pyro - {len(service_uris)} nodos] Tiempo total: {total_time:.2f}s | Throughput: {throughput:.2f} req/s\n")
    return total_time

def compare_static_scaling():
    t1 = static_scaling_test(SERVICE_URIS_1_NODE)
    t2 = static_scaling_test(SERVICE_URIS_2_NODES)
    t3 = static_scaling_test(SERVICE_URIS_3_NODES)
    print(f"Speedup con 1 nodo (base): 1.00")
    print(f"Speedup con 2 nodos: {t1 / t2:.2f}")
    print(f"Speedup con 3 nodos: {t1 / t3:.2f}\n")

def dynamic_scaling(service_uris):
    print("Iniciando test de escalado dinámico...")
    total_requests = NUM_REQUESTS
    processed = 0
    num_procs = 2
    durations = []

    while processed < total_requests:
        current_block = min(BLOCK_SIZE, total_requests - processed)
        with Pool(num_procs) as pool:
            block_durations = pool.starmap(send_insult, [(i, service_uris) for i in range(processed, processed + current_block)])
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
    dynamic_scaling(SERVICE_URIS_3_NODES)

if __name__ == "__main__":
    main()
