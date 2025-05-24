# redis_impl/insult_consumer3.py
import redis
import sys
import time

class InsultConsumer:
    def __init__(self, queue_index):
        self.queue_name = f"insult_queue.{queue_index}"
        self.result_key = "filtered_texts"
        self.insults = set([
            "Eres un bobalicón",
            "Vaya chapucero",
            "Pedazo de zopenco",
            "Más tonto que un ladrillo",
            "Tienes menos luces que un sótano"
        ])
        self.redis = redis.StrictRedis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            health_check_interval=30
        )
        self._verify_connection()

    def _verify_connection(self):
        for _ in range(3):
            try:
                if self.redis.ping():
                    return
            except redis.ConnectionError:
                time.sleep(1)
        print(f"[{self.queue_name}] No se pudo conectar a Redis.")
        sys.exit(1)

    def filter(self, text):
        return "CENSORED" if text in self.insults else text

    def start_consuming(self):
        print(f"InsultConsumer escuchando en {self.queue_name}")
        try:
            while True:
                _, insult = self.redis.blpop(self.queue_name)
                filtered = self.filter(insult)
                self.redis.rpush(self.result_key, filtered)
                # Opcional: comentar esto si quieres rendimiento máximo
                # print(f"Procesado: {insult} -> {filtered}")
        except KeyboardInterrupt:
            print(f"\nConsumer {self.queue_name} detenido por el usuario.")
            sys.exit(0)

if __name__ == "__main__":
    queue_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    consumer = InsultConsumer(queue_index)
    consumer.start_consuming()
