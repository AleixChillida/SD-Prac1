import multiprocessing
import Pyro4
import time
import statistics


TOTAL_MESSAGES = 80000

# Intervalo de tiempo (en segundos) para comprobar el estado de la cola
MONITOR_INTERVAL_SECONDS = 1

AVAILABLE_SERVICE_NAMES = ["insult.service.1", "insult.service.2", "insult.service.3"]

# Genera mensajes y los coloca en la cola compartida
def generate_messages(shared_queue, total_messages):
    for i in range(total_messages):
        shared_queue.append(f"You are a fool #{i}!")
    print("Finished sending all messages.")

# Worker que procesa mensajes llamando al método remoto 'add_insult' del servicio Pyro
def insult_worker(service_name, shared_queue, processing_times_list):
    try:
        # Conectar al NameServer de Pyro
        name_server = Pyro4.locateNS(host="localhost", port=9090)
        service_uri = str(name_server.lookup(service_name))
        proxy = Pyro4.Proxy(service_uri)
    except Exception as error:
        print(f"[{service_name}] ERROR locating NameServer: {error}")
        return

    while True:
        try:
            # Obtener un mensaje de la cola compartida
            message = shared_queue.pop(0)
        except IndexError:
            # Si la cola está vacía, espera un poco y vuelve a intentar
            time.sleep(0.05)
            continue

        try:
            start = time.time()
            proxy.add_insult(message)
            end = time.time()
            processing_times_list.append(end - start)
        except Exception as error:
            print(f"[{service_name}] ERROR processing message: {error}")

# Coordinador que escala dinámicamente el número de workers según la carga
def dynamic_scaling_controller():
    # Cola de mensajes compartida entre procesos
    shared_queue = multiprocessing.Manager().list()
    # Lista para registrar los tiempos individuales de procesamiento
    processing_times_list = multiprocessing.Manager().list()
    # Lista de procesos activos y conjunto de nombres en uso
    active_processes = []
    services_in_use = set()

    # Lanzar el generador de mensajes
    start_time = time.time()
    generator_process = multiprocessing.Process(
        target=generate_messages,
        args=(shared_queue, TOTAL_MESSAGES)
    )
    generator_process.start()

    # Bucle de control dinámico hasta que se procesen todos los mensajes
    while generator_process.is_alive() or len(shared_queue) > 0:
        # Tasa de llegada estimada de mensajes
        arrival_rate = len(shared_queue) / MONITOR_INTERVAL_SECONDS

        # Tiempo medio de procesamiento por mensaje
        avg_processing_time = statistics.mean(processing_times_list) if processing_times_list else 0.02

        # Capacidad por worker: cuántos mensajes puede procesar por segundo
        worker_capacity = 1 / avg_processing_time if avg_processing_time > 0 else 1

        # Número estimado de workers necesarios
        required_workers = max(1, round(arrival_rate / worker_capacity))

        print(f"Messages in queue: {len(shared_queue)} | "f"Estimated arrival rate: {arrival_rate:.2f} msg/s | "f"Average processing time message: {avg_processing_time:.4f} s | "f"Workers needed: {required_workers}")


        # Escalar si faltan workers
        if len(services_in_use) < required_workers:
            available_services = [
                name for name in AVAILABLE_SERVICE_NAMES if name not in services_in_use
            ]
            for service_name in available_services[:required_workers - len(services_in_use)]:
                print(f"Launching worker for {service_name}")
                worker_process = multiprocessing.Process(
                    target=insult_worker,
                    args=(service_name, shared_queue, processing_times_list)
                )
                worker_process.start()
                active_processes.append(worker_process)
                services_in_use.add(service_name)

        time.sleep(MONITOR_INTERVAL_SECONDS)

    # Esperar hasta que la cola esté completamente vacía
    while len(shared_queue) > 0:
        print(f"Remaining messages: {len(shared_queue)}")
        time.sleep(1)

    # Medición final de rendimiento
    end_time = time.time()
    total_duration = end_time - start_time
    throughput = TOTAL_MESSAGES / total_duration

    print(f"\n[RESULT] Total time: {total_duration:.2f} s")
    print(f"[RESULT] Throughput: {throughput:.2f} req/s")

    # Finalizar procesos
    for process in active_processes:
        process.terminate()
        process.join()

if __name__ == "__main__":
    print("PYRO MULTI-NODE DYNAMIC SCALING TEST")
    dynamic_scaling_controller()
