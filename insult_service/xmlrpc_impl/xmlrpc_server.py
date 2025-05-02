import xmlrpc.server
import xmlrpc.client
import random
import time
from threading import Thread

class InsultService:
    def __init__(self):
        self.insults = set()
        self.subscribers = set()  # Usamos set para evitar duplicados
        
    def add_insult(self, insult):
        """Agrega un insulto si no está repetido"""
        if insult not in self.insults:
            self.insults.add(insult)
            return True
        return False
    
    def get_insults(self):
        """Devuelve la lista de insultos"""
        return list(self.insults)
    
    def get_random_insult(self):
        """Retorna un insulto aleatorio"""
        if not self.insults:
            return ""
        return random.choice(list(self.insults))
    
    def add_subscriber(self, callback_url):
        """Añade un suscriptor para notificaciones"""
        if callback_url not in self.subscribers:
            self.subscribers.add(callback_url)
            return True
        return False
    
    def start_broadcasting(self, interval=5):
        """Inicia el broadcasting periódico de insultos"""
        def broadcast_loop():
            while True:
                if self.insults:
                    insult = self.get_random_insult()
                    self._notify_subscribers(insult)
                time.sleep(interval)
        
        Thread(target=broadcast_loop, daemon=True).start()
    
    def _notify_subscribers(self, insult):
        """Notifica a los suscriptores"""
        for url in list(self.subscribers):  # Usamos lista para evitar cambios durante iteración
            try:
                proxy = xmlrpc.client.ServerProxy(url)
                proxy.notify(insult)
            except Exception as e:
                print(f"Error notifying {url}: {str(e)}")
                self.subscribers.discard(url)

# Configuración del servidor
if __name__ == "__main__":
    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    service = InsultService()
    service.start_broadcasting(interval=5)  # Broadcast cada 5 segundos
    
    server.register_instance(service)
    print("XML-RPC InsultService running on port 8000...")
    print("Broadcasting insults every 5 seconds to subscribers...")
    server.serve_forever()

