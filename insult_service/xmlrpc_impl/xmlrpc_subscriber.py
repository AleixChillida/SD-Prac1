import xmlrpc.server
import xmlrpc.client
import time
from threading import Thread

class Subscriber:
    def __init__(self, port):
        self.server = xmlrpc.server.SimpleXMLRPCServer(("localhost", port), allow_none=True)
        self.server.register_function(self.notify, "notify")
        self.received_insults = []
    
    def notify(self, insult):
        """Método que será llamado por el servidor"""
        print(f"Received new insult: {insult}")
        self.received_insults.append(insult)
        return True
    
    def start(self):
        """Inicia el servidor del subscriptor"""
        print(f"Subscriber running on port {self.server.server_address[1]}...")
        Thread(target=self.server.serve_forever, daemon=True).start()
    
    def subscribe_to(self, server_url):
        """Registra este subscriptor en el servidor"""
        server = xmlrpc.client.ServerProxy(server_url)
        callback_url = f"http://localhost:{self.server.server_address[1]}"
        if server.add_subscriber(callback_url):
            print(f"Successfully subscribed to {server_url}")
        else:
            print(f"Already subscribed to {server_url}")

if __name__ == "__main__":
    # Crear subscriptor en puerto 8001
    subscriber = Subscriber(8001)
    subscriber.start()
    
    # Suscribirse al servidor principal
    subscriber.subscribe_to("http://localhost:8000")
    
    # Mantener el programa en ejecución
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nReceived insults:", subscriber.received_insults)
        print("Subscriber stopped.")