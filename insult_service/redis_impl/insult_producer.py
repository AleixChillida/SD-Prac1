import redis
import time
import random
import sys
from datetime import datetime

class InsultProducer:
    def __init__(self):
        # Configuración optimizada para WSL desde VS Code
        self.redis = redis.StrictRedis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            health_check_interval=30
        )
        self.queue_name = "insult_queue"
        self.insultos = [
            "Eres un bobalicón",
            "Vaya chapucero",
            "Pedazo de zopenco",
            "Más tonto que un ladrillo",
            "Tienes menos luces que un sótano"
        ]
        self._verify_connection()

    def _verify_connection(self):
        """Verifica la conexión a Redis con reintentos"""
        for _ in range(3):
            try:
                if self.redis.ping():
                    return
            except redis.ConnectionError:
                time.sleep(1)
        print(" No se pudo conectar a Redis. Verifica que el servidor está corriendo.")
        print("Ejecuta en WSL: sudo service redis-server start")
        sys.exit(1)

    def start_producing(self):
        """Envía insultos periódicamente"""
        print(" InsultProducer iniciado - Enviando insultos cada 5 segundos...")
        print("Presiona Ctrl+C para detener")
        
        try:
            while True:
                insulto = random.choice(self.insultos)
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                try:
                    self.redis.rpush(self.queue_name, insulto)
                    print(f"[{timestamp}]  Enviado: {insulto}")
                except redis.RedisError as e:
                    print(f"[{timestamp}]  Error enviando: {str(e)}")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n Producer detenido por el usuario")
            sys.exit(0)

if __name__ == "__main__":
    producer = InsultProducer()
    producer.start_producing()