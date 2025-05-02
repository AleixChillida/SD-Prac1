import pika
import random
import time

INSULTS = [
    "You are an idiot!", "You are a fool!", "You are stupid!",
    "You are a clown!", "You are a moron!"
]

# Conectar a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declarar la cola
channel.queue_declare(queue='insult_queue')

print("Insult Producer started. Generating insults every 5 seconds...")

try:
    while True:
        insult = random.choice(INSULTS)
        channel.basic_publish(exchange='', routing_key='insult_queue', body=insult)
        print(f"Produced: {insult}")
        time.sleep(5)  # Espera 5 segundos antes de producir el siguiente insulto
except KeyboardInterrupt:
    print("\nProducer stopped.")
    connection.close()
