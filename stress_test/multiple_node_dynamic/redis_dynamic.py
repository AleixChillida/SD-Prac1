import multiprocessing
import redis
import time
import statistics
import random

# Configuración
TOTAL_MESSAGES = 80000
MONITOR_INTERVAL_SECONDS = 2
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_NAME = 'insult_queue'

INSULTS = [
    "Eres un bobalicón", "Vaya chapucero", "Pedazo de zopenco",
    "Más tonto que un ladrillo", "Tienes menos luces que un sótano"
]

# Inserta mensajes directamente en Redis
def generate_and_ingest_messages(total_messages):
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.delete(QUEUE_NAME)
    for i in range(total_messages):
        insult = f"{random.choice(INSULTS)} #{i}"
        r.rpush(QUEUE_NAME, insult)
    print(" Finished inserting all messages into Redis.")

# Worker que simula la función add_insult y procesamiento
def insult_worker(queue_name, processing_times_list):
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    stored_insults = set()

    while True:
        msg = r.lpop(queue_name)
        if msg is None:
            time.sleep(0.05)
            continue

        t0 = time.time()

        # Simula la función add_insult: almacenar si no está repetido
        if msg not in stored_insults:
            stored_insults.add(msg)

        time.sleep(0.002)  # Simula procesamiento de 2ms por mensaje

        t1 = time.time()
        processing_times_list.append(t1 - t0)

# Obtener longitud actual de la cola
def get_queue_length():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    return r.llen(QUEUE_NAME)

# Coordinador que escala workers según la carga
def dynamic_scaling_controller():
    processing_times_list = multiprocessing.Manager().list()
    active_processes = []

    # Inserta mensajes en Redis desde el proceso principal
    start_time = time.time()
    generate_and_ingest_messages(TOTAL_MESSAGES)

    while get_queue_length() > 0:
        queue_length = get_queue_length()
        arrival_rate = queue_length / MONITOR_INTERVAL_SECONDS
        avg_processing_time = statistics.mean(processing_times_list) if processing_times_list else 0.002
        worker_capacity = 1 / avg_processing_time if avg_processing_time > 0 else 1
        required_workers = max(1, round(arrival_rate / worker_capacity))

        if len(active_processes) < required_workers:
            new_workers = required_workers - len(active_processes)
            for _ in range(new_workers):
                p = multiprocessing.Process(
                    target=insult_worker,
                    args=(QUEUE_NAME, processing_times_list)
                )
                p.start()
                active_processes.append(p)

        time.sleep(MONITOR_INTERVAL_SECONDS)

    # Espera final hasta vaciar completamente la cola
    while get_queue_length() > 0:
        print(f"[Scaler] Remaining messages: {get_queue_length()}")
        time.sleep(1)

    end_time = time.time()
    total_duration = end_time - start_time
    throughput = TOTAL_MESSAGES / total_duration

    print(f"\n[RESULT] Total time: {total_duration:.2f} s")
    print(f"[RESULT] Throughput: {throughput:.2f} req/s")

    for p in active_processes:
        p.terminate()
        p.join()

if __name__ == "__main__":
    print("REDIS MULTI-NODE DYNAMIC SCALING TEST")
    dynamic_scaling_controller()
