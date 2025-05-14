import time
import Pyro4
from multiprocessing import Pool, current_process

NUM_REQUESTS = 1000
NUM_PROCESSES = 20

# Lista con los nombres de los servicios en el Name Server para los 3 nodos
SERVICE_NAMES = ["insult.service.1", "insult.service.2", "insult.service.3"]

def send_insult(i):
    insult = f"insult-{i}"
    proc_name = current_process().name

    # Elegir nodo usando round-robin según el índice i
    service_name = SERVICE_NAMES[i % len(SERVICE_NAMES)]

    try:
        ns = Pyro4.locateNS()
        uri = ns.lookup(service_name)
        proxy = Pyro4.Proxy(uri)
        proxy._pyroTimeout = 10  # Timeout para la llamada

        t0 = time.perf_counter()
        result = proxy.add_insult(insult)
        t1 = time.perf_counter()

        status = " añadido" if result else " ya existía"

    except Exception as e:
        print(f"[{proc_name}] Error enviando {insult} a {service_name}: {str(e)}")

if __name__ == "__main__":
    print(f"\n Iniciando stress test Pyro con {NUM_REQUESTS} peticiones y {NUM_PROCESSES} procesos en 3 nodos...\n")
    start = time.perf_counter()

    with Pool(NUM_PROCESSES) as pool:
        pool.map(send_insult, range(NUM_REQUESTS))

    duration = time.perf_counter() - start
    throughput = NUM_REQUESTS / duration

    print(f"\n Finalizado")
    print(f"[PyRO - Concurrente 3 nodos] Mensajes enviados: {NUM_REQUESTS}")
    print(f"[PyRO - Concurrente 3 nodos] Tiempo total: {duration:.2f}s")
    print(f"[PyRO - Concurrente 3 nodos] Throughput: {throughput:.2f} req/s\n")
