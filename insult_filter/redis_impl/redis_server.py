import redis
import threading
import time
from datetime import datetime

class RedisInsultFilterServer:
    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(host=host, port=port)
        self.insults_key = "insult_filter:insults"
        self.tasks_key = "insult_filter:tasks"
        self.results_key = "insult_filter:results"
        
        # Inicializar insultos básicos
        self._init_insults({"moron", "idiot", "fool", "stupid", "dumb", "loser"})
        
        # Limpiar colas previas (opcional, para desarrollo)
        self.redis.delete(self.tasks_key)
        self.redis.delete(self.results_key)
        
        # Iniciar workers
        self._start_workers(num_workers=3)
        self._print_banner()

    def _init_insults(self, insults):
        """Inicializa la lista de insultos en Redis"""
        self.redis.delete(self.insults_key)
        for insult in insults:
            self.redis.sadd(self.insults_key, insult.lower())

    def _print_banner(self):
        """Muestra información del servidor al iniciar"""
        print(f"Insultos registrados: {self.redis.smembers(self.insults_key)}")

    def _start_workers(self, num_workers):
        """Inicia los workers que procesarán las tareas"""
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._process_queue,
                daemon=True,
                name=f"RedisWorker-{i+1}"
            )
            worker.start()

    def _process_queue(self):
        """Procesa tareas de la cola Redis indefinidamente"""
        while True:
            # BLPop es bloqueante, espera hasta que haya una tarea
            _, text = self.redis.blpop(self.tasks_key)
            text = text.decode('utf-8')
            
            # Filtrar el texto
            filtered_text = self._filter_text(text)
            
            # Almacenar resultado
            self.redis.rpush(self.results_key, filtered_text)
            
            # Mostrar en terminal
            self._display_processing(text, filtered_text)

    def _display_processing(self, original, filtered):
        """Muestra el procesamiento en el terminal del servidor"""

        print(f" Entrada: {original}")
        print(f" Salida: {filtered}")

    def _filter_text(self, text):
        """Filtra insultos en el texto"""
        words = text.split()
        filtered_words = []
        
        for word in words:
            # Comprobar si la palabra (en minúsculas) está en los insultos
            if self.redis.sismember(self.insults_key, word.lower()):
                filtered_words.append("***CENSORED***")
            else:
                filtered_words.append(word)
        
        return " ".join(filtered_words)

    def add_insult(self, insult):
        """Añade un nuevo insulto al conjunto"""
        insult = insult.lower()
        added = self.redis.sadd(self.insults_key, insult)
        if added:
            print(f"\n NUEVO INSULTO REGISTRADO: {insult}")
        return bool(added)

    def get_filtered_results(self):
        """Obtiene todos los resultados filtrados"""
        return [res.decode('utf-8') for res in self.redis.lrange(self.results_key, 0, -1)]

    def get_insults(self):
        """Obtiene la lista de insultos"""
        return [insult.decode('utf-8') for insult in self.redis.smembers(self.insults_key)]

def main():
    print("\nIniciando servidor Redis InsultFilter...")
    server = RedisInsultFilterServer()
    
    try:
        # Mantener el servidor corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServidor deteniéndose...")

if __name__ == "__main__":
    main()