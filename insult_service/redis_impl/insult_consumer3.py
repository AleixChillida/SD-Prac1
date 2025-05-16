import redis
import sys
import threading
import time

class InsultConsumer:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.insults_list_name = "INSULTS"
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            socket_timeout=10,
            socket_keepalive=True
        )

    def start_consuming(self):
        print(f"InsultConsumer iniciado en cola '{self.queue_name}' - Esperando insultos...")
        try:
            while True:
                result = self.redis_client.blpop(self.queue_name, timeout=5)
                if not result:
                    continue
                _, insult = result
                print(f"[{self.queue_name}] Recibido: {insult}")
                # Aquí podrías añadir lógica para procesar o almacenar insultos
        except KeyboardInterrupt:
            print(f"\nConsumer de {self.queue_name} detenido por el usuario")

def consume_queue(queue_name):
    consumer = InsultConsumer(queue_name)
    consumer.start_consuming()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python redis_consumer.py <cola1> [<cola2> ... <colaN>]")
        sys.exit(1)

    queues = sys.argv[1:]
    threads = []
    for q in queues:
        t = threading.Thread(target=consume_queue, args=(q,), daemon=True)
        t.start()
        threads.append(t)

    print(f"Lanzados consumidores para las colas: {', '.join(queues)}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo todos los consumidores.")
