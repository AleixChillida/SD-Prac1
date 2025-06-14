import multiprocessing
import Pyro4
import time
import statistics

# Configuración
NUM_MESSAGES = 80000
MONITOR_INTERVAL = 2  # segundos
ALL_SERVICE_NAMES = ["insult.service.1", "insult.service.2", "insult.service.3"]

# Generador de mensajes
def message_generator(queue, num_messages):
    for i in range(num_messages):
        queue.append(f"You are a fool #{i}!")
    print("[Generator] Finished sending all messages.")

# Worker Pyro que consume mensajes
def pyro_worker(service_name, queue, processed_times):
    try:
        ns = Pyro4.locateNS(host="localhost", port=9090)
        uri = str(ns.lookup(service_name))
        proxy = Pyro4.Proxy(uri)
    except Exception as e:
        print(f"[{service_name}] ERROR localizando el NameServer: {e}")
        return

    while True:
        try:
            message = queue.pop(0)  # .popleft no funciona con ListProxy
        except IndexError:
            time.sleep(0.05)
            continue

        try:
            t0 = time.time()
            proxy.add_insult(message)
            t1 = time.time()
            processed_times.append(t1 - t0)
        except Exception as e:
            print(f"[{service_name}] ERROR procesando mensaje: {e}")

# Coordinador que ajusta dinámicamente el número de workers
def dynamic_scaler():
    queue = multiprocessing.Manager().list()
    processed_times = multiprocessing.Manager().list()
    processes = []
    active_services = set()

    start_time = time.time()

    generator = multiprocessing.Process(target=message_generator, args=(queue, NUM_MESSAGES))
    generator.start()

    while generator.is_alive() or len(queue) > 0:
        # Cálculo de métricas
        λ = len(queue) / MONITOR_INTERVAL
        T = statistics.mean(processed_times) if processed_times else 0.02  # tiempo medio por mensaje
        C = 1 / T if T > 0 else 1
        N_required = max(1, round(λ / C))

        print(f"[Scaler] Queue: {len(queue)} | λ ≈ {λ:.2f} msg/s | T ≈ {T:.4f}s | N = {N_required}")

        # Escalar hacia arriba si es necesario
        if len(active_services) < N_required:
            available = [s for s in ALL_SERVICE_NAMES if s not in active_services]
            for service in available[:N_required - len(active_services)]:
                print(f"[Scaler] Launching worker for {service}")
                p = multiprocessing.Process(target=pyro_worker, args=(service, queue, processed_times))
                p.start()
                processes.append(p)
                active_services.add(service)

        time.sleep(MONITOR_INTERVAL)

    # Espera a que se vacíe la cola completamente
    while len(queue) > 0:
        print(f"[Scaler] Aún quedan {len(queue)} mensajes por procesar...")
        time.sleep(1)

    end_time = time.time()
    total_time = end_time - start_time
    throughput = NUM_MESSAGES / total_time

    print(f"\n[RESULT] Total time: {total_time:.2f} s")
    print(f"[RESULT] Throughput: {throughput:.2f} req/s")

    # Finalizar workers
    for p in processes:
        p.terminate()
        p.join()

if __name__ == "__main__":
    print("PYRO MULTI-NODE DYNAMIC SCALING TEST")
    dynamic_scaler()
