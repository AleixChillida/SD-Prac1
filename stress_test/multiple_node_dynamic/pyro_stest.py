import time
import Pyro4
from multiprocessing import Pool, current_process
import math

NUM_REQUESTS = 1000
NUM_PROCESSES = 20
BLOCK_SIZE = 100  # Número de peticiones por bloque
SERVICE_NAMES_1_NODE = ["insult.service.1"]
SERVICE_NAMES_2_NODES = ["insult.service.1", "insult.service.2"]
SERVICE_NAMES_3_NODES = ["insult.service.1", "insult.service.2", "insult.service.3"]

# Función para enviar insulto
def send_insult(i, service_names):
    insult = f"insult-{i}"
    proc_name = current_process().name

    service_name = service_names[i % len(service_names)]

    try:
        ns = Pyro4.locateNS()
        uri = ns.lookup(service_name)
        proxy = Pyro4.Proxy(uri)
        proxy._pyroTimeout = 10  # Timeout para la llamada

        t0 = time.perf_counter()
        result = proxy.add_insult(insult)
        t1 = time.perf_counter()

        return t1 - t0

    except Exception as e:
        print(f"[{proc_name}] Error enviando {insult} a {service_name}: {str(e)}")
        return 0

# ---------------------------------------------------------------
# 1. Single-node performance analysis
# ---------------------------------------------------------------
def single_node_performance():
    start = time.perf_counter()

    # Ejecutar el test con un solo nodo
    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, SERVICE_NAMES_1_NODE) for i in range(NUM_REQUESTS)])

    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time if total_time > 0 else 0

    print(f"[Single Node] Mensajes enviados: {NUM_REQUESTS}")
    print(f"[Single Node] Tiempo total: {total_time:.2f}s")
    print(f"[Single Node] Throughput: {throughput:.2f} req/s\n")

    return total_time  # Para calcular el speedup más tarde

# ---------------------------------------------------------------
# 2. Multiple-nodes static scaling performance analysis
# ---------------------------------------------------------------
def static_scaling_performance(service_names):
    start = time.perf_counter()

    with Pool(NUM_PROCESSES) as pool:
        durations = pool.starmap(send_insult, [(i, service_names) for i in range(NUM_REQUESTS)])

    total_time = sum(durations)
    throughput = NUM_REQUESTS / total_time if total_time > 0 else 0

    print(f"[PyRO - Concurrente {len(service_names)} nodos] Mensajes enviados: {NUM_REQUESTS}")
    print(f"[PyRO - Concurrente {len(service_names)} nodos] Tiempo total: {total_time:.2f}s")
    print(f"[PyRO - Concurrente {len(service_names)} nodos] Throughput: {throughput:.2f} req/s\n")

    return total_time  # Retorna el tiempo para calcular el speedup más tarde

def compare_static_scaling():
    # Test con 1, 2 y 3 nodos
    time_single_node = static_scaling_performance(SERVICE_NAMES_1_NODE)
    time_two_nodes = static_scaling_performance(SERVICE_NAMES_2_NODES)
    time_three_nodes = static_scaling_performance(SERVICE_NAMES_3_NODES)

    # Calcular speedups
    speedup_two_nodes = time_single_node / time_two_nodes if time_two_nodes > 0 else 0
    speedup_three_nodes = time_single_node / time_three_nodes if time_three_nodes > 0 else 0

    print(f"Speedup con 2 nodos: {speedup_two_nodes:.2f}")
    print(f"Speedup con 3 nodos: {speedup_three_nodes:.2f}")

# ---------------------------------------------------------------
# 3. Multiple-nodes dynamic scaling performance analysis
# ---------------------------------------------------------------
def dynamic_scaling(service_names):
    total_requests = NUM_REQUESTS
    processed = 0
    num_procs = 2  # Empezamos con 2 procesos
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

        # Calculamos tiempo medio del bloque
        avg_duration = sum(block_durations) / len(block_durations) if block_durations else 0.1
        throughput = current_block / avg_duration if avg_duration > 0 else 0

        # Ajuste dinámico de workers
        if throughput < 50:
            num_procs = min(10, num_procs + 2)  # Aumentamos si throughput es bajo
        else:
            num_procs = max(2, num_procs - 1)  # Reducimos si throughput es alto

        print(f"Bloque terminado. Duración media por petición: {avg_duration:.4f}s")
        print(f"Estimación workers necesarios para siguiente bloque: {num_procs}")

    total_time = sum(durations)
    throughput = total_requests / total_time if total_time > 0 else 0

    print(f"\nTest finalizado.")
    print(f"Total solicitudes: {total_requests}")
    print(f"Tiempo total: {total_time:.2f}s")
    print(f"Throughput: {throughput:.2f} req/s")

# ---------------------------------------------------------------
# Función principal que ejecuta todos los análisis
# ---------------------------------------------------------------
def main():
    # 1. Single-node performance analysis
    print("Iniciando test con un solo nodo...")
    single_node_performance()

    # 2. Multiple-nodes static scaling performance analysis
    print("Iniciando prueba de escalado estático con 1, 2 y 3 nodos...")
    compare_static_scaling()

    # 3. Multiple-nodes dynamic scaling performance analysis
    print("Iniciando prueba de escalado dinámico con múltiples nodos...")
    dynamic_scaling(SERVICE_NAMES_3_NODES)  # Simulamos 3 nodos

if __name__ == "__main__":
    main()
