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

# Declarar el exchange tipo 'fanout' (para que lo reciban todos los receivers)
channel.exchange_declare(exchange='insult_exchange', exchange_type='fanout')

print("Broadcaster started. Broadcasting insults every 5 seconds...")

try:
    while True:
        insult = random.choice(INSULTS)
        channel.basic_publish(exchange='insult_exchange', routing_key='', body=insult)
        print(f"Published: {insult}")
        time.sleep(5)  # Espera 5 segundos antes del siguiente mensaje
except KeyboardInterrupt:
    print("\nBroadcaster stopped.")
    connection.close()
