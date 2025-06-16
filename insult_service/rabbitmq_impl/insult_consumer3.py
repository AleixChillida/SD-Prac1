# consumer_worker.py

import pika

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'insult_queue'

def start_worker():
    # Conectar a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Asegurar que la cola existe
    channel.queue_declare(queue=QUEUE_NAME)

    # Importante: evitar que un nodo acapare todos los mensajes
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        insult = body.decode()
        # Procesamiento simulado
        # print(f"Consumed: {insult}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Escuchar la cola con ack manual
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[Consumer] Started and listening on '{QUEUE_NAME}'...")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
