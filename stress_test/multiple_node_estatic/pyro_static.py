import time
import multiprocessing
import Pyro4
from collections import Counter

# Parámetros del test de estrés
NUM_PROCESSES = 16
REQUESTS_PER_PROCESS = 5000

# Lista de servicios disponibles registrados en el NameServer
ALL_SERVICE_NAMES = [
    "insult.service.1",
    "insult.service.2",
    "insult.service.3"
]

# Función que ejecuta un proceso de test: envía múltiples mensajes a un servicio Pyro
def stress_test_process(proc_id, uri, return_dict):
    try:
        service = Pyro4.Proxy(uri)  # Conectarse al objeto remoto
        local_count = 0

        for i in range(REQUESTS_PER_PROCESS):
            insult = f"You are a fool #{proc_id}-{i}!"
            service.add_insult(insult)
            local_count += 1

        return_dict[proc_id] = (uri, local_count)  # Guardar resultados del proceso

    except Exception as e:
        print(f"[Process {proc_id}] ERROR: {e}")
        return_dict[proc_id] = (uri, 0)

# Ejecuta el test de estrés con un número determinado de nodos (1, 2 o 3)
def run_stress_test(num_nodes):
    print(f"\n--- Running stress test with {num_nodes} node(s) ---")

    # Localiza los URIs de los servicios que se usarán
    ns = Pyro4.locateNS()
    service_names = ALL_SERVICE_NAMES[:num_nodes]
    uris = [str(ns.lookup(name)) for name in service_names]

    start_time = time.time()

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []

    # Lanza los procesos distribuidos de forma round-robin entre los nodos disponibles
    for i in range(NUM_PROCESSES):
        uri = uris[i % len(uris)]  # Asignación round-robin
        p = multiprocessing.Process(target=stress_test_process, args=(i, uri, return_dict))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()  # Esperar a que todos los procesos terminen

    end_time = time.time()
    total_time = end_time - start_time
    total_requests = NUM_PROCESSES * REQUESTS_PER_PROCESS
    throughput = total_requests / total_time

    # Agrupar resultados por URI (nodo)
    usage = Counter()
    for _, (uri, count) in return_dict.items():
        usage[uri] += count

    print(f"\n[Result] Total requests: {total_requests}")
    print(f"[Result] Total time: {total_time:.2f} seconds")
    print(f"[Result] Throughput: {throughput:.2f} req/s")

    return total_time

# Función principal: ejecuta el test con 1, 2 y 3 nodos y calcula speedups
def main():
    print("PYRO MULTI-NODE STATIC STRESS TEST")

    times = {}
    for n in [1, 2, 3]:
        time_taken = run_stress_test(n)
        if time_taken:
            times[n] = time_taken
        else:
            print(f"[Error] Test failed for {n} nodes")
            return

    # Comparación de rendimiento entre configuraciones
    print("\n===== SPEEDUP ANALYSIS =====")
    t1 = times[1]
    for n in [2, 3]:
        speedup = t1 / times[n]
        print(f"[Speedup] {n} node(s): {speedup:.2f} (T1 = {t1:.2f}s, T{n} = {times[n]:.2f}s)")

if __name__ == "__main__":
    main()
