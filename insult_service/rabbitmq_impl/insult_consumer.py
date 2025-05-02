import pika

# Conectar a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Asegurar que la cola existe
channel.queue_declare(queue='insult_queue')

def callback(ch, method, properties, body):
    insult = body.decode()
    print(f"Consumed and stored: {insult}")

# Escuchar la cola
channel.basic_consume(queue='insult_queue', on_message_callback=callback, auto_ack=True)

print("Waiting for insults. Press CTRL+C to exit.")
channel.start_consuming()
