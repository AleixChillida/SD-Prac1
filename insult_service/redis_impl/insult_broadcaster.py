# redis_insult_broadcaster.py
import redis
import time
import random
import sys
from datetime import datetime

class InsultBroadcaster:
    def __init__(self):
        self.redis = redis.StrictRedis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        self.insults_list = "INSULTS"
        self.channel = "insult_channel"
        self._verify_connection()

    def _verify_connection(self):
        """Verifica la conexión a Redis"""
        try:
            if not self.redis.ping():
                raise ConnectionError("Redis no respondió")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            print(f" Error conectando a Redis: {e}")
            sys.exit(1)

    def start_broadcasting(self):
        """Publica insultos aleatorios periódicamente"""
        print("InsultBroadcaster iniciado - Publicando cada 5 segundos...")
        print("Presiona Ctrl+C para detener")
        
        try:
            while True:
                # Obtener todos los insultos almacenados
                insults = self.redis.lrange(self.insults_list, 0, -1)
                
                if insults:
                    insult = random.choice(insults)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.redis.publish(self.channel, insult)
                    print(f"[{timestamp}] 📡 Publicado: {insult}")
                else:
                    print(" No hay insultos en la lista. Esperando...")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n Broadcaster detenido por el usuario")
            sys.exit(0)

if __name__ == "__main__":
    broadcaster = InsultBroadcaster()
    broadcaster.start_broadcasting()