import redis
import time
import random
from threading import Thread

class RedisInsultFilterClient:
    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(host=host, port=port)
        self.tasks_key = "insult_filter:tasks"
        
        # Frases de ejemplo que pueden contener insultos
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
                self.redis.rpush(self.tasks_key, text)
                print(f" Enviado: {text[:50]}")
                time.sleep(interval)

        Thread(target=sender, daemon=True).start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nCliente detenido")

if __name__ == "__main__":
    print("Iniciando cliente Redis InsultFilter...")
    client = RedisInsultFilterClient()
    client.start_sending()