import pika

# Conectar a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declarar el exchange
channel.exchange_declare(exchange='insult_exchange', exchange_type='fanout')

# Crear una cola exclusiva por receptor
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Vincular la cola con el exchange
channel.queue_bind(exchange='insult_exchange', queue=queue_name)

def callback(ch, method, properties, body):
    insult = body.decode()
    print(f"Received: {insult}")

# Escuchar mensajes
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Waiting for insults. Press CTRL+C to exit.")
channel.start_consuming()
