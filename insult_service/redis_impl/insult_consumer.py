import redis
import time
import sys
from typing import Optional

class InsultConsumer:
    def __init__(self):
        # Configuración de conexión para WSL desde VS Code
        self.redis_client = redis.StrictRedis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            socket_timeout=10,
            socket_keepalive=True
        )
        self.queue_name = "insult_queue"
        self.insults_list_name = "INSULTS"
        self._initialize_redis()

    def _initialize_redis(self):
        """Inicializa y verifica la conexión a Redis"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if not self.redis_client.ping():
                    raise ConnectionError("Redis no respondió a PING")
                
                # Asegurar que la clave es una lista
                if self.redis_client.exists(self.insults_list_name):
                    if self.redis_client.type(self.insults_list_name) != 'list':
                        print("Corrigiendo tipo de dato para INSULTS...")
                        self.redis_client.delete(self.insults_list_name)
                return
                
            except (redis.ConnectionError, redis.TimeoutError) as e:
                if attempt == max_retries - 1:
                    print(f"Error conectando a Redis: {e}")
                    print("Por favor ejecuta en WSL: sudo service redis-server start")
                    sys.exit(1)
                time.sleep(1)
                continue

    def _safe_lpos(self, insult: str) -> Optional[int]:
        """Implementación segura de LPOS para versiones antiguas de Redis"""
        try:
            # Para Redis >= 6.0.6
            return self.redis_client.lpos(self.insults_list_name, insult)
        except redis.ResponseError:
            # Fallback para versiones antiguas
            insults = self.redis_client.lrange(self.insults_list_name, 0, -1)
            try:
                return insults.index(insult)
            except ValueError:
                return None

    def start_consuming(self):
        """Procesa insultos de la cola"""
        print(" InsultConsumer iniciado - Esperando insultos...")
        try:
            while True:
                try:
                    # BLPOP con timeout para manejar interrupciones
                    result = self.redis_client.blpop(self.queue_name, timeout=5)
                    if not result:
                        continue
                        
                    _, insult = result
                    print(f" Recibido: {insult}")
                    
                    # Verificar si el insulto es nuevo
                    if self._safe_lpos(insult) is None:
                        self.redis_client.rpush(self.insults_list_name, insult)
                        print(f" Añadido nuevo insulto: {insult}")
                    else:
                        print(f"⏭ Duplicado ignorado: {insult}")
                        
                except (redis.RedisError, Exception) as e:
                    print(f" Error: {str(e)}")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n Consumer detenido por el usuario")
            sys.exit(0)

if __name__ == "__main__":
    print("Iniciando InsultConsumer...")
    consumer = InsultConsumer()
    consumer.start_consuming()