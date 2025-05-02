import Pyro4
import time
import random
from threading import Thread, Lock

class InsultFilterClient:
    def __init__(self):
        self.lock = Lock()
        self.service = None
        self._connect_to_service()

    def _connect_to_service(self):
        """Establece conexión con el servicio PyRO"""
        max_retries = 3
        retry_delay = 2  # segundos
        
        for attempt in range(max_retries):
            try:
                with self.lock:
                    ns = Pyro4.locateNS()
                    uri = ns.lookup("insult.filter.service")
                    self.service = Pyro4.Proxy(uri)
                    print(" Conexión establecida con el servidor PyRO")
                    return
            except Pyro4.errors.NamingError:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        print(" No se pudo conectar al servidor después de varios intentos")
        exit(1)

    def _generate_text(self):
        """Genera textos aleatorios"""
        phrases = [
            "The weather is nice today",
            "I enjoy programming",
            "Let's go to the park",
            "Have a nice day",
            "You are such an idiot",
            "What a fool you are!",
            "Only a moron would do that",
            "Don't be dumb"
        ]
        return random.choice(phrases)

    def _safe_filter_text(self, text):
        """Envía texto de forma segura para filtrar"""
        with self.lock:
            try:
                return self.service.filter_text(text)
            except Pyro4.errors.CommunicationError:
                self._connect_to_service()
                return self.service.filter_text(text)

    def start_sending(self):
        """Inicia el envío periódico de textos"""
        def sender():
            while True:
                text = self._generate_text()
                try:
                    response = self._safe_filter_text(text)
                    print(f" Enviado: {text[:50]}")
                except Exception as e:
                    print(f" Error al enviar texto: {str(e)}")
                time.sleep(4)

        Thread(target=sender, daemon=True).start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n Cliente detenido")

if __name__ == "__main__":
    Pyro4.config.SERIALIZER = "serpent"
    Pyro4.config.SERVERTYPE = "multiplex"
    
    print(" Iniciando cliente PyRO InsultFilter...")
    client = InsultFilterClient()
    client.start_sending()