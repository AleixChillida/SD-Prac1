import pika
import time
import random
from threading import Thread

class RabbitMQInsultFilterClient:
    def __init__(self, host='localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        
        # Declarar cola
        self.channel.queue_declare(queue='filter_tasks')
        
        # Frases de ejemplo
        self.phrases = [
            "The weather is nice today",
            "I enjoy programming",
            "Let's go to the park",
            "Have a nice day",
            "You are such an idiot",
            "What a fool you are!",
            "Only a moron would do that",
            "Don't be dumb"
        ]

    def _generate_text(self):
        """Genera un texto aleatorio"""
        return random.choice(self.phrases)

    def start_sending(self, interval=4):
        """Inicia el envío periódico de textos"""
        def sender():
            while True:
                text = self._generate_text()
                self.channel.basic_publish(
                    exchange='',
                    routing_key='filter_tasks',
                    body=text
                )
                print(f" Enviado: {text[:50]}")
                time.sleep(interval)

        Thread(target=sender, daemon=True).start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.connection.close()
            print("\nCliente detenido")

if __name__ == "__main__":
    print("Iniciando cliente RabbitMQ InsultFilter...")
    client = RabbitMQInsultFilterClient()
    client.start_sending()