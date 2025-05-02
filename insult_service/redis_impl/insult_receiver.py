# redis_insult_receiver.py
import redis
import sys

class InsultReceiver:
    def __init__(self, receiver_id):
        self.redis = redis.StrictRedis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        self.channel = "insult_channel"
        self.receiver_id = receiver_id
        self._verify_connection()

    def _verify_connection(self):
        """Verifica la conexión a Redis"""
        try:
            if not self.redis.ping():
                raise ConnectionError("Redis no respondió")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            print(f" Error conectando a Redis: {e}")
            sys.exit(1)

    def start_receiving(self):
        """Escucha el canal para recibir insultos"""
        pubsub = self.redis.pubsub()
        pubsub.subscribe(self.channel)
        
        print(f" Receiver {self.receiver_id} iniciado - Escuchando...")
        print("Presiona Ctrl+C para detener")
        
        try:
            for message in pubsub.listen():
                if message["type"] == "message":
                    print(f" Receiver {self.receiver_id} recibió: {message['data']}")
        except KeyboardInterrupt:
            print(f"\n Receiver {self.receiver_id} detenido")
            sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python redis_insult_receiver.py <ID_receiver>")
        sys.exit(1)
    
    receiver = InsultReceiver(sys.argv[1])
    receiver.start_receiving()