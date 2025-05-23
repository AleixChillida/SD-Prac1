# consumer_redis.py
import redis
import time
from datetime import datetime

class InsultConsumer:
    def __init__(self):
        self.redis = redis.StrictRedis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            health_check_interval=30
        )
        self.queue_name = "insult_queue"
        self.result_key = "filtered_texts"
        self.insults = set([
            "Eres un bobalicón",
            "Vaya chapucero",
            "Pedazo de zopenco",
            "Más tonto que un ladrillo",
            "Tienes menos luces que un sótano"
        ])
        self._verify_connection()

    def _verify_connection(self):
        for _ in range(3):
            try:
                if self.redis.ping():
                    return
            except redis.ConnectionError:
                time.sleep(1)
        print(" No se pudo conectar a Redis. Verifica que el servidor está corriendo.")
        sys.exit(1)

    def filter(self, text):
        return "CENSORED" if text in self.insults else text

    def start_consuming(self):
        print(" InsultConsumer iniciado - Esperando mensajes...")
        try:
            while True:
                _, insult = self.redis.blpop(self.queue_name)
                filtered = self.filter(insult)
                self.redis.rpush(self.result_key, filtered)
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Procesado: {insult} -> {filtered}")
        except KeyboardInterrupt:
            print("\n Consumer detenido por el usuario")
            sys.exit(0)

if __name__ == "__main__":
    consumer = InsultConsumer()
    consumer.start_consuming()
