import time
import Pyro4
from multiprocessing import Pool, current_process
import math

NUM_REQUESTS = 1000
MIN_PROCESSES = 2
MAX_PROCESSES = 20
BLOCK_SIZE = 100  # Número de peticiones por bloque
SERVICE_NAMES = ["insult.service.1", "insult.service.2", "insult.service.3"]

def send_insult(i):
    insult = f"insult-{i}"
    proc_name = current_process().name

    service_name = SERVICE_NAMES[i % len(SERVICE_NAMES)]

    try:
        ns = Pyro4.locateNS()
        uri = ns.lookup(service_name)
        proxy = Pyro4.Proxy(uri)
        proxy._pyroTimeout = 10

        t0 = time.perf_counter()
        result = proxy.add_insult(insult)
        t1 = time.perf_counter()

        return t1 - t0

    except Exception as e:
        print(f"[{proc_name}] Error enviando {insult} a {service_name}: {str(e)}")
        return 0

def dynamic_pool():
    total_requests = NUM_REQUESTS
    processed = 0
    num_procs = MIN_PROCESSES
    durations = []

    print(f"Iniciando escalado dinámico con {total_requests} solicitudes")

    while processed < total_requests:
        remaining = total_requests - processed
        current_block = min(BLOCK_SIZE, remaining)

        print(f"\nProcesando bloque: solicitudes {processed} a {processed + current_block - 1} con {num_procs} procesos")

        with Pool(processes=num_procs) as pool:
            block_durations = pool.map(send_insult, range(processed, processed + current_block))

        processed += current_block
        durations.extend(block_durations)

        # Calculamos tiempo medio del bloque
        avg_duration = sum(block_durations) / len(block_durations) if block_durations else 0.1
        capacity = 1 / avg_duration if avg_duration > 0 else 10

        # Estimamos tasa llegada de mensajes (simplificado)
        arrival_rate = current_block / avg_duration if avg_duration > 0 else 0

        # Calculamos workers necesarios (limitado)
        workers_needed = math.ceil((arrival_rate * avg_duration) / capacity)
        workers_needed = max(MIN_PROCESSES, min(MAX_PROCESSES, workers_needed))

        print(f"Bloque terminado. Duración media por petición: {avg_duration:.4f}s")
        print(f"Estimación workers necesarios para siguiente bloque: {workers_needed}")

        # Ajustamos número procesos para siguiente bloque
        num_procs = workers_needed

    total_time = sum(durations)
    throughput = total_requests / total_time if total_time > 0 else 0

    print(f"\nTest finalizado.")
    print(f"Total solicitudes: {total_requests}")
    print(f"Tiempo estimado total (suma tiempos individuales): {total_time:.2f}s")
    print(f"Throughput estimado: {throughput:.2f} req/s")

if __name__ == "__main__":
    print("Ejecutando pyro_test.py...")
    dynamic_pool() 
    print("Test terminado.")
