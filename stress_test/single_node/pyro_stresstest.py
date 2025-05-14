import time
import Pyro4
from multiprocessing import Pool, current_process

NUM_REQUESTS = 1000
NUM_PROCESSES = 20

def send_insult(i):
    insult = f"insult-{i}"
    proc_name = current_process().name
    try:
        ns = Pyro4.locateNS()
        uri = ns.lookup("insult.service")
        proxy = Pyro4.Proxy(uri)
        proxy._pyroTimeout = 10  # Tiempo máximo para cada llamada

        t0 = time.perf_counter()
        result = proxy.add_insult(insult)
        t1 = time.perf_counter()

        status = " añadido" if result else " ya existía"
        print(f"[{proc_name}] {insult} -> {status} ({t1 - t0:.3f}s)")

    except Exception as e:
        print(f"[{proc_name}]  Error enviando {insult}: {str(e)}")

if __name__ == "__main__":
    print(f"\n Iniciando stress test Pyro con {NUM_REQUESTS} peticiones y {NUM_PROCESSES} procesos...\n")
    start = time.perf_counter()

    with Pool(NUM_PROCESSES) as pool:
        pool.map(send_insult, range(NUM_REQUESTS))

    duration = time.perf_counter() - start
    throughput = NUM_REQUESTS / duration

    print(f"\n Finalizado")
    print(f"[PyRO - Concurrente] Mensajes enviados: {NUM_REQUESTS}")
    print(f"[PyRO - Concurrente] Tiempo total: {duration:.2f}s")
    print(f"[PyRO - Concurrente] Throughput: {throughput:.2f} req/s\n")
