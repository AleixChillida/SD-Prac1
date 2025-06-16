import pika
import time
import random
import statistics
import multiprocessing

# Configuración
TOTAL_MESSAGES = 80000
MONITOR_INTERVAL_SECONDS = 2
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'insult_queue'

INSULTS = [
    "You are an idiot!", "You are a fool!", "You are stupid!",
    "You are a clown!", "You are a moron!"
]

# Inserta mensajes directamente en RabbitMQ
def generate_messages(total_messages):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_delete(queue=QUEUE_NAME)
    channel.queue_declare(queue=QUEUE_NAME)

    for i in range(total_messages):
        insult = f"{random.choice(INSULTS)} #{i}"
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=insult.encode())

    connection.close()
    print("Finished inserting all messages into RabbitMQ.")

# Worker que simula add_insult y mide el tiempo de procesamiento
def insult_worker(processing_times_list):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    stored_insults = set()

    def callback(ch, method, properties, body):
        t0 = time.time()
        insult = body.decode()
        if insult not in stored_insults:
            stored_insults.add(insult)
        time.sleep(0.002)  # Simula procesamiento
        t1 = time.time()
        processing_times_list.append(t1 - t0)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()

# Obtener el número actual de mensajes en la cola
def get_queue_message_count():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    queue = channel.queue_declare(queue=QUEUE_NAME, passive=True)
    count = queue.method.message_count
    connection.close()
    return count

# Coordinador que escala dinámicamente según la carga
def dynamic_scaling_controller():
    processing_times_list = multiprocessing.Manager().list()
    active_processes = []

    # Genera todos los mensajes antes de escalar
    start_time = time.time()
    generate_messages(TOTAL_MESSAGES)

    while get_queue_message_count() > 0:
        queue_length = get_queue_message_count()
        arrival_rate = queue_length / MONITOR_INTERVAL_SECONDS
        avg_processing_time = statistics.mean(processing_times_list) if processing_times_list else 0.002
        worker_capacity = 1 / avg_processing_time if avg_processing_time > 0 else 1
        required_workers = max(1, round(arrival_rate / worker_capacity))


        if len(active_processes) < required_workers:
            for _ in range(required_workers - len(active_processes)):
                p = multiprocessing.Process(target=insult_worker, args=(processing_times_list,))
                p.start()
                active_processes.append(p)

        time.sleep(MONITOR_INTERVAL_SECONDS)

    while get_queue_message_count() > 0:
        print(f"Remaining messages: {get_queue_message_count()}")
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
    print("RABBITMQ MULTI-NODE DYNAMIC SCALING TEST")
    dynamic_scaling_controller()
