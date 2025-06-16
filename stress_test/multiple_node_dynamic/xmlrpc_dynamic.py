import multiprocessing
import xmlrpc.client
import time
import statistics
import random
import string

# Total de mensajes a enviar
TOTAL_MESSAGES = 1600

# Intervalo de monitorización (en segundos)
MONITOR_INTERVAL_SECONDS = 2

# Lista de URLs de los servicios disponibles
AVAILABLE_SERVICE_URLS = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003"
]

# Generador de insultos aleatorios
def generate_random_insult(index):
    return f"You are a {''.join(random.choices(string.ascii_lowercase, k=8))}! #{index}"

# Generador de mensajes que llena la cola
def generate_messages(shared_queue, total_messages):
    for i in range(total_messages):
        shared_queue.append(generate_random_insult(i))
    print("[Generator] Finished sending all messages.")

# Worker que consume mensajes y hace llamadas a XML-RPC
def insult_worker(server_url, shared_queue, processing_times_list):
    try:
        proxy = xmlrpc.client.ServerProxy(server_url)
    except Exception as error:
        print(f"[{server_url}] ERROR creating proxy: {error}")
        return

    while True:
        try:
            message = shared_queue.pop(0)
        except IndexError:
            time.sleep(0.05)
            continue

        try:
            start = time.time()
            proxy.add_insult(message)
            end = time.time()
            processing_times_list.append(end - start)
        except Exception as error:
            print(f"[{server_url}] ERROR processing message: {error}")

# Coordinador que escala dinámicamente según la carga
def dynamic_scaling_controller():
    shared_queue = multiprocessing.Manager().list()
    processing_times_list = multiprocessing.Manager().list()
    active_processes = []
    urls_in_use = set()

    # Arranca el generador de mensajes
    start_time = time.time()
    generator_process = multiprocessing.Process(
        target=generate_messages,
        args=(shared_queue, TOTAL_MESSAGES)
    )
    generator_process.start()

    while generator_process.is_alive() or len(shared_queue) > 0:
        arrival_rate = len(shared_queue) / MONITOR_INTERVAL_SECONDS
        avg_processing_time = statistics.mean(processing_times_list) if processing_times_list else 0.02
        worker_capacity = 1 / avg_processing_time if avg_processing_time > 0 else 1
        required_workers = max(1, round(arrival_rate / worker_capacity))

        print(
            f"[Scaler] Messages in queue: {len(shared_queue)} | "
            f"Estimated arrival rate: {arrival_rate:.2f} msg/s | "
            f"Average processing time per message: {avg_processing_time:.4f} s | "
            f"Workers needed: {required_workers}"
        )

        if len(urls_in_use) < required_workers:
            available = [url for url in AVAILABLE_SERVICE_URLS if url not in urls_in_use]
            for server_url in available[:required_workers - len(urls_in_use)]:
                print(f"[Scaler] Launching worker for {server_url}")
                worker_process = multiprocessing.Process(
                    target=insult_worker,
                    args=(server_url, shared_queue, processing_times_list)
                )
                worker_process.start()
                active_processes.append(worker_process)
                urls_in_use.add(server_url)

        time.sleep(MONITOR_INTERVAL_SECONDS)

    while len(shared_queue) > 0:
        print(f"[Scaler] Remaining messages: {len(shared_queue)}")
        time.sleep(1)

    end_time = time.time()
    total_duration = end_time - start_time
    throughput = TOTAL_MESSAGES / total_duration

    print(f"\n[RESULT] Total time: {total_duration:.2f} s")
    print(f"[RESULT] Throughput: {throughput:.2f} req/s")

    for process in active_processes:
        process.terminate()
        process.join()

if __name__ == "__main__":
    print("XML-RPC MULTI-NODE DYNAMIC SCALING TEST")
    dynamic_scaling_controller()
