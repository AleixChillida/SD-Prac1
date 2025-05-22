import time
import xmlrpc.client
from multiprocessing import Pool, current_process
import math

NUM_REQUESTS = 1000
NUM_PROCESSES = 20
BLOCK_SIZE = 100

SERVICE_NAMES_1_NODE = ["http://localhost:8000"]
SERVICE_NAMES_2_NODES = ["http://localhost:8000", "http://localhost:8001"]
SERVICE_NAMES_3_NODES = ["http://localhost:8000", "http://localhost:8001", "http://localhost:8002"]

def send_insult(i, service_names):
    insult = f"insult-{i}"
    proc_name = current_process().name

    service_url = service_names[i % len(service_names)]

    try:
        proxy = xmlrpc.client.ServerProxy(service_url)
        t0 = time.perf_counter()
        result = proxy.add_insult(insult)
        t1 = time.perf_counter()
        return t1 - t0
    except Exception as e:
        print(f"[{proc_name}] Error enviando {insult} a {service_url}: {str(e)}")
        return 0

def single_node_performance():
    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, SERVICE_NAMES_1_NODE) for i in range(NUM_REQUESTS)])

    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time if total_time > 0 else 0

    print(f"[Single Node] Mensajes enviados: {NUM_REQUESTS}")
    print(f"[Single Node] Tiempo total: {total_time:.2f}s")
    print(f"[Single Node] Throughput: {throughput:.2f} req/s\n")
    return total_time

def static_scaling_performance(service_names):
    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, service_names) for i in range(NUM_REQUESTS)])

    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time if total_time > 0 else 0

    print(f"[XML-RPC - Concurrente {len(service_names)} nodos] Mensajes enviados: {NUM_REQUESTS}")
    print(f"[XML-RPC - Concurrente {len(service_names)} nodos] Tiempo total: {total_time:.2f}s")
    print(f"[XML-RPC - Concurrente {len(service_names)} nodos] Throughput: {throughput:.2f} req/s\n")
    return total_time

def compare_static_scaling():
    t1 = static_scaling_performance(SERVICE_NAMES_1_NODE)
    t2 = static_scaling_performance(SERVICE_NAMES_2_NODES)
    t3 = static_scaling_performance(SERVICE_NAMES_3_NODES)

    print(f"Speedup con 1 nodo (referencia): 1.00")
    print(f"Speedup con 2 nodos: {t1 / t2:.2f}")
    print(f"Speedup con 3 nodos: {t1 / t3:.2f}")

def dynamic_scaling(service_names):
    total_requests = NUM_REQUESTS
    processed = 0
    num_procs = 2
    durations = []

    print(f"Iniciando escalado dinámico con {total_requests} solicitudes")

    while processed < total_requests:
        remaining = total_requests - processed
        current_block = min(BLOCK_SIZE, remaining)

        print(f"\nProcesando bloque: solicitudes {processed} a {processed + current_block - 1} con {num_procs} procesos")

        with Pool(processes=num_procs) as pool:
            block_durations = pool.starmap(send_insult, [(i, service_names) for i in range(processed, processed + current_block)])

        processed += current_block
        durations.extend(block_durations)

        avg_duration = sum(block_durations) / len(block_durations) if block_durations else 0.1
        throughput = current_block / avg_duration if avg_duration > 0 else 0

        if throughput < 50:
            num_procs = min(10, num_procs + 2)
        elif throughput > 100:
            num_procs = max(2, num_procs - 1)

        print(f"Bloque terminado. Duración media por petición: {avg_duration:.4f}s")
        print(f"Estimación workers necesarios para siguiente bloque: {num_procs}")

    total_time = sum(durations)
    throughput = total_requests / total_time if total_time > 0 else 0

    print(f"\nTest finalizado.")
    print(f"Total solicitudes: {total_requests}")
    print(f"Tiempo total: {total_time:.2f}s")
    print(f"Throughput: {throughput:.2f} req/s")

def main():
    print("Iniciando test con un solo nodo...")
    single_node_performance()

    print("Iniciando prueba de escalado estático con 1, 2 y 3 nodos...")
    compare_static_scaling()

    print("Iniciando prueba de escalado dinámico con múltiples nodos...")
    dynamic_scaling(SERVICE_NAMES_3_NODES)

if __name__ == "__main__":
    main()
